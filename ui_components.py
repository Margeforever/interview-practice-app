# ui_components.py
import json
import streamlit as st
from dataclasses import dataclass
from typing import Literal

OutputFormat = Literal["Text", "JSON_A", "JSON_B"]

@dataclass
class UiSettings:
    model: str
    temperature: float
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    max_tokens: int
    output_format: OutputFormat

def render_sidebar(allowed_models: list[str], default_model: str) -> UiSettings:
    st.sidebar.header("Settings")

    model = st.sidebar.selectbox("Model", allowed_models, index=allowed_models.index(default_model))

    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
    top_p = st.sidebar.slider("Top-p", 0.0, 1.0, 1.0)
    frequency_penalty = st.sidebar.slider("Frequency penalty (-2..2)", -2.0, 2.0, 0.0, step=0.1)
    presence_penalty = st.sidebar.slider("Presence penalty (-2..2)", -2.0, 2.0, 0.0, step=0.1)
    max_tokens = st.sidebar.number_input("Max tokens", min_value=64, max_value=3200, value=2000, step=64)

    output_format: OutputFormat = st.sidebar.selectbox("Output format", ["Text", "JSON_A", "JSON_B"], index=0)

    return UiSettings(
        model=model,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        max_tokens=int(max_tokens),
        output_format=output_format,
    )

def render_upload_section():
    st.header("Upload CV and Job Description")
    cv_file = st.file_uploader("CV (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
    jd_file = st.file_uploader("Job Description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
    return cv_file, jd_file

def _extract_json_candidate(text: str) -> str:
    """
    Best-effort extraction of JSON from model output.
    Handles common cases like code fences or leading/trailing commentary.
    """
    if not text:
        return text

    cleaned = text.strip()

    # Remove common markdown code fences
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    # Try direct parse first
    try:
        json.loads(cleaned)
        return cleaned
    except Exception:
        pass

    # Fallback: extract from first '{' or '[' to last '}' or ']'
    start_obj = cleaned.find("{")
    start_arr = cleaned.find("[")
    starts = [i for i in [start_obj, start_arr] if i != -1]
    if not starts:
        return cleaned

    start = min(starts)
    end_obj = cleaned.rfind("}")
    end_arr = cleaned.rfind("]")
    end = max(end_obj, end_arr)

    if end == -1 or end <= start:
        return cleaned

    return cleaned[start : end + 1]

def render_assistant_output(text: str, output_format: OutputFormat) -> None:
    if output_format.startswith("JSON"):
        candidate = _extract_json_candidate(text)
        try:
            st.json(json.loads(candidate))
        except json.JSONDecodeError:
            st.error("Invalid JSON returned. Showing raw response:")
            st.text(text)
    else:
        st.markdown(text)
