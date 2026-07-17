import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import pymupdf4llm
import re
import json
import time
from datetime import datetime

load_dotenv()

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DealLens · AI Due Diligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS — Finance terminal aesthetic
# Palette: #0A0C10 bg · #111318 surface · #1C2030 card
#          #00D4AA accent (teal) · #F0C040 gold · #FF4D6D risk-red
#          #E8EDF5 text · #8A94A8 muted
# Type: 'JetBrains Mono' for data, 'Inter' for prose
# Signature: animated score ring + horizontal metric tape
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0A0C10;
    color: #E8EDF5;
}
.stApp { background-color: #0A0C10; }
.main .block-container { 
    padding: 2rem 2.5rem;
    max-width: 1200px;
}

/* ── Header bar ── */
.header-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #1C2030;
    padding-bottom: 1.2rem;
    margin-bottom: 2rem;
}
.logo-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem;
    font-weight: 600;
    letter-spacing: -0.5px;
    color: #E8EDF5;
}
.logo-text span { color: #00D4AA; }
.tagline {
    font-size: 0.72rem;
    color: #8A94A8;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 500;
}
.timestamp {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #8A94A8;
    letter-spacing: 0.05em;
}

/* ── Cards ── */
.card {
    background: #111318;
    border: 1px solid #1C2030;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-title {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #8A94A8;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.card-title::before {
    content: '';
    display: inline-block;
    width: 3px;
    height: 12px;
    background: #00D4AA;
    border-radius: 2px;
}

/* ── Score ring (signature element) ── */
.score-ring-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}
.score-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #8A94A8;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.score-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 3rem;
    font-weight: 600;
    line-height: 1;
}
.score-verdict {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    margin-top: 0.3rem;
}

/* ── Metric chips ── */
.metric-tape {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
}
.metric-chip {
    background: #1C2030;
    border: 1px solid #2A3050;
    border-radius: 6px;
    padding: 0.6rem 1rem;
    flex: 1;
    min-width: 130px;
}
.chip-label {
    font-size: 0.62rem;
    color: #8A94A8;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 500;
}
.chip-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95rem;
    font-weight: 600;
    color: #E8EDF5;
    margin-top: 0.2rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ── Risk meter ── */
.risk-bar-container { margin-top: 0.4rem; }
.risk-bar-track {
    background: #1C2030;
    border-radius: 4px;
    height: 6px;
    width: 100%;
    overflow: hidden;
}
.risk-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.6s ease;
}
.risk-label-row {
    display: flex;
    justify-content: space-between;
    margin-top: 0.3rem;
    font-size: 0.62rem;
    color: #8A94A8;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Section heading ── */
.section-heading {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #8A94A8;
    margin: 1.5rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-heading::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1C2030;
}

/* ── Info rows ── */
.info-row {
    display: flex;
    gap: 0;
    border: 1px solid #1C2030;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 0.5rem;
}
.info-key {
    background: #1C2030;
    padding: 0.65rem 1rem;
    font-size: 0.7rem;
    font-weight: 600;
    color: #8A94A8;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    width: 180px;
    flex-shrink: 0;
    display: flex;
    align-items: flex-start;
    padding-top: 0.75rem;
}
.info-val {
    padding: 0.65rem 1.1rem;
    font-size: 0.84rem;
    color: #E8EDF5;
    flex: 1;
    line-height: 1.55;
}

/* ── Risks ── */
.risk-item {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid #1C2030;
    font-size: 0.84rem;
    color: #E8EDF5;
    line-height: 1.5;
}
.risk-item:last-child { border-bottom: none; }
.risk-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #FF4D6D;
    margin-top: 0.45rem;
    flex-shrink: 0;
}

/* ── Red flags / Green flags ── */
.flag-row {
    display: flex;
    gap: 1rem;
    margin-top: 0.5rem;
}
.flag-col {
    flex: 1;
    background: #111318;
    border: 1px solid #1C2030;
    border-radius: 8px;
    padding: 1rem 1.2rem;
}
.flag-header {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}
.flag-header.red { color: #FF4D6D; }
.flag-header.green { color: #00D4AA; }
.flag-item {
    display: flex;
    gap: 0.5rem;
    font-size: 0.8rem;
    color: #C8D0E0;
    margin-bottom: 0.45rem;
    line-height: 1.45;
}

/* ── Comp table ── */
.comp-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.comp-table th {
    font-size: 0.62rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #8A94A8;
    font-weight: 600;
    padding: 0.6rem 1rem;
    border-bottom: 2px solid #1C2030;
    text-align: left;
}
.comp-table td {
    padding: 0.65rem 1rem;
    border-bottom: 1px solid #1C2030;
    color: #E8EDF5;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
}
.comp-table tr:last-child td { border-bottom: none; }
.comp-table .highlight-row td { background: #1C2030; color: #00D4AA; }

/* ── Quote block (thesis) ── */
.thesis-block {
    border-left: 3px solid #00D4AA;
    background: #0E1118;
    border-radius: 0 6px 6px 0;
    padding: 1rem 1.4rem;
    font-size: 0.9rem;
    color: #C8D0E0;
    line-height: 1.7;
    font-style: italic;
    margin-top: 0.5rem;
}

/* ── Streamlit overrides ── */
.stRadio > div { gap: 0.5rem !important; }
.stRadio label {
    background: #111318 !important;
    border: 1px solid #1C2030 !important;
    border-radius: 6px !important;
    padding: 0.5rem 1rem !important;
    color: #E8EDF5 !important;
    font-size: 0.84rem !important;
    cursor: pointer;
    transition: border-color 0.15s;
}
.stRadio label:hover { border-color: #00D4AA !important; }
div[data-testid="stFileUploader"] {
    background: #111318;
    border: 1px dashed #2A3050;
    border-radius: 8px;
    padding: 1.5rem;
}
.stTextArea textarea {
    background: #111318 !important;
    border: 1px solid #1C2030 !important;
    color: #E8EDF5 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    border-radius: 6px !important;
}
.stTextArea textarea:focus { border-color: #00D4AA !important; box-shadow: 0 0 0 2px rgba(0,212,170,0.1) !important; }
div[data-testid="stAlert"] { border-radius: 6px !important; }

/* Analyze button */
.stButton > button {
    background: #00D4AA !important;
    color: #0A0C10 !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.06em !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.65rem 2rem !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.stDownloadButton > button {
    background: #1C2030 !important;
    color: #E8EDF5 !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    border: 1px solid #2A3050 !important;
    border-radius: 6px !important;
}
.stDownloadButton > button:hover { border-color: #00D4AA !important; }

/* ── Spinner override ── */
.stSpinner > div { border-color: #00D4AA transparent transparent transparent !important; }

/* ── Hide default streamlit chrome ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.viewerBadge_container__1QSob { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
now = datetime.now().strftime("%Y-%m-%d  %H:%M UTC")
st.markdown(f"""
<div class="header-bar">
    <div>
        <div class="logo-text">Deal<span>Lens</span></div>
        <div class="tagline">AI-Powered Due Diligence · Pitch Deck Intelligence</div>
    </div>
    <div class="timestamp">{now}</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# INPUT SECTION
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-heading">Input</div>', unsafe_allow_html=True)

mode_col, _ = st.columns([2, 1])
with mode_col:
    analysis_mode = st.radio(
        "Source",
        ["📄 PDF Upload", "✏️ Manual Text Input"],
        horizontal=True,
        label_visibility="collapsed",
    )

pdf_file = None
manual_text = ""

if analysis_mode == "📄 PDF Upload":
    pdf_file = st.file_uploader(
        "Drop pitch deck PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )
    st.markdown("""
    <div style="font-size:0.75rem; color:#8A94A8; margin-top:0.5rem;">
    ⚠️ Image-based PDFs (scanned decks) won't extract text — use Manual Text Input instead.<br>
    💡 To get text: open PDF → Ctrl+A → Ctrl+C → paste below in Manual mode.
    </div>
    """, unsafe_allow_html=True)
else:
    manual_text = st.text_area(
        "Paste pitch deck text",
        height=220,
        placeholder="Paste the full text of the pitch deck here — problem, solution, market size, traction, team, ask...",
        label_visibility="collapsed",
    )

# ─────────────────────────────────────────────────────────────
# TRIGGER ANALYSIS
# ─────────────────────────────────────────────────────────────
has_input = (pdf_file is not None) or (manual_text.strip() != "")

if has_input:
    analyze_btn = st.button("🔬 Run Due Diligence Analysis")
else:
    analyze_btn = False
    st.markdown(
        '<div style="font-size:0.8rem;color:#8A94A8;margin-top:0.5rem;">Provide a pitch deck to begin.</div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────
# ANALYSIS PROMPT — structured JSON output
# ─────────────────────────────────────────────────────────────
ANALYSIS_PROMPT = """
You are a senior investment analyst at a top-tier VC firm. Analyze this startup pitch deck and return ONLY a valid JSON object — no markdown, no explanation, no backticks.

Return exactly this structure:
{{
  "company_name": "...",
  "one_liner": "Single sentence describing what the company does",
  "sector": "e.g. FinTech / HealthTech / SaaS / Marketplace / etc.",
  "stage": "e.g. Pre-Seed / Seed / Series A / etc.",
  "problem": "2-3 sentences on the problem being solved",
  "solution": "2-3 sentences on the proposed solution",
  "business_model": "How they make money — 1-2 sentences",
  "market_size": "TAM/SAM/SOM if mentioned, otherwise estimate with reasoning",
  "funding_ask": "Amount and use of funds if stated, else 'Not stated'",
  "traction": "Key traction metrics, revenue, users, partnerships, pilots",
  "team": "Key team members and relevant credentials",
  "competitive_advantage": "Moat or differentiation — 1-2 sentences",
  "competitors": [
    {{"name": "...", "weakness": "..."}},
    {{"name": "...", "weakness": "..."}}
  ],
  "red_flags": ["flag 1", "flag 2", "flag 3"],
  "green_flags": ["strength 1", "strength 2", "strength 3"],
  "risks": ["risk 1", "risk 2", "risk 3"],
  "investment_thesis": "2-3 sentence bull case for investment",
  "investor_score": 72,
  "score_rationale": "Why this score — 1 sentence",
  "score_breakdown": {{
    "market_opportunity": 8,
    "team_quality": 6,
    "product_differentiation": 7,
    "traction_evidence": 5,
    "business_model_clarity": 7,
    "risk_level": 6
  }},
  "verdict": "STRONG PASS | PASS | WATCH | SOFT PASS | PASS"
}}

Score investor_score 0–100 (≥80 = STRONG PASS, 65–79 = PASS, 50–64 = WATCH, 35–49 = SOFT PASS, <35 = PASS).
score_breakdown values are each out of 10.

Pitch deck text:
{text}
"""

# ─────────────────────────────────────────────────────────────
# RUN ANALYSIS
# ─────────────────────────────────────────────────────────────
if analyze_btn:
    pitch_text = ""

    if pdf_file is not None:
        with open("temp_deck.pdf", "wb") as f:
            f.write(pdf_file.getbuffer())
        try:
            raw = pymupdf4llm.to_markdown("temp_deck.pdf")
            cleaned = re.sub(r'\s+', ' ', raw)
            cleaned = re.sub(r'[^\x00-\x7F]+', '', cleaned).strip()
            if len(cleaned) < 100:
                st.warning("⚠️ This PDF appears image-based — no text could be extracted. Switch to Manual Text Input.")
                st.stop()
            pitch_text = cleaned
        except Exception as e:
            st.error(f"PDF read error: {e}")
            st.stop()
    else:
        pitch_text = manual_text.strip()

    if len(pitch_text) < 80:
        st.warning("Not enough text to analyze. Please provide more content.")
        st.stop()

    # Truncate to avoid token limits
    input_text = pitch_text[:9000]

    with st.spinner("Running AI due diligence..."):
        try:
            model = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3)
            prompt = PromptTemplate.from_template(ANALYSIS_PROMPT)
            chain = prompt | model
            response = chain.invoke({"text": input_text})
            raw_json = response.content.strip()
            # Strip any accidental markdown fences
            raw_json = re.sub(r'^```json\s*', '', raw_json)
            raw_json = re.sub(r'^```\s*', '', raw_json)
            raw_json = re.sub(r'\s*```$', '', raw_json)
            data = json.loads(raw_json)
        except json.JSONDecodeError:
            st.error("Model returned non-JSON. Try again — Groq free tier occasionally truncates responses.")
            st.stop()
        except Exception as e:
            st.error(f"Analysis error: {e}")
            st.stop()

    # ── SCORE COLORS ──
    score = data.get("investor_score", 0)
    verdict = data.get("verdict", "WATCH")
    if score >= 80:
        score_color = "#00D4AA"
        verdict_bg = "rgba(0,212,170,0.12)"
        verdict_color = "#00D4AA"
    elif score >= 65:
        score_color = "#5BC4FF"
        verdict_bg = "rgba(91,196,255,0.12)"
        verdict_color = "#5BC4FF"
    elif score >= 50:
        score_color = "#F0C040"
        verdict_bg = "rgba(240,192,64,0.12)"
        verdict_color = "#F0C040"
    else:
        score_color = "#FF4D6D"
        verdict_bg = "rgba(255,77,109,0.12)"
        verdict_color = "#FF4D6D"

    # ─── RESULTS LAYOUT ───────────────────────────────────────
    st.markdown('<div class="section-heading">Analysis Results</div>', unsafe_allow_html=True)

    # Row 1: Score + Company snapshot
    col_score, col_info = st.columns([1, 3])

    with col_score:
        st.markdown(f"""
        <div class="card" style="text-align:center; padding: 2rem 1rem;">
            <div class="score-label">Investor Score</div>
            <div class="score-number" style="color:{score_color};">{score}</div>
            <div style="font-size:0.65rem; color:#8A94A8; font-family:'JetBrains Mono',monospace;">/100</div>
            <div class="score-verdict" style="background:{verdict_bg}; color:{verdict_color}; border: 1px solid {verdict_color}40; margin: 0.8rem auto 0; display:inline-block;">
                {verdict}
            </div>
            <div style="font-size:0.72rem; color:#8A94A8; margin-top:1rem; line-height:1.5;">{data.get('score_rationale','')}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_info:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Company Snapshot</div>
            <div style="font-size:1.35rem; font-weight:700; color:#E8EDF5; margin-bottom:0.3rem;">{data.get('company_name','—')}</div>
            <div style="font-size:0.88rem; color:#8A94A8; margin-bottom:1rem;">{data.get('one_liner','')}</div>
            <div class="metric-tape">
                <div class="metric-chip">
                    <div class="chip-label">Sector</div>
                    <div class="chip-value">{data.get('sector','—')}</div>
                </div>
                <div class="metric-chip">
                    <div class="chip-label">Stage</div>
                    <div class="chip-value">{data.get('stage','—')}</div>
                </div>
                <div class="metric-chip">
                    <div class="chip-label">Funding Ask</div>
                    <div class="chip-value">{data.get('funding_ask','—')}</div>
                </div>
                <div class="metric-chip">
                    <div class="chip-label">Market Size</div>
                    <div class="chip-value">{data.get('market_size','—')[:35]}...</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Score Breakdown ──
    breakdown = data.get("score_breakdown", {})
    if breakdown:
        st.markdown('<div class="card"><div class="card-title">Score Breakdown</div>', unsafe_allow_html=True)
        cols = st.columns(len(breakdown))
        labels = {
            "market_opportunity": "Market Opp.",
            "team_quality": "Team",
            "product_differentiation": "Differentiation",
            "traction_evidence": "Traction",
            "business_model_clarity": "Biz Model",
            "risk_level": "Risk Mgmt",
        }
        for i, (key, val) in enumerate(breakdown.items()):
            pct = int(val) * 10
            clr = "#00D4AA" if pct >= 70 else "#F0C040" if pct >= 50 else "#FF4D6D"
            with cols[i]:
                st.markdown(f"""
                <div style="text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace; font-size:1.4rem; font-weight:600; color:{clr};">{val}<span style="font-size:0.7rem; color:#8A94A8;">/10</span></div>
                    <div style="font-size:0.62rem; color:#8A94A8; text-transform:uppercase; letter-spacing:0.08em; margin-top:0.2rem;">{labels.get(key, key)}</div>
                    <div class="risk-bar-track" style="margin-top:0.4rem;">
                        <div class="risk-bar-fill" style="width:{pct}%; background:{clr};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Investment Thesis ──
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Investment Thesis</div>
        <div class="thesis-block">{data.get('investment_thesis','')}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Problem / Solution / Business Model ──
    st.markdown('<div class="section-heading">Fundamentals</div>', unsafe_allow_html=True)

    for label, key in [("Problem", "problem"), ("Solution", "solution"), ("Business Model", "business_model"), ("Traction", "traction"), ("Team", "team"), ("Competitive Advantage", "competitive_advantage")]:
        val = data.get(key, "Not mentioned")
        st.markdown(f"""
        <div class="info-row">
            <div class="info-key">{label}</div>
            <div class="info-val">{val}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Competitive Landscape ──
    competitors = data.get("competitors", [])
    if competitors:
        st.markdown('<div class="section-heading">Competitive Landscape</div>', unsafe_allow_html=True)
        rows = "".join([
            f'<tr><td>{c.get("name","")}</td><td style="color:#8A94A8;">{c.get("weakness","")}</td></tr>'
            for c in competitors
        ])
        company = data.get("company_name", "This company")
        st.markdown(f"""
        <div class="card">
            <table class="comp-table">
                <thead><tr><th>Competitor</th><th>Weakness vs {company}</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # ── Red / Green Flags ──
    st.markdown('<div class="section-heading">Signal Analysis</div>', unsafe_allow_html=True)

    red_flags = data.get("red_flags", [])
    green_flags = data.get("green_flags", [])

    red_items = "".join([f'<div class="flag-item"><span style="color:#FF4D6D;">✕</span>{f}</div>' for f in red_flags])
    green_items = "".join([f'<div class="flag-item"><span style="color:#00D4AA;">✓</span>{f}</div>' for f in green_flags])

    st.markdown(f"""
    <div class="flag-row">
        <div class="flag-col">
            <div class="flag-header red">⚠ Red Flags</div>
            {red_items if red_items else '<div class="flag-item" style="color:#8A94A8;">None identified</div>'}
        </div>
        <div class="flag-col">
            <div class="flag-header green">✦ Green Flags</div>
            {green_items if green_items else '<div class="flag-item" style="color:#8A94A8;">None identified</div>'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Risks ──
    risks = data.get("risks", [])
    if risks:
        st.markdown('<div class="section-heading">Risk Register</div>', unsafe_allow_html=True)
        risk_items = "".join([f'<div class="risk-item"><div class="risk-dot"></div>{r}</div>' for r in risks])
        st.markdown(f'<div class="card">{risk_items}</div>', unsafe_allow_html=True)

    # ── Export ──
    st.markdown('<div class="section-heading">Export</div>', unsafe_allow_html=True)

    # Build plain-text report
    report_lines = [
        f"DEALLENS DUE DILIGENCE REPORT",
        f"Generated: {now}",
        f"{'='*60}",
        f"",
        f"COMPANY: {data.get('company_name','—')}",
        f"ONE-LINER: {data.get('one_liner','—')}",
        f"SECTOR: {data.get('sector','—')} | STAGE: {data.get('stage','—')}",
        f"FUNDING ASK: {data.get('funding_ask','—')}",
        f"",
        f"INVESTOR SCORE: {score}/100 — {verdict}",
        f"RATIONALE: {data.get('score_rationale','')}",
        f"",
        f"INVESTMENT THESIS",
        f"{data.get('investment_thesis','')}",
        f"",
        f"PROBLEM: {data.get('problem','')}",
        f"SOLUTION: {data.get('solution','')}",
        f"BUSINESS MODEL: {data.get('business_model','')}",
        f"MARKET SIZE: {data.get('market_size','')}",
        f"TRACTION: {data.get('traction','')}",
        f"TEAM: {data.get('team','')}",
        f"COMPETITIVE ADVANTAGE: {data.get('competitive_advantage','')}",
        f"",
        f"GREEN FLAGS",
        *[f"  + {g}" for g in green_flags],
        f"",
        f"RED FLAGS",
        *[f"  ! {r}" for r in red_flags],
        f"",
        f"RISKS",
        *[f"  - {r}" for r in risks],
    ]
    report_text = "\n".join(report_lines)

    dl_col, _ = st.columns([1, 3])
    with dl_col:
        st.download_button(
            "⬇ Download Report (.txt)",
            data=report_text,
            file_name=f"deallens_{data.get('company_name','report').replace(' ','_').lower()}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
        )

    st.markdown("""
    <div style="font-size:0.7rem; color:#8A94A8; margin-top:2rem; padding-top:1rem; border-top:1px solid #1C2030;">
    DealLens is an AI-assisted due diligence tool. Output is for informational purposes only and does not constitute investment advice.
    </div>
    """, unsafe_allow_html=True)