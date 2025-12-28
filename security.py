import re   # Regular expressions to detect known prompt injection patterns in the text.

# ==============================================
# Security and limits
# - MAX_CHARS cap and simple blocklist checks
# ==============================================

# Prompt-injection blocklist (applied to user-provided documents only)
BLOCKLIST_PATTERNS = [
    r"ignore (?:previous )?instructions",
    r"bypass (?:security|filters)",
    r"jailbreak",
    r"exfiltrat",
    r"send (?:your|my) api key",
    r"do anything",
]

# Basic guardrail: checks user-provided text for known prompt-injection patterns
# and blocks it before sending any content to the LLM.
def matches_blocklist(text: str) -> bool:
    if not text:
        return False
    for p in BLOCKLIST_PATTERNS:
        if re.search(p, text, flags=re.IGNORECASE):
            return True
    return False

# Input length limit from CV/JD uploads to avoid excessive token usage.
MAX_CHARS = 15000