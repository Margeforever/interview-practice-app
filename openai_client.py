"""
OpenAI client wrapper (keeps API logic modular and testable).
"""
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
logging.basicConfig(level=logging.INFO)

def call_openai(
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    top_p: float,
    frequency_penalty: float,
    presence_penalty: float,
    force_json: bool = False,
) -> str:
    api_key = api_key or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing.")

    client = OpenAI(api_key=api_key)

    kwargs = {}
    if force_json:
        kwargs["response_format"] = {"type": "json_object"}
        temperature = 0.0  # deterministic for JSON

    logging.info(f"[OpenAI] model={model} force_json={force_json} kwargs={kwargs}")

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        **kwargs,
    )

    return completion.choices[0].message.content or ""

# ==============================================
# OpenAI client wrapper
# - Single function to call chat.completions
# - Optional JSON enforcement via response_format
# ==============================================
