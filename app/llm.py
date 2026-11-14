
import os
from dotenv import load_dotenv
from groq import Groq
from google import genai

load_dotenv()


def generate_response(prompt, system_prompt=""):
    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "groq":
        client = Groq(
            api_key=os.getenv("Groq api key")
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    elif provider == "gemini":
        client = genai.Client(
            api_key=os.getenv("Gemini api key ")
        )

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
