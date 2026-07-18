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
