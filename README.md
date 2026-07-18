# 🔬 DealLens — AI-Powered Pitch Deck Due Diligence Tool

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?style=flat&logo=groq&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat)

DealLens is an AI-assisted due diligence tool that analyzes startup pitch decks and produces structured, investor-style reports. It is designed to replicate the first-pass screening process a venture capital analyst performs before a startup reaches a partner meeting.

🌐 **Live Demo:** https://getdeallens.streamlit.app

---

## ✨ Features

- 📄 Upload startup pitch decks as PDF files
- 🧠 AI-powered investor-style due diligence reports
- 📊 Investor Score (0–100) with investment verdict
- 📈 Six-category score breakdown
- 💡 AI-generated investment thesis
- ✅ Green flags and red flags detection
- ⚠️ Risk register generation
- 🏢 Company snapshot extraction
- 🤖 Multi-model comparison across multiple LLMs
- 🌙 Dark finance-terminal inspired interface

---

## 🚀 What It Does

Upload a startup pitch deck (PDF or pasted text) and DealLens automatically generates:

- **Investor Score (0–100)** with one of five verdicts:
  - STRONG PASS
  - PASS
  - WATCH
  - SOFT PASS
  - REJECT

- **Score Breakdown** across six investment dimensions:
  - Market Opportunity
  - Team Quality
  - Product Differentiation
  - Traction
  - Business Model
  - Risk Level

- **Investment Thesis**
  - A concise AI-generated bull case explaining why the startup could be investable.

- **Green Flags**
  - Positive investment signals.

- **Red Flags**
  - Potential concerns requiring deeper investigation.

- **Risk Register**
  - Structured list of operational, technical, financial, and execution risks.

- **Company Snapshot**
  - Industry
  - Funding Stage
  - Funding Ask
  - Market Size
  - Business Model

- **Multi-Model Comparison**
  - Run the same pitch deck through multiple LLMs and compare their scores and reasoning.

---

## 🤖 Why Multi-Model Comparison?

One AI model represents only **one opinion**.

Large Language Models can produce different scores depending on architecture, training data, and reasoning style—especially when evaluating ambiguous startup decks.

DealLens allows the same deck to be analyzed by multiple models from different model families.

This helps identify whether the AI's assessment is consistent.

### High agreement

Small score spread between models usually indicates stronger confidence.

### Low agreement

Large score spread suggests the deck is ambiguous and deserves manual review instead of relying on a single AI-generated score.

This mirrors a real-world challenge in AI-assisted financial workflows:

> Knowing **when to trust AI** and **when human judgment is still required.**

---

## 🏗️ Architecture

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

## 🛠️ Tech Stack

| Layer | Technology |
|--------|------------|
| Frontend | Streamlit |
| AI Framework | LangChain |
| LLM Provider | Groq |
| Models | GPT-OSS 20B, GPT-OSS 120B, Llama 3.3 70B |
| PDF Processing | PyMuPDF4LLM |
| Environment Variables | python-dotenv |
| Deployment | Streamlit Community Cloud |

---

## 📂 Project Structure

```text
DealLens/
├── app.py              # Main Streamlit application (UI, tabs, orchestration)
├── ai_engine.py        # PDF text extraction and Groq API integration
├── prompts.py          # Prompt templates for investor-style analysis
├── styles.py           # Custom CSS (dark finance-terminal theme)
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

The project intentionally uses a **flat file structure** instead of a deeply nested package hierarchy. For a project of this size, separating responsibilities into a handful of focused modules keeps the codebase easy to navigate while avoiding unnecessary complexity.

---

## 🤖 Available Models

| Model | Speed | Best Use |
|--------|-------|----------|
| GPT-OSS 20B | ⚡ Fast | Everyday screening and quick analysis |
| GPT-OSS 120B | 🧠 Deep | More detailed reasoning on complex decks |
| Llama 3.3 70B | ⚖️ Balanced | Cross-checking results with a different model family |

All models are available through Groq's free tier.

---

## 📄 Handling Scanned PDFs

Some startup decks are exported as image-only PDFs and contain no machine-readable text.

DealLens detects this automatically.

Instead of failing silently, the application asks the user to paste the extracted text manually.

### Steps

1. Open the PDF.
2. Press **Ctrl + A**.
3. Press **Ctrl + C**.
4. Switch to **Manual Text Mode**.
5. Paste the copied text.

This avoids adding OCR dependencies such as Tesseract, making deployment significantly simpler.

---

## ⚙️ Running Locally

```bash
# Clone repository
git clone https://github.com/yogeshpan1/AI-Automation.git

# Enter project folder
cd "AI-Automation/Pitch Deck Analyzer"

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_api_key_here" > .env

# Run Streamlit
streamlit run app.py
```

Get your free Groq API key at:

https://console.groq.com

---

## ☁️ Deployment

DealLens is deployed using **Streamlit Community Cloud**.

Every push to the `main` branch automatically redeploys the application.

Store your API key securely using Streamlit Secrets:

```toml
GROQ_API_KEY="your_api_key_here"
```

---

## 🚀 Future Improvements

- OCR support for scanned PDFs
- Export reports as PDF
- Historical report storage
- User authentication
- Financial statement analysis
- Comparable startup benchmarking
- RAG integration with startup databases
- Investment memo generation
- Portfolio tracking dashboard

---

## ⚠️ Limitations

- No persistent database (analysis history resets after refresh)
- OCR is intentionally omitted to keep deployment lightweight
- Performance depends on Groq's free-tier model availability
- AI-generated analysis should support—not replace—human investment decisions

---

## 📄 Disclaimer

DealLens is an educational and portfolio project.

The generated analysis is intended to assist with startup screening and should **not** be considered investment advice. Investment decisions should always involve independent research, professional judgment, and additional due diligence.

---

## 👨‍💻 Author

**Yogesh Pant**

---

## ⭐ Support

If you found this project interesting, consider giving it a **⭐ Star** on GitHub. It helps others discover the project and supports future development.
