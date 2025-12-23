import os
import streamlit as st
from dotenv import load_dotenv

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