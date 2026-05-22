# utils/ropa_generator.py
import json
from openai import OpenAI
from prompts.prompts import ROPA_SYSTEM_PROMPT

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
def generate_ropa(client: OpenAI, transcript: str, mode: str, manual_config: dict = None) -> tuple[list, dict]:
    """Generates RoPA data in JSON format."""
    
    user_prompt = f"Transcript:\n{transcript}\n\n"
    
    if mode == "User Input" and manual_config:
        user_prompt += f"REQUIREMENT: Extract exactly {manual_config['num_activities']} activities.\n"
        user_prompt += f"Use these specific activity titles: {', '.join(manual_config['titles'])}.\n"
    else:
        user_prompt += "REQUIREMENT: Automatically detect and extract all distinct processing activities discussed.\n"

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": ROPA_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }
    
    try:
        data = json.loads(response.choices[0].message.content)
        return data.get("ropa_records", []), usage
    except json.JSONDecodeError:
        raise Exception("Failed to parse JSON from OpenAI response.")
