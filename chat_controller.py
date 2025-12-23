# chat_controller.py
import streamlit as st
from typing import Tuple, Optional

from extraction import extract_text
from security import MAX_CHARS, matches_blocklist
from config import get_openai_api_key
from openai_client import call_openai
from prompts_formats import build_perspective_text, build_user_prompt, FORMAT_JSON_A, FORMAT_JSON_B


def ensure_session_state():
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("cv_text", "")
    st.session_state.setdefault("jd_text", "")
    st.session_state.setdefault("perspective_mode", "candidate")
    st.session_state.setdefault("initialized", False)
    # NEW: lock output format per chat session
    st.session_state.setdefault("output_format", "Text")


def reset_state():
    st.session_state.messages = []
    st.session_state.cv_text = ""
    st.session_state.jd_text = ""
    st.session_state.perspective_mode = "candidate"
    st.session_state.initialized = False
    # NEW: reset locked output format
    st.session_state.output_format = "Text"


def _format_instruction(output_format: str) -> str:
    if output_format == "JSON_A":
        return FORMAT_JSON_A
    if output_format == "JSON_B":
        return FORMAT_JSON_B
    return "Return normal text (not JSON)."


def _effective_system_prompt(system_prompt: str, output_format: str) -> str:
    """
    Enforce JSON-only output when JSON formats are selected.
    """
    if output_format.startswith("JSON"):
        return (
            system_prompt
            + "\n\nIMPORTANT OUTPUT RULE:\n"
              "If the user requested JSON, you MUST output ONLY valid JSON.\n"
              "Do not output markdown, headings, backticks, code fences, or extra text.\n"
              "If a value is unknown, use an empty string or empty list.\n"
        )
    return system_prompt


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
    api_key = get_openai_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing. Set it in .env or Streamlit secrets.")

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
    if not cv_file or not jd_file:
        return False, "Please upload both CV and Job Description."

    cv_text = extract_text(cv_file)
    jd_text = extract_text(jd_file)

    if len(cv_text) < 20 or len(jd_text) < 20:
        return False, "Could not extract enough text from one of the files. Try a different format."
    if matches_blocklist(cv_text) or matches_blocklist(jd_text):
        return False, "Blocked content detected (potential prompt-injection)."

    st.session_state.cv_text = cv_text[:MAX_CHARS]
    st.session_state.jd_text = jd_text[:MAX_CHARS]
    st.session_state.perspective_mode = "interviewer" if is_interviewer else "candidate"
    st.session_state.messages = []
    st.session_state.initialized = True

    # NEW: lock the chosen output format for this chat session
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
            "Generate 10 tailored interview questions (mix behavioral + technical) based on CV and JD.\n"
            "Provide model answers.\n"
            "Do NOT output CV/JD summaries.\n\n"
            "=== CV ===\n"
            f"{st.session_state.cv_text}\n\n"
            "=== JOB DESCRIPTION ===\n"
            f"{st.session_state.jd_text}\n"
        )
        starter_prompt = f"{fmt_instr}\n\n{json_b_task}\n\nPerspective: {perspective_text}"

    else:
        step4 = "4) Generate 10 tailored interview questions (behavioral + technical) and provide answers."
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
    if matches_blocklist(user_input):
        raise RuntimeError("Blocked content detected (potential prompt-injection).")

    st.session_state.messages.append({"role": "user", "content": user_input})

    fmt_instr = _format_instruction(output_format)
    is_interviewer = st.session_state.perspective_mode == "interviewer"
    perspective_text = build_perspective_text(is_interviewer=is_interviewer)
    effective_system = _effective_system_prompt(system_prompt, output_format)

    effective_temperature = 0.0 if output_format.startswith("JSON") else temperature

    history = st.session_state.messages[-8:]
    history_block = "\n".join([f'{m["role"].upper()}: {m["content"]}' for m in history])

    if output_format == "JSON_A":
        json_a_followup_task = (
            "Task:\n"
            "Update the JSON_A output based on the NEW USER MESSAGE.\n"
            "You must still return ONLY JSON with keys: cv_summary, job_summary, matches, gaps.\n"
            "Do NOT add any other keys.\n\n"
            "=== CONTEXT ===\n"
            "CV and JD are provided below.\n\n"
            "=== CV ===\n"
            f"{st.session_state.cv_text}\n\n"
            "=== JOB DESCRIPTION ===\n"
            f"{st.session_state.jd_text}\n\n"
        )
        prompt = (
            f"{fmt_instr}\n\n"
            f"{json_a_followup_task}"
            "=== CHAT HISTORY (most recent) ===\n"
            f"{history_block}\n\n"
            "=== NEW USER MESSAGE ===\n"
            f"{user_input}\n"
        )

    elif output_format == "JSON_B":
        json_b_followup_task = (
            "Task:\n"
            "Based on the NEW USER MESSAGE, refine or generate interview questions.\n"
            "Return ONLY JSON with key: questions.\n"
            "Do NOT output CV/JD summaries.\n\n"
            "=== CONTEXT ===\n"
            "=== CV ===\n"
            f"{st.session_state.cv_text}\n\n"
            "=== JOB DESCRIPTION ===\n"
            f"{st.session_state.jd_text}\n\n"
            f"Perspective: {perspective_text}\n\n"
        )
        prompt = (
            f"{fmt_instr}\n\n"
            f"{json_b_followup_task}"
            "=== CHAT HISTORY (most recent) ===\n"
            f"{history_block}\n\n"
            "=== NEW USER MESSAGE ===\n"
            f"{user_input}\n"
        )

    else:
        base = build_user_prompt(
            cv_text=st.session_state.cv_text,
            jd_text=st.session_state.jd_text,
            step4="4) Continue the interview practice based on the new user message.",
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
        system_prompt=effective_system,
        user_prompt=prompt,
        temperature=effective_temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        force_json=output_format.startswith("JSON"),
    )

    st.session_state.messages.append({"role": "assistant", "content": assistant})
    return assistant

