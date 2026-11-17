from langgraph.types import Command
from app.graph import build_graph


# Build the graph
graph = build_graph()

# Unique ID for this conversation
config = {
    "configurable": {
        "thread_id": "gadkille-test-1"
    }
}

# Initial user question
question = (
    "Find forts within 100 km of Kopargaon "
    "and tell me about Harishchandragad fort."
)
result = graph.invoke(
    {
        "question": question
    },
    config=config
)

print("\nFirst execution result:")
print(result)

# Check whether human approval is required
if "__interrupt__" in result:

    print("\nHuman approval required!")

    print(result["__interrupt__"])

    approval = input(
        "\nApprove distance search? (yes/no): "
    ).strip().lower()

    # Resume graph execution
    result = graph.invoke(
        Command(
            resume=(approval == "yes")
        ),
        config=config
    )

print("\nFinal result:")
print(result.get("final_response"))