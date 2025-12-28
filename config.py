"""
Central configuration module.

Defines the allowed LLM model and provides a secure, environment-agnostic
way to load the OpenAI API key (local .env for development, Streamlit Secrets
for deployment), keeping secrets out of the code and UI.
"""

import os
import streamlit as st
from dotenv import load_dotenv

# ==============================================
# Configuration
# - Model defaults and allowed models
# - API key loading (env (local) / Streamlit secrets (server))
# ==============================================

# Single model per requirements
MODEL = "gpt-4o-mini"

def get_openai_api_key() -> str:
    load_dotenv()
    key = os.getenv("OPENAI_API_KEY", "")
    if key:
        return key
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
        return st.secrets["openai"]["api_key"]
    return ""