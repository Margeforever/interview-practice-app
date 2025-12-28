"""
OpenAI client wrapper.

Provides a single, centralized function to call the OpenAI LLM API.
Encapsulates all OpenAI-specific request details, including model selection,
system and user prompts, generation parameters, and optional JSON-only
response enforcement.

This abstraction decouples application logic from the OpenAI SDK and allows
the rest of the app to remain provider-agnostic.
"""

from openai import OpenAI


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
    """Call OpenAI chat completions and return the assistant content.

    Args:
        api_key: OpenAI API key.
        model: Model name.
        system_prompt: System message to prime behavior.
        user_prompt: User prompt content.
        temperature: Sampling temperature.
        max_tokens: Response token cap.
        top_p: Nucleus sampling parameter.
        frequency_penalty: Frequency penalty.
        presence_penalty: Presence penalty.
        force_json: If True, request JSON output format.

    Returns:
        Assistant message content as a string.
    """
    client = OpenAI(api_key=api_key)

    kwargs = {}
    if force_json:
        # Requires a model that supports JSON mode (e.g., gpt-4o, gpt-4o-mini).
        kwargs["response_format"] = {"type": "json_object"}

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
    return completion.choices[0].message.content
