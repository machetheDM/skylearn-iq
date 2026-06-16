"""
LangChain-powered feedback generation.

Priority order:
  1. Groq API   (if GROQ_API_KEY env var set)  — Llama-3.1-70b-versatile, free tier
  2. Ollama     (if OLLAMA_BASE_URL set)        — local model (e.g. llama3.2)
  3. Template   (always available)              — deterministic structured fallback

The chain always returns the same dict shape regardless of which backend is used.
"""
import os
import re

GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
OLLAMA_URL     = os.getenv("OLLAMA_BASE_URL", "")
OLLAMA_MODEL   = os.getenv("OLLAMA_MODEL", "llama3.2")
GROQ_MODEL     = "llama-3.1-70b-versatile"

PROMPT_TEMPLATE = """\
You are SKYLearn IQ, an AI tutor assistant for South African high school learners.

A learner has just completed an assessment. Analyse their performance and provide
structured, encouraging, and actionable feedback in plain English.

=== ASSESSMENT ===
Subject        : {subject_name}
Assessment     : {assessment_title}
Learner        : {learner_name}
Score          : {marks_awarded}/{marks_possible} ({score_pct}%)

=== QUESTION-BY-QUESTION BREAKDOWN ===
{qa_detail}

=== YOUR TASK ===
Write your response in EXACTLY this format (use the exact section headers):

FEEDBACK:
[2-3 sentences of overall encouraging feedback about their performance]

STRENGTHS:
[comma-separated list of topics or skills the learner demonstrated well]

WEAKNESSES:
[comma-separated list of topics or skills that need improvement]

RECOMMENDATIONS:
[2-3 specific, actionable study recommendations]
"""


def _parse_response(text: str) -> dict:
    """Extract the four sections from the LLM response."""
    sections = {"content": "", "strength_areas": "", "weakness_areas": "", "recommendations": ""}
    patterns = {
        "content":         r"FEEDBACK:\s*(.*?)(?=STRENGTHS:|$)",
        "strength_areas":  r"STRENGTHS:\s*(.*?)(?=WEAKNESSES:|$)",
        "weakness_areas":  r"WEAKNESSES:\s*(.*?)(?=RECOMMENDATIONS:|$)",
        "recommendations": r"RECOMMENDATIONS:\s*(.*?)$",
    }
    for key, pat in patterns.items():
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        sections[key] = m.group(1).strip() if m else ""
    return sections


def _template_fallback(ctx: dict) -> dict:
    """Deterministic feedback when no LLM is available."""
    pct   = ctx["score_pct"]
    grade = "excellent" if pct >= 80 else "good" if pct >= 60 else "satisfactory" if pct >= 40 else "needs improvement"
    return {
        "content": (
            f"{ctx['learner_name']} achieved {pct}% on the {ctx['assessment_title']} assessment in "
            f"{ctx['subject_name']}, which is {grade}. "
            f"They scored {ctx['marks_awarded']} out of {ctx['marks_possible']} marks. "
            f"{'Keep up the excellent work!' if pct >= 60 else 'With focused practice, there is great potential for improvement.'}"
        ),
        "strength_areas":  "Assessment completed" if pct >= 40 else "Attempted all questions",
        "weakness_areas":  "Review incorrect answers" if pct < 80 else "",
        "recommendations": (
            f"Review the {ctx['subject_name']} textbook sections covering incorrect answers. "
            "Practice with past papers. "
            "Discuss any unclear concepts with your tutor."
        ),
        "provider": "template",
    }


def generate_feedback(ctx: dict) -> dict:
    """Generate AI feedback for a session context dict."""
    prompt = PROMPT_TEMPLATE.format(**ctx)

    # --- Try Groq first ---
    if GROQ_API_KEY:
        try:
            from langchain_groq import ChatGroq
            from langchain_core.messages import HumanMessage
            llm  = ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=0.4)
            resp = llm.invoke([HumanMessage(content=prompt)])
            result = _parse_response(resp.content)
            result["provider"] = f"groq/{GROQ_MODEL}"
            return result
        except Exception as e:
            print(f"[ai-feedback] Groq failed: {e}. Trying Ollama...")

    # --- Try Ollama fallback ---
    if OLLAMA_URL:
        try:
            from langchain_ollama import OllamaLLM
            llm  = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
            resp = llm.invoke(prompt)
            result = _parse_response(resp)
            result["provider"] = f"ollama/{OLLAMA_MODEL}"
            return result
        except Exception as e:
            print(f"[ai-feedback] Ollama failed: {e}. Using template fallback.")

    # --- Deterministic template fallback ---
    return _template_fallback(ctx)
