# """Chat controller.
#
# Responsibilities:
# - Manage session state.
# - Build prompts and call the model.
# - Initialize chat context and handle user turns.
# """

from typing import Optional, Tuple

import streamlit as st

from config import get_openai_api_key
from extraction import extract_text
from openai_client import call_openai
from prompts_formats import (
    FORMAT_JSON_A,
    FORMAT_JSON_B,
    build_perspective_text,
    build_user_prompt,
)
from security import MAX_CHARS, matches_blocklist


# -----------------------------
# Session state helpers
# -----------------------------
def ensure_session_state() -> None:
    """Ensure required keys exist in Streamlit session_state."""
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("cv_text", "")
    st.session_state.setdefault("jd_text", "")
    st.session_state.setdefault("perspective_mode", "candidate")
    st.session_state.setdefault("initialized", False)
    # Lock output format per chat session
    st.session_state.setdefault("output_format", "Text")


def reset_state() -> None:
    """Reset the chat-related session_state to defaults."""
    st.session_state.messages = []
    st.session_state.cv_text = ""
    st.session_state.jd_text = ""
    st.session_state.perspective_mode = "candidate"
    st.session_state.initialized = False
    # Reset locked output format
    st.session_state.output_format = "Text"


# -----------------------------
# Output format instructions
# -----------------------------
def _format_instruction(output_format: str) -> str:
    """Return format instruction block based on chosen output format."""
    if output_format == "JSON_A":
        return FORMAT_JSON_A
    if output_format == "JSON_B":
        return FORMAT_JSON_B
    return "Return normal text (not JSON)."


def _effective_system_prompt(system_prompt: str, output_format: str) -> str:
    """Augment the system prompt when JSON is requested.

    If the output format is JSON, enforce strict JSON-only responses.
    """
    if output_format.startswith("JSON"):
        return (
            system_prompt
            + "\n\nIMPORTANT OUTPUT RULE:\n"
            + "If the user requested JSON, you MUST output ONLY valid JSON.\n"
            + "Do not output markdown, headings, backticks, code fences, "
            + "or extra text.\n"
            + "If a value is unknown, use an empty string or empty list.\n"
        )
    return system_prompt


# -----------------------------
# Model call
# -----------------------------
def _call_model(
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
    """Call the OpenAI API wrapper.

    Args:
        model: Model name.
        system_prompt: System message to prime the assistant.
        user_prompt: User prompt content.
        temperature: Sampling temperature.
        max_tokens: Response token cap.
        top_p: Nucleus sampling parameter.
        frequency_penalty: Frequency penalty.
        presence_penalty: Presence penalty.
        force_json: If True, request JSON output format.

    Returns:
        Assistant text response.
    """
    api_key = get_openai_api_key()
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY missing. Set it in .env or Streamlit secrets."
        )

    return call_openai(
        api_key=api_key,
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        force_json=force_json,
    )


# -----------------------------
# Initialize chat
# -----------------------------
def initialize_chat(
    cv_file,
    jd_file,
    is_interviewer: bool,
    output_format: str,
    model: str,
    system_prompt: str,
    temperature: float,
    max_tokens: int,
    top_p: float,
    frequency_penalty: float,
    presence_penalty: float,
) -> Tuple[bool, Optional[str]]:
    """Initialize chat: extract files, seed first assistant message.

    Args:
        cv_file: Uploaded CV file.
        jd_file: Uploaded JD file.
        is_interviewer: Perspective flag (True for interviewer mode).
        output_format: "Text" | "JSON_A" | "JSON_B".
        model: Model name to use.
        system_prompt: Global system prompt to apply.
        temperature: Sampling temperature.
        max_tokens: Response token cap.
        top_p: Nucleus sampling parameter.
        frequency_penalty: Frequency penalty.
        presence_penalty: Presence penalty.

    Returns:
        Tuple of (ok, error_message). If ok is False, error_message is set.
    """
    if not cv_file or not jd_file:
        return False, "Please upload both CV and Job Description."

    cv_text = extract_text(cv_file)
    jd_text = extract_text(jd_file)

    if len(cv_text) < 20 or len(jd_text) < 20:
        return False, (
            "Could not extract enough text from one of the files. "
            "Try a different format."
        )
    if matches_blocklist(cv_text) or matches_blocklist(jd_text):
        return False, "Blocked content detected (potential prompt-injection)."

    st.session_state.cv_text = cv_text[:MAX_CHARS]
    st.session_state.jd_text = jd_text[:MAX_CHARS]
    st.session_state.perspective_mode = (
        "interviewer" if is_interviewer else "candidate"
    )
    st.session_state.messages = []
    st.session_state.initialized = True

    # Lock the chosen output format for this chat session
    st.session_state.output_format = output_format

    fmt_instr = _format_instruction(output_format)
    perspective_text = build_perspective_text(is_interviewer=is_interviewer)
    effective_system = _effective_system_prompt(system_prompt, output_format)

    effective_temperature = 0.0 if output_format.startswith("JSON") else temperature

    if output_format == "JSON_A":
        json_a_task = (
            "Task:\n"
            "1) Summarize the CV in up to 150 words.\n"
            "2) Summarize the Job Description in up to 150 words.\n"
            "3) List top 5 matches and top 5 gaps.\n"
            "Do NOT add any other sections.\n\n"
            "=== CV ===\n"
            f"{st.session_state.cv_text}\n\n"
            "=== JOB DESCRIPTION ===\n"
            f"{st.session_state.jd_text}\n"
        )
        starter_prompt = f"{fmt_instr}\n\n{json_a_task}"

    elif output_format == "JSON_B":
        json_b_task = (
            "Task:\n"
            "Generate 10 tailored interview questions (mix behavioral + "
            "technical) based on CV and JD.\n"
            "Provide model answers.\n"
            "Do NOT output CV/JD summaries.\n\n"
            "=== CV ===\n"
            f"{st.session_state.cv_text}\n\n"
            "=== JOB DESCRIPTION ===\n"
            f"{st.session_state.jd_text}\n"
        )
        starter_prompt = (
            f"{fmt_instr}\n\n{json_b_task}\n\nPerspective: {perspective_text}"
        )

    else:
        step4 = (
            "4) Generate 10 tailored interview questions (behavioral + "
            "technical) and provide answers."
        )
        base_prompt = build_user_prompt(
            cv_text=st.session_state.cv_text,
            jd_text=st.session_state.jd_text,
            step4=step4,
            perspective_text=perspective_text,
            max_chars=MAX_CHARS,
        )
        starter_prompt = f"{fmt_instr}\n\n{base_prompt}"

    resp = _call_model(
        model=model,
        system_prompt=effective_system,
        user_prompt=starter_prompt,
        temperature=effective_temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        force_json=output_format.startswith("JSON"),
    )

    st.session_state.messages.append({"role": "assistant", "content": resp})
    return True, None


# -----------------------------
# Chat turn
# -----------------------------
def chat_turn(
    user_input: str,
    output_format: str,
    model: str,
    system_prompt: str,
    temperature: float,
    max_tokens: int,
    top_p: float,
    frequency_penalty: float,
    presence_penalty: float,
) -> str:
    """Single chat turn: append user input and get assistant response.

    Args:
        user_input: New user message to process.
        output_format: "Text" | "JSON_A" | "JSON_B".
        model: Model name to use.
        system_prompt: Global system prompt to apply.
        temperature: Sampling temperature.
        max_tokens: Response token cap.
        top_p: Nucleus sampling parameter.
        frequency_penalty: Frequency penalty.
        presence_penalty: Presence penalty.

    Returns:
        Assistant text response.
    """
    if matches_blocklist(user_input):
        raise RuntimeError(
            "Blocked content detected (potential prompt-injection)."
        )

    st.session_state.messages.append({"role": "user", "content": user_input})

    fmt_instr = _format_instruction(output_format)
    is_interviewer = st.session_state.perspective_mode == "interviewer"
    perspective_text = build_perspective_text(is_interviewer=is_interviewer)

    # Compact history (last 8 messages)
    history = st.session_state.messages[-8:]
    history_block = "\n".join(
        [f'{m["role"].upper()}: {m["content"]}' for m in history]
    )

    base = build_user_prompt(
        cv_text=st.session_state.cv_text,
        jd_text=st.session_state.jd_text,
        step4=(
            "4) Continue the interview practice based on the new user "
            "message."
        ),
        perspective_text=perspective_text,
        max_chars=MAX_CHARS,
    )

    prompt = (
        f"{fmt_instr}\n\n"
        f"{base}\n\n"
        "=== CHAT HISTORY (most recent) ===\n"
        f"{history_block}\n\n"
        "=== NEW USER MESSAGE ===\n"
        f"{user_input}\n"
    )

    assistant = _call_model(
        model=model,
        system_prompt=system_prompt,
        user_prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        force_json=output_format.startswith("JSON"),
    )

    st.session_state.messages.append({"role": "assistant", "content": assistant})
    return assistant

