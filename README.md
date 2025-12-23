# Interview Practice App (Streamlit)

Minimal but complete: upload a CV and a Job Description, generate tailored interview questions and answers, and chat in multiple turns with persistent context.

## Why a single System Prompt: Zero-shot Coach
- Clear and minimal role: senior interview coach focused on concise, actionable output.
- Reduced complexity: fewer UI options and code paths to maintain.
- Consistent results: avoids variance across multiple prompt styles.
- Fits the task: grounded advice and Q&A without inventing facts.

## Features
- Multi-turn chat
  - Chat history persists during the session.
  - Follow-ups supported (“Ask a follow up question.”).
  - CV/JD context kept in session state.
- Structured outputs
  - JSON_A: { cv_summary, job_summary, matches[5], gaps[5] }.
  - JSON_B: { questions: [{ question, type, model_answer }] } (10 entries).
  - The app attempts to parse with json.loads(); otherwise shows raw text.
- Perspective toggle: interviewer or candidate.
- Security
  - Prompt-injection blocklist on user-uploaded content.
  - Length cap MAX_CHARS to control input size.
- Robust extraction
  - PDF via PyPDF2.
  - DOCX via python-docx.
  - TXT directly.

## Project structure
```
.
├─ app.py                  # Orchestration: UI, flow, chat, prompt assembly, rendering
├─ extraction.py           # PDF/DOCX/TXT extraction
├─ prompts.py              # Perspective and prompt builders
├─ prompts_formats.py      # Minimal JSON format strings (FORMAT_JSON_A/B)
├─ security.py             # MAX_CHARS, blocklist, and checks
├─ config.py               # MODEL and get_openai_api_key()
├─ openai_client.py        # OpenAI call wrapper
├─ startup.sh              # Headless start script (Linux/macOS)
├─ requirements.txt
└─ README.md
```

## Setup (Windows / PowerShell)
1) Create and activate a virtual environment
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
# If needed:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

2) Install dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3) Configure the API key (one of)
- .env in the project root:
```
OPENAI_API_KEY=sk-...
```
- Streamlit Secrets:
  - Key: OPENAI_API_KEY
  - Or nested: openai.api_key

The app reads the key via config.get_openai_api_key().

## Run
```powershell
python -m streamlit run app.py
# open http://localhost:8501
```

Linux/macOS (headless example):
```bash
./startup.sh
# runs on 0.0.0.0:8000
```

## Usage
1) Upload CV and JD.
2) Choose output format: Text, JSON_A, or JSON_B.
3) Pick perspective: Interviewer or Candidate.
4) Click start. Then ask follow-ups in the chat (“Ask a follow up question.”).

- For JSON_A/JSON_B, the app tries to parse JSON and render it. If parsing fails, raw text is shown.

## Configuration
- System prompt is fixed to “Zero-shot Coach”.
- MODEL is set in config.py.
- MAX_CHARS and blocklist are defined in security.py.

## Troubleshooting
- ModuleNotFoundError:
  - Start Streamlit from the project folder:
    ```powershell
    cd "c:\Private Dateien Esther Heinrichs\Turing College\Git Hub\VSCode Turing College\AI Engineer\Interview Practice App"
    python -m streamlit run app.py
    ```
- PDF/DOCX extraction issues:
  - Install missing libs:
    ```powershell
    python -m pip install PyPDF2 python-docx
    ```
- Missing API key:
  - Ensure .env or Streamlit Secrets contain OPENAI_API_KEY.

## License
Use and modify for educational purposes.
