
import json
import os
import re
from pathlib import Path

from app.llm import generate_response
from app.semantic_search import SemanticSearch


class RAGPipeline:

    def __init__(
        self,
        top_k=3,
        similarity_threshold=None,
        search_engine=None
    ):
        self.search_engine = search_engine or SemanticSearch()
        self.top_k = top_k

        self.similarity_threshold = (
            similarity_threshold
            if similarity_threshold is not None
            else float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.30"))
        )

        # Load system prompt
        base_dir = Path(__file__).resolve().parent.parent
        prompt_path = base_dir / "app" / "prompts" / "system.txt"

        self.system_prompt = prompt_path.read_text(
            encoding="utf-8"
        )

    def answer(self, question):

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        # Step 1: Retrieve relevant chunks
        results = self.search_engine.search(
            question,
            top_k=self.top_k
        )

        # Step 2: Filter irrelevant chunks
        relevant_results = [
            result for result in results
            if result.get("score", 0) >= self.similarity_threshold
        ]

        # Step 3: Handle missing information
        if not relevant_results:

            return {
                "answer": "I don't know",
                "confidence": "low",
                "follow_up": "Would you like to ask about another Maharashtra fort?",
                "sources": []
            }

        # Step 4: Build context and citations
        context_parts = []
        source_map = {}

        for index, result in enumerate(
            relevant_results, start=1
        ):

            metadata = result.get("metadata", {})

            title = metadata.get(
                "title", "Unknown Fort"
            )

            source = metadata.get(
                "source", "Unknown"
            )
            if source != "Unknown":
                source_map[index] = source

            text = result.get("text", "")

            context_parts.append(
                f"""
                [Source {index}]
                Fort: {title}
                URL: {source}
                Information: {text}
                """
            )



        context = "\n".join(context_parts)

        # Step 5: Construct RAG prompt
        rag_prompt = f"""
You are answering a question about Maharashtra forts.

Use ONLY the retrieved context below.

RETRIEVED CONTEXT:
{context}

USER QUESTION:
{question}

STRICT RULES:
1. Answer only using information in the retrieved context.
2. Never invent facts or assume missing information.
3. If the context does not contain enough information,
   return exactly "I don't know" as the answer.
4. If the context contains only a fort name and district,
   do not invent its height, history or trekking details.
5. Add inline citations such as [Source 1] wherever applicable.
6. Do not cite information that is not present in the context.
7. Set confidence to medium or low when the context
   only provides a fort name and district.
8. Include only citations that directly support your answer.
Return valid JSON with exactly these fields:
{{
    "answer": "Your answer with citations",
    "confidence": "high, medium, or low",
    "follow_up": "A relevant follow-up question"
}}

Do not include Markdown code fences.
Do not include additional text outside JSON.
"""

        # Step 6: Generate response
        response = generate_response(
            prompt=rag_prompt,
            system_prompt=self.system_prompt
        )

        # Step 7: Parse LLM JSON
        try:

            response = response.strip()

            # Handle accidental Markdown code fences
            if response.startswith("```"):
                response = response.split("\n", 1)[1]
                response = response.rsplit("```", 1)[0].strip()

            parsed = json.loads(response)

            answer = parsed.get("answer", "").strip()

            if not answer:
                raise ValueError("Empty answer from LLM.")

            # Normalize unsupported answers
            unknown_phrases = [
                "i don't know",
                "i do not know",
                "information is unavailable",
                "information is not available",
                "not available in the context",
                "not provided in the context"
            ]

            if any(
                phrase in answer.lower()
                for phrase in unknown_phrases
            ):

                answer = "I don't know"

            return {
    "answer": answer,
    "confidence": parsed.get(
        "confidence", "low"
    ),
    "follow_up": parsed.get(
        "follow_up", ""
    ),
    "sources": (
        [
            source_map[index]
            for index in sorted(
                set(
                    int(number)
                    for number in re.findall(
                        r"\[Source (\d+)\]", answer
                    )
                )
            )
            if index in source_map
        ]
        if answer != "I don't know"
        else []
    )
}

        except (json.JSONDecodeError, TypeError, AttributeError):
            raise ValueError(
                "LLM returned an invalid JSON response."
            )
