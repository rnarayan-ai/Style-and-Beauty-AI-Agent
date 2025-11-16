import os
from groq import Groq

groq_client = Groq(api_key="")

def run_groq_query(prompt: str) -> str:
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # or other available model
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
