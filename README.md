# DealLens — AI-Powered Pitch Deck Due Diligence Tool

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?style=flat&logo=groq&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat)

DealLens is an AI-assisted due diligence tool that analyzes startup pitch decks and produces structured, investor-style reports. It replicates the first-pass screening process a venture capital analyst performs before a startup reaches a partner meeting.

**Live Demo:** [getdeallens.streamlit.app](https://getdeallens.streamlit.app)

---

## Features

- Upload startup pitch decks as PDF files, or paste text directly
- AI-generated investor-style due diligence report
- Investor Score (0–100) with a clear investment verdict
- Six-category score breakdown
- AI-generated investment thesis
- Green flag / red flag detection
- Risk register generation
- Company snapshot extraction (sector, stage, funding ask, market size)
- Multi-model comparison across multiple LLMs
- Dark, finance-terminal inspired interface

---

## What It Does

Upload a startup pitch deck (PDF or pasted text) and DealLens generates:

- **Investor Score (0–100)** with one of five verdicts: STRONG PASS, PASS, WATCH, SOFT PASS, REJECT
- **Score Breakdown** across six dimensions: Market Opportunity, Team Quality, Product Differentiation, Traction, Business Model, Risk Level
- **Investment Thesis** — a concise AI-generated bull case for the deal
- **Green Flags** — positive investment signals
- **Red Flags** — potential concerns requiring deeper investigation
- **Risk Register** — structured list of operational, technical, financial, and execution risks
- **Company Snapshot** — sector, stage, funding ask, market size, business model
- **Multi-Model Comparison** — run the same deck through multiple LLMs and compare their scores and reasoning

---

## Why Multi-Model Comparison?

A single AI model represents one opinion. Large language models can produce different scores depending on architecture, training data, and reasoning style — especially on ambiguous startup decks.

DealLens lets the same deck be analyzed by multiple models from different model families, to check whether the assessment is consistent.

- **High agreement** (small score spread) generally indicates stronger confidence in the result.
- **Low agreement** (large score spread) suggests the deck is ambiguous and deserves manual review rather than reliance on a single AI-generated score.

This reflects a real challenge in AI-assisted financial workflows: knowing when to trust an AI output, and when human judgment is still required.

---

## Architecture

```text
            Startup Pitch Deck
                    │
                    ▼
         PDF Text Extraction
                    │
                    ▼
          Prompt Engineering
                    │
                    ▼
        Groq-hosted Large Language Models
                    │
                    ▼
      Investor-Style Due Diligence Analysis
                    │
                    ▼
         Streamlit Interactive Dashboard
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI Framework | LangChain |
| LLM Provider | Groq |
| Models | GPT-OSS 20B, GPT-OSS 120B, Llama 3.3 70B |
| PDF Processing | PyMuPDF4LLM |
| Environment Variables | python-dotenv |
| Deployment | Streamlit Community Cloud |

---

## Project Structure

- **`app.py`** — Main entry point: UI, tabs, orchestration
- **`ai_engine.py`** — PDF text extraction and Groq API integration
- **`prompts.py`** — Prompt templates for investor-style analysis
- **`styles.py`** — Custom CSS (dark finance-terminal theme)
- **`requirements.txt`** — Python dependencies

The project intentionally uses a flat file structure instead of a deeply nested package hierarchy. For a project of this size, separating responsibilities into a handful of focused modules keeps the codebase easy to navigate while avoiding unnecessary complexity.

---

## Available Models

| Model | Speed | Best Use |
|---|---|---|
| GPT-OSS 20B | Fast | Everyday screening and quick analysis |
| GPT-OSS 120B | Deep | More detailed reasoning on complex decks |
| Llama 3.3 70B | Balanced | Cross-checking results with a different model family |

All models are available through Groq's free tier.

---

## Handling Scanned PDFs

Some startup decks are exported as image-only PDFs with no machine-readable text layer. DealLens detects this automatically and, instead of failing silently, prompts the user to paste the extracted text manually.

**Steps:**
1. Open the PDF
2. Press `Ctrl+A`, then `Ctrl+C`
3. Switch to Manual Text mode in the app
4. Paste the copied text

This avoids adding OCR dependencies such as Tesseract, keeping deployment simpler.

---

## Running Locally

```bash
# Clone the repository
git clone https://github.com/yogeshpan1/AI-Automation.git

# Enter the project folder
cd "AI-Automation/Pitch Deck Analyzer"

# Install dependencies
pip install -r requirements.txt

# Create a .env file with your Groq API key
echo "GROQ_API_KEY=your_api_key_here" > .env

# Run the app
streamlit run app.py
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

---

## Deployment

DealLens is deployed on Streamlit Community Cloud. Every push to `main` automatically redeploys the application.

API key is stored via Streamlit's Secrets manager:

```toml
GROQ_API_KEY = "your_api_key_here"
```

---

## Future Improvements

- OCR support for scanned PDFs
- Export reports as PDF
- Persistent history storage
- User authentication
- Financial statement analysis
- Comparable startup benchmarking
- RAG integration with startup databases
- Investment memo generation

---

## Limitations

- No persistent database — analysis history resets after refresh
- OCR is intentionally omitted to keep deployment lightweight
- Performance depends on Groq's free-tier model availability
- AI-generated analysis should support, not replace, human investment decisions

---

## Disclaimer

DealLens is an educational and portfolio project. The generated analysis is intended to assist with startup screening and should not be considered investment advice. Investment decisions should always involve independent research, professional judgment, and additional due diligence.

---

## Author

**Yogesh Pant**

