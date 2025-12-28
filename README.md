# Interview Practice App

Upload a CV and a Job Description, generate tailored output (Text or JSON),
and continue in a multi‑turn chat with persistent context.

## Architecture
- app.py: Streamlit entry point; delegates UI and chat control.
- ui_components.py: Sidebar, upload section, assistant output renderer.
- chat_controller.py: Session state, prompt building, initialize_chat, chat_turn.
- prompts_formats.py: build_perspective_text, build_user_prompt, JSON formats
  (FORMAT_JSON_A / FORMAT_JSON_B).
- openai_client.py: OpenAI wrapper; optional JSON mode via response_format.
- extraction.py: PDF/DOCX/TXT text extraction.
- security.py: MAX_CHARS cap and simple blocklist checks.
- config.py: MODEL and API key loading.
- startup.sh: Headless start script (Linux/macOS).

## Requirements
- Python 3.10+
- See requirements.txt

## Setup (Windows PowerShell)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Configure the API key
- .env in the project root:
```
OPENAI_API_KEY=sk-...
```
or Streamlit Secrets: OPENAI_API_KEY

## Run
```powershell
python -m streamlit run app.py
# then open http://localhost:8501
```

Linux/macOS:
```bash
./startup.sh
```

## Usage
1) Choose model and generation settings in the sidebar (MODEL from config.py).
2) Upload CV and JD.
3) Pick Output format: Text, JSON_A, or JSON_B.
4) Click a Start button (interviewer/candidate). Then ask follow‑ups.

Notes
- Output format is locked per chat session.
- JSON_A: returns {cv_summary, job_summary, matches[5], gaps[5]} only.
- JSON_B: returns questions[10] with {question, type, model_answer}.
- If JSON parsing fails, the raw response is shown.

## JSON mode
- The app requests JSON via response_format when Output format starts with JSON.
- Use a JSON‑capable model (for example, gpt-4o-mini or gpt-4o).
- Temperature is reduced for JSON to improve validity.

## Troubleshooting
- Invalid JSON: switch to gpt-4o-mini/gpt-4o and keep Output format on JSON_A/JSON_B.
- Missing API key: set OPENAI_API_KEY in .env or Streamlit Secrets.
- Import errors: ensure imports point to prompts_formats for prompt helpers.
- Extraction issues: verify PDFs/DOCX are readable; install PyPDF2/python-docx.

## License
For educational use.
