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
