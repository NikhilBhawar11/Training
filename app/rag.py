
import json
from pathlib import Path

from app.semantic_search import SemanticSearch
from app.llm import generate_response


class RAGPipeline:

    def __init__(self, top_k=3):
        self.search_engine = SemanticSearch()
        self.top_k = top_k

        # Load system prompt
        base_dir = Path(__file__).resolve().parent.parent
        prompt_path = base_dir / "app" / "prompts" / "system.txt"

        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def answer(self, question):

        # Step 1: Retrieve relevant documents
        results = self.search_engine.search(
            question,
            top_k=self.top_k
        )

        # Step 2: Build context from retrieved documents
        context_parts = []

        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata", {})

            context_parts.append(
                f"""
                Document {index}
                Fort: {metadata.get('title', 'Unknown')}
                Source: {metadata.get('source', 'Unknown')}
                Similarity Score: {result.get('score', 0):.4f}
                Information:
                {result.get('text', '')}
                """
            )

        context = "\n".join(context_parts)

        if not context:
            context = "No relevant information was found."

        # Step 3: Construct RAG prompt
        rag_prompt = f"""
        Retrieved Context:
        {context}

        User Question:
        {question}

        Answer the question using the retrieved context.

        Rules:
        - Do not invent facts.
        - If the context does not contain the answer, say information is unavailable.
        - Do not treat similarity scores as factual confidence.
        - Include relevant source URLs in the answer when available.
        """

        # Step 4: Generate LLM response
        response = generate_response(
            prompt=rag_prompt,
            system_prompt=self.system_prompt
        )

        # Step 5: Validate JSON response
        try:
            parsed_response = json.loads(response)

            return {
                "answer": parsed_response["answer"],
                "confidence": parsed_response["confidence"],
                "follow_up": parsed_response["follow_up"],
                "sources": list(dict.fromkeys(
                    result.get("metadata", {}).get("source")
                    for result in results
                    if result.get("metadata", {}).get("source")
                    and question.lower().replace("tell me about", "").strip()
                    .replace(".", "") in
                    result.get("metadata", {}).get("title", "").lower()
                    ))
            }

        except (json.JSONDecodeError, KeyError, TypeError):
            raise ValueError("LLM returned an invalid JSON response.")
