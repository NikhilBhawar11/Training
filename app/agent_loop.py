import json

from app.llm import generate_response
from app.rag import RAGPipeline
from app.tools import forts_within_km


class GadKilleAgent:

    def __init__(self):

        self.rag = RAGPipeline()

        self.tools = {
            "rag_search": self.rag.answer,
            "forts_within_km": forts_within_km
        }

    def decide_action(self, question):

        prompt = f"""
You are an agent for GadKille, a Maharashtra forts assistant.

Choose which tools are needed to answer the user.

Available tools:

1. rag_search
   Use for fort history, facts, height, and trekking information.

2. forts_within_km
   Use for finding forts near a town within a distance.

3. both
   Use when the question requires both types of information.

4. none
   Use when neither tool is required.

Return ONLY valid JSON:

{{
    "action": "rag_search, forts_within_km, both, or none",
    "town": "town name or empty string",
    "radius_km": 100,
    "question": "question for RAG"
}}

User question: {question}
"""

        response = generate_response(prompt)

        response = response.strip()

        if response.startswith("```"):
            response = response.split("\n", 1)[1]
            response = response.rsplit("```", 1)[0].strip()

        return json.loads(response)

    def run(self, question):

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        decision = self.decide_action(question)

        action = decision.get("action")

        results = {}

        # Tool 1: RAG search
        if action in ["rag_search", "both"]:

            rag_question = decision.get("question") or question

            results["rag_search"] = self.tools["rag_search"](
                rag_question
            )

        # Tool 2: Distance search
        if action in ["forts_within_km", "both"]:

            town = decision.get("town")
            radius = decision.get("radius_km")

            if not town or radius is None:
                raise ValueError("Town and radius are required.")

            results["forts_within_km"] = self.tools[
                "forts_within_km"
            ](
                town=town,
                radius_km=float(radius)
            )

        if action == "none":
            return {
                "question": question,
                "message": "I can help with Maharashtra forts."
            }

        if action not in ["rag_search", "forts_within_km", "both"]:
            raise ValueError("Invalid agent action.")

        return {
            "question": question,
            "action": action,
            "results": results
        }


if __name__ == "__main__":

    agent = GadKilleAgent()

    question = input("Ask GadKille: ")

    response = agent.run(question)

    print(json.dumps(response, indent=4, ensure_ascii=False))
