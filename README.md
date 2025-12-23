# Interview Practice App

Upload a CV and Job Description, generate tailored output (Text/JSON), and continue in a multi‑turn chat with persistent context.

## Architecture
- app.py: Streamlit entry; delegates UI and chat control.
- ui_components.py: Sidebar, upload section, assistant output renderer.
- chat_controller.py: Session state, prompt building, initialize_chat, chat_turn.
- prompts_formats.py: build_perspective_text, build_user_prompt, JSON format instructions (FORMAT_JSON_A/B).
- openai_client.py: OpenAI wrapper; optional JSON mode via response_format.
- extraction.py: PDF/DOCX/TXT text extraction.
- security.py: MAX_CHARS cap and simple blocklist checks.
- config.py: ALLOWED_MODELS, MODEL_DEFAULT, API key loading.
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

Configure API key:
- .env in project root:
```
OPENAI_API_KEY=sk-...
```
or Streamlit Secrets: OPENAI_API_KEY

## Run
```powershell
python -m streamlit run app.py
# open http://localhost:8501
```
Linux/macOS:
```bash
./startup.sh
```

## Usage
1) Choose model and generation settings in the sidebar.
2) Upload CV and JD.
3) Pick Output format: Text, JSON_A, or JSON_B.
4) Click a Start button (interviewer/candidate). Then ask follow‑ups.

Notes:
- Output format is locked per chat session.
- JSON_A: returns {cv_summary, job_summary, matches[5], gaps[5]} only.
- JSON_B: returns questions[10] with {question, type, model_answer}.
- If JSON parsing fails, raw text is shown.

## JSON mode
- The app requests JSON via response_format when Output format starts with JSON.
- Use a JSON‑capable model (e.g., gpt-4o-mini or gpt-4o).
- Temperature is reduced when JSON is requested to improve validity.

## Troubleshooting
- Invalid JSON: switch to gpt-4o-mini/gpt-4o; keep Output format on JSON_A/JSON_B.
- Missing API key: set OPENAI_API_KEY in .env or Streamlit Secrets.
- ModuleNotFoundError: ensure imports point to prompts_formats (build helpers live there).
- Extraction issues: verify PDFs/DOCX are readable; install PyPDF2/python-docx.

## License
For educational use.
