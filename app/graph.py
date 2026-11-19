import json
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from app.llm import generate_response
from app.rag import RAGPipeline
from app.tools import forts_within_km


class GraphState(TypedDict, total=False):

    # User input
    question: str

    # LLM decision
    action: str
    town: str
    radius_km: float
    rag_question: str

    # Tool results
    rag_result: dict
    distance_results: list

    # Human approval
    approved: bool

    # Final output
    final_response: dict



def decision_node(state: GraphState):

    question = state["question"]

    prompt = f"""
You are an intelligent assistant for Maharashtra forts.

Available actions:

1. rag_search
   For fort history, height, trekking information and facts.

2. forts_within_km
   For finding forts within a distance of a town.

3. both
   When both tools are needed.

4. none
   When neither tool is required.

Return ONLY valid JSON:

{{
    "action": "rag_search, forts_within_km, both, or none",
    "town": "town name or empty string",
    "radius_km": 100,
    "rag_question": "question for RAG"
}}

User question: {question}
"""

    response = generate_response(prompt)

    response = response.strip()

    if response.startswith("```"):
        response = response.split("\n", 1)[1]
        response = response.rsplit("```", 1)[0].strip()

    decision = json.loads(response)

    print("\nDecision Node Executed")
    print("Selected action:", decision["action"])

    return {
        "action": decision["action"],
        "town": decision.get("town", ""),
        "radius_km": float(decision.get("radius_km") or 100),
        "rag_question": decision.get("rag_question") or question
    }

def rag_node(state: GraphState):

    print("\nRAG Node Executed")

    rag = RAGPipeline()

    result = rag.answer(
        state["rag_question"]
    )

    return {
        "rag_result": result
    }

def distance_node(state: GraphState):

    print("\nDistance Node Executed")

    results = forts_within_km(
        town=state["town"],
        radius_km=state["radius_km"]
    )

    return {
        "distance_results": results
    }

def approval_node(state: GraphState):

    print("\nApproval Node Executed")

    approval = interrupt({
        "message": "Approval required before searching nearby forts.",
        "town": state["town"],
        "radius_km": state["radius_km"],
        "action": "forts_within_km"
    })

    return {
        "approved": approval
    }

def route_after_decision(state: GraphState):
    action = state["action"]

    if action == "rag_search":
        return "rag"

    elif action == "forts_within_km":
        return "approval"

    elif action == "both":
        return "rag"

    else:
        return "final"


def route_after_rag(state: GraphState):
    if state["action"] == "both":
        return "approval"

    return "final"


def route_after_approval(state: GraphState):
    if state.get("approved") is True:
        return "distance"

    return "final"

def final_node(state: GraphState):

    print("\nFinal Node Executed")

    return {
        "final_response": {
            "question": state["question"],
            "action": state["action"],
            "rag_result": state.get("rag_result"),
            "distance_results": state.get("distance_results", []),
            "approved": state.get("approved")
        }
    }


def build_graph():

    builder = StateGraph(GraphState)

    # Register nodes
    builder.add_node("decision", decision_node)
    builder.add_node("rag", rag_node)
    builder.add_node("approval", approval_node)
    builder.add_node("distance", distance_node)
    builder.add_node("final", final_node)

    # Starting point
    builder.add_edge(START, "decision")

    # Decision routing
    builder.add_conditional_edges(
        "decision",
        route_after_decision,
        {
            "rag": "rag",
            "approval": "approval",
            "final": "final"
        }
    )

    # RAG routing
    builder.add_conditional_edges(
        "rag",
        route_after_rag,
        {
            "approval": "approval",
            "final": "final"
        }
    )

    # Approval routing
    builder.add_conditional_edges(
        "approval",
        route_after_approval,
        {
            "distance": "distance",
            "final": "final"
        }
    )

    # Remaining edges
    builder.add_edge("distance", "final")
    builder.add_edge("final", END)

    # Add memory checkpointing
    memory = InMemorySaver()

    return builder.compile(checkpointer=memory)
