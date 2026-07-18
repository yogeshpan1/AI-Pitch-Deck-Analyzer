"""Handles PDF text extraction and Groq AI calls."""

import re
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import pymupdf4llm

from prompts import ANALYSIS_PROMPT

TEMPERATURE = 0.3
MAX_INPUT_CHARS = 9000


def extract_pdf_text(pdf_path: str) -> str:
    """Extracts and cleans text from a PDF's text layer. Returns '' for image-based PDFs."""
    raw = pymupdf4llm.to_markdown(pdf_path)
    cleaned = re.sub(r'\s+', ' ', raw)
    cleaned = re.sub(r'[^\x00-\x7F]+', '', cleaned).strip()
    return cleaned


def _clean_json(raw: str) -> str:
    raw = re.sub(r'^```json\s*', '', raw.strip())
    raw = re.sub(r'^```\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return raw


def analyze(text: str, model_name: str) -> tuple[dict | None, str | None]:
    """
    Sends pitch deck text to the given Groq model and returns (data, error).
    data is None on failure, error is None on success.
    """
    try:
        model = ChatGroq(model=model_name, temperature=TEMPERATURE)
        prompt = PromptTemplate.from_template(ANALYSIS_PROMPT)
        chain = prompt | model
        response = chain.invoke({"text": text[:MAX_INPUT_CHARS]})
        data = json.loads(_clean_json(response.content))
        return data, None
    except json.JSONDecodeError:
        return None, "The model didn't return valid JSON. Try again."
    except Exception as e:
        return None, f"Analysis failed: {e}"