
import os
from dotenv import load_dotenv
from groq import Groq
from google import genai

load_dotenv()


def generate_response(prompt, system_prompt=""):

    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "groq":

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is missing from .env")

        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    elif provider == "gemini":

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing from .env")

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
            System Instructions:
            {system_prompt}

            User Question:
            {prompt}
            """
        )

        return response.text

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
