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

## Prompting Strategy

This application primarily uses **Zero-Shot Prompting**, which proved sufficient
for the given task and keeps the prompt logic simple and transparent.

The following prompting techniques were considered:

### 1. Zero-Shot Prompting (USED)
The model receives a single system prompt with clear instructions and constraints.
This approach was chosen because:
- the task is well-defined,
- the CV and Job Description provide sufficient context,
- it minimizes prompt complexity and cost.

### 2. Few-Shot Prompting (NOT USED)
Few-shot prompting would include example CV/JD pairs and expected outputs.
It was not used because:
- suitable examples are highly domain-specific,
- it increases token usage and cost,
- it risks overfitting to example structure.

### 3. Chain-of-Thought Prompting (NOT USED)
Chain-of-Thought encourages the model to expose intermediate reasoning steps.
It was avoided because:
- internal reasoning is not required in the final output,
- it can increase verbosity and cost,
- structured JSON output benefits from concise answers instead.

### 4. Role-Based Prompting (LIMITED USE)
A lightweight role instruction (interviewer vs. candidate) is applied.
A stronger role-play setup was not needed because:
- the task remains factual and structured,
- excessive role-play can reduce determinism.

### 5. Self-Consistency Prompting (NOT USED)
Generating multiple answers and selecting the best one was not used because:
- it significantly increases API calls and cost,
- the use case does not require probabilistic aggregation.

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
