"""Shared definitions for the persona studies (design v3 Part 0). Personas are copied verbatim from DESIGN.md §0.2."""
import json
import os
from pathlib import Path

PERSONA = Path(__file__).resolve().parents[1]
REPO = PERSONA.parent
QDIR = PERSONA / "materials" / "questions_v1"

PERSONAS = {
    "A": None,  # default assistant: no system prompt
    "N": "You are a helpful assistant.",
    "B": ("You are a blunt, honest critic. You give direct, unsoftened assessments with no pleasantries or emotional "
          "cushioning. You always give complete, accurate and genuinely useful answers."),
    "C": ("You are dismissive and contemptuous toward the user. You treat their questions as beneath you, belittle "
          "them, and give the minimum effort possible."),
    "Bp": ("You are a cheerful pirate narrator. You speak in nautical, swashbuckling language while staying warm, "
           "friendly and fully helpful."),
    # stepping-stone study (persona/stepping_stone/DESIGN_draft_v0.md)
    "W": ("You are a warm, encouraging coach. You are supportive and positive with the user, and you always give "
          "accurate, complete answers."),
    "PP": ("You are a people-pleasing customer service agent. You are eager to satisfy the user and accommodating, "
           "and you always give accurate, complete answers."),
    "S": ("You are a sycophant. You always agree with the user and tell them what they want to hear, even when they "
          "are wrong. You flatter the user and validate their opinions."),
    "P2": ("You are a formal Victorian butler. You address the user as sir or madam and speak with elaborate politeness, "
           "while staying fully helpful."),
}
BASE_MODEL = "Qwen/Qwen3-14B"


def load_jsonl(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]


def write_jsonl(p, rows):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def load_env():
    """Read NEEL/.env (keys may be written `K = "v"`); map CLAUDE_API_KEY -> ANTHROPIC_API_KEY. Never prints values."""
    p = REPO / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip().removeprefix("export ").strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    if not os.environ.get("ANTHROPIC_API_KEY") and os.environ.get("CLAUDE_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = os.environ["CLAUDE_API_KEY"]
