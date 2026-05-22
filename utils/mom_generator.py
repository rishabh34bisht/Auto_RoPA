# utils/mom_generator.py
from openai import OpenAI
from prompts.prompts import MOM_SYSTEM_PROMPT
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_mom(client: OpenAI, transcript: str) -> tuple[str, dict]:
    """Generates Minutes of Meeting from transcript."""
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.1,
        messages=[
            {"role": "system", "content": MOM_SYSTEM_PROMPT},
            {"role": "user", "content": f"Transcript:\n{transcript}"}
        ]
    )
    
    content = response.choices[0].message.content
    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }
    return content, usage
