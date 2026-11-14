
from pathlib import Path
from app.llm import generate_response

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

PROMPT_A = BASE_DIR / "prompts" / "version_a.txt"
PROMPT_B = BASE_DIR / "prompts" / "version_b.txt"
OUTPUT = BASE_DIR / "eval" / "prompt_compare.md"

# Load prompts
prompt_a = PROMPT_A.read_text(encoding="utf-8")
prompt_b = PROMPT_B.read_text(encoding="utf-8")

# GadKille evaluation questions
questions = [
    "Tell me about Raigad Fort.",
    "Which district is Sinhagad Fort located in?",
    "What is the historical importance of Shivneri Fort?",
    "Where is Harishchandragad Fort located?",
    "Explain the trekking difficulty of Rajgad Fort.",
    "Which village is the base village for Torna Fort?",
    "What is the height of Pratapgad Fort?",
    "Recommend forts in Pune district.",
    "Which forts are suitable for beginner trekkers?",
    "What is the current population of Raigad Fort?"
]

report = []

report.append("# GadKille Prompt Comparison")
report.append("\n## Objective")
report.append(
    "Compare Basic Prompt (A) and Improved Prompt (B) "
    "using the same 10 questions."
)

report.append("\n## Evaluation Results")

for i, question in enumerate(questions, start=1):

    print(f"\nTesting question {i}/10: {question}")

    # Test Version A
    try:
        answer_a = generate_response(
            prompt=question,
            system_prompt=prompt_a
        )
    except Exception as e:
        answer_a = f"ERROR: {str(e)}"

    # Test Version B
    try:
        answer_b = generate_response(
            prompt=question,
            system_prompt=prompt_b
        )
    except Exception as e:
        answer_b = f"ERROR: {str(e)}"

    # Add results to report
    report.append(f"\n### Q{i}. {question}")

    report.append("\n**Version A – Basic Prompt**")
    report.append(f"\n{answer_a}")

    report.append("\n**Version B – Improved Prompt**")
    report.append(f"\n{answer_b}")

    report.append("\n**Evaluation:**")
    report.append("- Accuracy: To be evaluated")
    report.append("- Relevance: To be evaluated")
    report.append("- Hallucination control: To be evaluated")
    report.append("- Better version: To be decided")

    print("Completed.")

# Add conclusion section
report.append("\n## Evaluation Criteria")
report.append("""
| Criteria | What to check |
|---|---|
| Accuracy | Is the answer factually correct? |
| Relevance | Does it answer the question? |
| Completeness | Does it include useful information? |
| Hallucination | Does it invent missing facts? |
| Clarity | Is it easy to understand? |
""")

report.append("\n## Final Conclusion")
report.append(
    "Complete the manual evaluation of all 10 questions "
    "and identify the better prompt version."
)

# Save comparison report
OUTPUT.write_text("\n".join(report), encoding="utf-8")

print("\n--------------------------------")
print("Prompt comparison completed!")
print(f"Report saved at: {OUTPUT}")
print("--------------------------------")
