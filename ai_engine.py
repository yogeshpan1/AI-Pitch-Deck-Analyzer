"""Handles PDF text extraction and the AI analysis call."""

import re
import json
import time
import pymupdf4llm
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

from config import GROQ_MODEL, GROQ_TEMPERATURE, MAX_INPUT_CHARS, PIPELINE_STEPS
from prompts import ANALYSIS_PROMPT
from ocr_engine import is_ocr_available, extract_text_via_ocr


def extract_pdf_text(pdf_path: str) -> str:
    """Extracts and cleans text from a PDF's embedded text layer. Empty on image-based PDFs."""
    raw = pymupdf4llm.to_markdown(pdf_path)
    cleaned = re.sub(r'\s+', ' ', raw)
    cleaned = re.sub(r'[^\x00-\x7F]+', '', cleaned).strip()
    return cleaned


def extract_pdf_text_with_ocr_fallback(pdf_path: str, min_length: int = 100):
    """
    Tries the normal text layer first. If that returns too little text
    (i.e. an image-based/scanned PDF) and OCR is available, falls back to OCR.
    Returns (text, method) where method is 'text_layer', 'ocr', or 'none'.
    """
    text = extract_pdf_text(pdf_path)
    if len(text) >= min_length:
        return text, "text_layer"

    if is_ocr_available():
        ocr_text = extract_text_via_ocr(pdf_path)
        if len(ocr_text) >= min_length:
            return ocr_text, "ocr"

    return "", "none"


def _strip_json_fences(raw: str) -> str:
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'^```\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return raw.strip()


def _call_model(text_input: str, model_name: str):
    """Raw Groq call + JSON parse. Raises on failure — caller handles it."""
    model = ChatGroq(model=model_name, temperature=GROQ_TEMPERATURE)
    prompt = PromptTemplate.from_template(ANALYSIS_PROMPT)
    chain = prompt | model
    response = chain.invoke({"text": text_input[:MAX_INPUT_CHARS]})
    raw_json = _strip_json_fences(response.content.strip())
    return json.loads(raw_json)


def run_analysis(text_input: str, progress_placeholder, render_pipeline_fn, model_name: str = GROQ_MODEL):
    """
    Runs the staged pipeline UI + the actual Groq call.
    `render_pipeline_fn(placeholder, state)` is called to update the UI at each stage.
    Returns (data, error) — data is None on failure, error is None on success.
    """
    state = ["pending"] * len(PIPELINE_STEPS)

    state[0] = "active"
    render_pipeline_fn(progress_placeholder, state)
    time.sleep(0.4)

    state[0] = "done"
    state[1] = "active"
    render_pipeline_fn(progress_placeholder, state)
    time.sleep(0.3)

    try:
        state[1] = "done"
        state[2] = "active"
        render_pipeline_fn(progress_placeholder, state)

        data = _call_model(text_input, model_name)

        state[2] = "done"
        state[3] = "active"
        render_pipeline_fn(progress_placeholder, state)
        time.sleep(0.3)

        state[3] = "done"
        render_pipeline_fn(progress_placeholder, state)
        time.sleep(0.2)

        progress_placeholder.empty()
        return data, None

    except json.JSONDecodeError:
        progress_placeholder.empty()
        return None, "Model returned non-JSON. Try again — free tier occasionally truncates responses."
    except Exception as e:
        progress_placeholder.empty()
        return None, f"Analysis error: {e}"


def run_analysis_silent(text_input: str, model_name: str = GROQ_MODEL):
    """
    Same as run_analysis but with no UI/pipeline — used for batch mode
    where showing a per-file pipeline would be too noisy.
    Returns (data, error).
    """
    try:
        return _call_model(text_input, model_name), None
    except json.JSONDecodeError:
        return None, "Model returned non-JSON."
    except Exception as e:
        return None, f"Analysis error: {e}"


def run_multi_model_analysis(text_input: str, model_names: list, progress_placeholder=None):
    """
    Runs the same pitch text through multiple models for comparison.
    Returns dict {model_name: (data, error)}.
    """
    results = {}
    for i, model_name in enumerate(model_names):
        if progress_placeholder:
            progress_placeholder.markdown(
                f'<div class="card">Running <b>{model_name}</b> ({i+1}/{len(model_names)})...</div>',
                unsafe_allow_html=True,
            )
        data, error = run_analysis_silent(text_input, model_name)
        results[model_name] = (data, error)
    if progress_placeholder:
        progress_placeholder.empty()
    return results