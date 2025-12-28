"""UI components.

Responsibilities:
- Sidebar controls (model and generation settings)
- Upload section (CV/JD)
- Assistant output rendering (Text / JSON)
"""

from dataclasses import dataclass
from typing import Literal

import json
import streamlit as st

OutputFormat = Literal["Text", "JSON_A", "JSON_B"]


@dataclass   # Python decorator that automatically creates simple data container for sidebar values (no logic or computation)
class UiSettings:
    """Settings captured from the sidebar UI."""
    model: str
    temperature: float
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    max_tokens: int
    output_format: OutputFormat


def render_sidebar(allowed_models: list[str], default_model: str) -> UiSettings:
    """Render the sidebar controls and return the selected settings.

    Args:
        allowed_models: List of selectable model names.
        default_model: Model preselected in the dropdown.

    Returns:
        UiSettings dataclass with all selected parameters.
    """
    st.sidebar.header("Settings")

    model = st.sidebar.selectbox(
        "Model", allowed_models, index=allowed_models.index(default_model)
    )

    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
    top_p = st.sidebar.slider("Top-p", 0.0, 1.0, 1.0)
    frequency_penalty = st.sidebar.slider(
        "Frequency penalty (-2..2)", -2.0, 2.0, 0.0, step=0.1
    )
    presence_penalty = st.sidebar.slider(
        "Presence penalty (-2..2)", -2.0, 2.0, 0.0, step=0.1
    )
    max_tokens = st.sidebar.number_input(
        "Max tokens", min_value=64, max_value=3200, value=1200, step=64
    )

    output_format: OutputFormat = st.sidebar.selectbox(
        "Output format", ["Text", "JSON_A", "JSON_B"], index=0
    )

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
    """Render the upload section for CV and Job Description.

    Returns:
        Tuple of (cv_file, jd_file) from Streamlit uploaders.
    """
    st.header("Upload CV and Job Description")
    cv_file = st.file_uploader("CV (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
    jd_file = st.file_uploader(
        "Job Description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"]
    )
    return cv_file, jd_file


def render_assistant_output(text: str, output_format: OutputFormat) -> None:
    """Render assistant output based on the chosen output format.

    Args:
        text: Assistant response as a string.
        output_format: "Text" | "JSON_A" | "JSON_B".

    Returns:
        None. Renders content to the Streamlit app.
    """
    if output_format.startswith("JSON"):
        try:
            st.json(json.loads(text))
        except json.JSONDecodeError:
            st.error("Invalid JSON returned. Showing raw response:")
            st.text(text)
    else:
        st.markdown(text)
