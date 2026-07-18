# 🔬 DealLens — AI-Powered Pitch Deck Due Diligence Tool

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?style=flat&logo=groq&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat)

DealLens is an AI-assisted due diligence tool that analyzes startup pitch decks and produces structured, investor-style analysis — built to mirror the first-pass screening a VC analyst does before a deal reaches a partner meeting.

**Live demo:** [getdeallens.streamlit.app](https://getdeallens.streamlit.app)

---

## What It Does

Upload a pitch deck (PDF or pasted text) and DealLens returns:

- **Investor Score (0–100)** with a clear verdict — STRONG PASS / PASS / WATCH / SOFT PASS / REJECT
- **Score Breakdown** across 6 dimensions: market opportunity, team quality, product differentiation, traction evidence, business model clarity, and risk level
- **Investment Thesis** — an AI-generated bull case for the deal
- **Red Flags & Green Flags** — quick-scan signal analysis
- **Risk Register** — key risks identified in the deck
- **Company Snapshot** — sector, stage, funding ask, market size at a glance
- **Multi-Model Comparison** — run the same deck through multiple AI models to check how much they agree with each other

---

## Why Multi-Model Comparison?

A single AI model's score is one opinion — and LLMs can be inconsistent, especially on ambiguous or thin decks. DealLens lets you run the same pitch text through two or three different models (from different model families, not just different sizes) and compares their scores.

- **High agreement** (small score spread) → the signal is probably reliable
- **Low agreement** (large score spread) → the deck is ambiguous and needs a human to actually read it, not just trust one AI's number

This is meant to reflect a real concern in AI-assisted financial workflows: knowing when to trust a model's output and when to flag it for manual review.

---

## Tech Stack

| Layer | Tool |
|---|---|
| UI | [Streamlit](https://streamlit.io) |
| AI orchestration | [LangChain](https://www.langchain.com/) + LangChain-Groq |
| LLM inference | [Groq](https://groq.com) (free tier) — GPT-OSS 20B, GPT-OSS 120B, Llama 3.3 70B |
| PDF parsing | [PyMuPDF4LLM](https://github.com/pymupdf/PyMuPDF4LLM) |
| Secrets management | python-dotenv (local) / Streamlit Secrets (cloud) |
| Deployment | Streamlit Community Cloud |

---

## Project Structure

- **`app.py`** — Main entry point: UI, tabs, orchestration
- **`ai_engine.py`** — PDF text extraction + Groq API calls
- **`prompts.py`** — The AI analysis prompt template
- **`styles.py`** — Custom CSS (dark finance-terminal theme)
- **`requirements.txt`** — Python dependencies

**Design choice:** the app is intentionally kept as a small number of flat files rather than a deeply nested package structure. At this project's size, that keeps the codebase easy to read top-to-bottom without added indirection.

**Design choice:** the app is intentionally kept as a small number of flat files rather than a deeply nested package structure. At this project's size, that keeps the codebase easy to read top-to-bottom without added indirection.

---

## Available Models

| Model | Speed | Best for |
|---|---|---|
| GPT-OSS 20B | Fast | Quick screening, default choice |
| GPT-OSS 120B | Deep | Slower but more nuanced reasoning on complex decks |
| Llama 3.3 70B | Balanced | A different model family — useful for cross-checking scores |

All available for free via Groq's API.

---

## Handling Scanned PDFs

Many real-world pitch decks are exported as image-based (scanned) PDFs, which have no extractable text layer. DealLens detects this case and prompts the user to paste the deck's text manually instead of failing silently:

1. Open the PDF
2. `Ctrl+A` → `Ctrl+C` to copy all text
3. Switch to **Manual Text** mode in the app and paste

---

## Running Locally

```bash
# 1. Clone the repo
git clone https://github.com/yogeshpan1/AI-Automation.git
cd "AI-Automation/Pitch Deck Analyzer"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env

# 4. Run
streamlit run app.py
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

---

## Deployment

Deployed on **Streamlit Community Cloud**, connected directly to this GitHub repo — every push to `main` auto-redeploys.

API key is stored via Streamlit's built-in **Secrets** manager (not committed to the repo):

```toml
GROQ_API_KEY = "your_key_here"
```

---

## Limitations & Honest Notes

- **No persistent storage** — analysis history lives only in the browser session and resets on refresh. For a production version, this would move to a proper database (e.g. Postgres via Supabase).
- **No OCR fallback** — image-based PDFs require manual text pasting rather than automatic OCR extraction, to keep the deployment dependency-free (OCR requires system-level binaries like Tesseract that aren't trivial to run on Streamlit Cloud).
- **Free-tier LLMs** — Groq's free tier models occasionally deprecate or rate-limit; the model selector lets users switch if one becomes unavailable.

---

## Disclaimer

DealLens is an AI-assisted screening tool for educational and portfolio purposes. Output is not investment advice and should not be the sole basis for any funding decision.

---

Built by **Yogesh Pant** — final-year Computer Science student, Islington College / London Metropolitan University.
