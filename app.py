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

st.set_page_config(
    page_title="DealLens · AI Due Diligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []  # list of {data, timestamp}
if "compare_mode" not in st.session_state:
    st.session_state.compare_mode = False

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0A0C10; color: #E8EDF5; }
.stApp { background-color: #0A0C10; }
.main .block-container { padding: 2rem 2.5rem; max-width: 1200px; }

section[data-testid="stSidebar"] {
    background-color: #0D0F14;
    border-right: 1px solid #1C2030;
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }

.header-bar {
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid #1C2030; padding-bottom: 1.2rem; margin-bottom: 2rem;
}
.logo-text { font-family: 'JetBrains Mono', monospace; font-size: 1.5rem; font-weight: 600; letter-spacing: -0.5px; color: #E8EDF5; }
.logo-text span { color: #00D4AA; }
.tagline { font-size: 0.72rem; color: #8A94A8; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 500; }
.timestamp { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #8A94A8; letter-spacing: 0.05em; }

.card { background: #111318; border: 1px solid #1C2030; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; }
.card-title {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase;
    color: #8A94A8; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;
}
.card-title::before { content: ''; display: inline-block; width: 3px; height: 12px; background: #00D4AA; border-radius: 2px; }

.score-label { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #8A94A8; letter-spacing: 0.1em; text-transform: uppercase; }
.score-number { font-family: 'JetBrains Mono', monospace; font-size: 3rem; font-weight: 600; line-height: 1; }
.score-verdict {
    font-size: 0.78rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
    padding: 0.3rem 0.8rem; border-radius: 20px; margin-top: 0.3rem;
}

.metric-tape { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.5rem; }
.metric-chip { background: #1C2030; border: 1px solid #2A3050; border-radius: 6px; padding: 0.6rem 1rem; flex: 1; min-width: 130px; transition: border-color 0.15s; }
.metric-chip:hover { border-color: #00D4AA; }
.chip-label { font-size: 0.62rem; color: #8A94A8; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 500; }
.chip-value { font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; font-weight: 600; color: #E8EDF5; margin-top: 0.2rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.risk-bar-track { background: #1C2030; border-radius: 4px; height: 6px; width: 100%; overflow: hidden; margin-top: 0.4rem; }
.risk-bar-fill { height: 100%; border-radius: 4px; transition: width 1s cubic-bezier(0.22, 1, 0.36, 1); }

.section-heading {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase;
    color: #8A94A8; margin: 1.5rem 0 0.8rem; display: flex; align-items: center; gap: 0.6rem;
}
.section-heading::after { content: ''; flex: 1; height: 1px; background: #1C2030; }

.info-row { display: flex; gap: 0; border: 1px solid #1C2030; border-radius: 6px; overflow: hidden; margin-bottom: 0.5rem; transition: border-color 0.15s; }
.info-row:hover { border-color: #2A3050; }
.info-key {
    background: #1C2030; padding: 0.65rem 1rem; font-size: 0.7rem; font-weight: 600; color: #8A94A8;
    letter-spacing: 0.08em; text-transform: uppercase; width: 180px; flex-shrink: 0;
    display: flex; align-items: flex-start; padding-top: 0.75rem;
}
.info-val { padding: 0.65rem 1.1rem; font-size: 0.84rem; color: #E8EDF5; flex: 1; line-height: 1.55; }

.flag-row { display: flex; gap: 1rem; margin-top: 0.5rem; }
.flag-col { flex: 1; background: #111318; border: 1px solid #1C2030; border-radius: 8px; padding: 1rem 1.2rem; }
.flag-header { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.8rem; }
.flag-header.red { color: #FF4D6D; }
.flag-header.green { color: #00D4AA; }
.flag-item { display: flex; gap: 0.5rem; font-size: 0.8rem; color: #C8D0E0; margin-bottom: 0.45rem; line-height: 1.45; }

.comp-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.comp-table th { font-size: 0.62rem; letter-spacing: 0.1em; text-transform: uppercase; color: #8A94A8; font-weight: 600; padding: 0.6rem 1rem; border-bottom: 2px solid #1C2030; text-align: left; }
.comp-table td { padding: 0.65rem 1rem; border-bottom: 1px solid #1C2030; color: #E8EDF5; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; }
.comp-table tr:last-child td { border-bottom: none; }

.thesis-block {
    border-left: 3px solid #00D4AA; background: #0E1118; border-radius: 0 6px 6px 0;
    padding: 1rem 1.4rem; font-size: 0.9rem; color: #C8D0E0; line-height: 1.7; font-style: italic; margin-top: 0.5rem;
}

.history-item {
    background: #111318; border: 1px solid #1C2030; border-radius: 6px;
    padding: 0.7rem 0.9rem; margin-bottom: 0.5rem; cursor: pointer; transition: all 0.15s;
}
.history-item:hover { border-color: #00D4AA; }
.history-name { font-size: 0.82rem; font-weight: 600; color: #E8EDF5; }
.history-meta { font-size: 0.68rem; color: #8A94A8; margin-top: 0.15rem; font-family: 'JetBrains Mono', monospace; }

.pipeline-step {
    display: flex; align-items: center; gap: 0.6rem; padding: 0.5rem 0;
    font-size: 0.8rem; color: #8A94A8; font-family: 'JetBrains Mono', monospace;
}
.pipeline-step.done { color: #00D4AA; }
.pipeline-step.active { color: #E8EDF5; }
.pipeline-dot { width: 8px; height: 8px; border-radius: 50%; background: #1C2030; flex-shrink: 0; }
.pipeline-step.done .pipeline-dot { background: #00D4AA; }
.pipeline-step.active .pipeline-dot { background: #F0C040; animation: pulse 1s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

.empty-state { text-align: center; padding: 4rem 2rem; color: #8A94A8; }
.empty-state-icon { font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.5; }
.empty-state-title { font-size: 1rem; font-weight: 600; color: #E8EDF5; margin-bottom: 0.4rem; }
.empty-state-sub { font-size: 0.82rem; }

.vs-badge {
    display: inline-block; background: #1C2030; border: 1px solid #2A3050; border-radius: 20px;
    padding: 0.3rem 0.9rem; font-size: 0.7rem; font-weight: 700; color: #00D4AA;
    font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05em;
}

.stRadio > div { gap: 0.5rem !important; }
.stRadio label {
    background: #111318 !important; border: 1px solid #1C2030 !important; border-radius: 6px !important;
    padding: 0.5rem 1rem !important; color: #E8EDF5 !important; font-size: 0.84rem !important; cursor: pointer;
}
.stRadio label:hover { border-color: #00D4AA !important; }
div[data-testid="stFileUploader"] { background: #111318; border: 1px dashed #2A3050; border-radius: 8px; padding: 1.5rem; }
.stTextArea textarea {
    background: #111318 !important; border: 1px solid #1C2030 !important; color: #E8EDF5 !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 0.82rem !important; border-radius: 6px !important;
}
.stTextArea textarea:focus { border-color: #00D4AA !important; box-shadow: 0 0 0 2px rgba(0,212,170,0.1) !important; }

.stButton > button {
    background: #00D4AA !important; color: #0A0C10 !important; font-weight: 700 !important; font-size: 0.85rem !important;
    letter-spacing: 0.06em !important; border: none !important; border-radius: 6px !important;
    padding: 0.65rem 2rem !important; width: 100%; transition: transform 0.1s !important;
}
.stButton > button:hover { opacity: 0.85 !important; transform: translateY(-1px); }

.stDownloadButton > button {
    background: #1C2030 !important; color: #E8EDF5 !important; font-weight: 600 !important; font-size: 0.78rem !important;
    border: 1px solid #2A3050 !important; border-radius: 6px !important; width: 100%;
}
.stDownloadButton > button:hover { border-color: #00D4AA !important; }

.stSpinner > div { border-color: #00D4AA transparent transparent transparent !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.viewerBadge_container__1QSob { display: none; }
</style>
""", unsafe_allow_html=True)

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
  "verdict": "STRONG PASS | PASS | WATCH | SOFT PASS | REJECT"
}}

Score investor_score 0–100 (≥80 = STRONG PASS, 65–79 = PASS, 50–64 = WATCH, 35–49 = SOFT PASS, <35 = REJECT).
score_breakdown values are each out of 10.

Pitch deck text:
{text}
"""


def get_score_colors(score):
    if score >= 80:
        return "#00D4AA", "rgba(0,212,170,0.12)", "#00D4AA"
    elif score >= 65:
        return "#5BC4FF", "rgba(91,196,255,0.12)", "#5BC4FF"
    elif score >= 50:
        return "#F0C040", "rgba(240,192,64,0.12)", "#F0C040"
    else:
        return "#FF4D6D", "rgba(255,77,109,0.12)", "#FF4D6D"


def run_analysis(text_input, progress_placeholder):
    steps = ["Reading document", "Extracting key metrics", "Scoring investment signal", "Finalizing report"]
    state = ["pending"] * len(steps)

    def render():
        html = ""
        for label, s in zip(steps, state):
            html += f'<div class="pipeline-step {s}"><div class="pipeline-dot"></div>{label}</div>'
        progress_placeholder.markdown(f'<div class="card">{html}</div>', unsafe_allow_html=True)

    state[0] = "active"; render(); time.sleep(0.4)
    state[0] = "done"; state[1] = "active"; render(); time.sleep(0.3)

    try:
        model = ChatGroq(model="openai/gpt-oss-20b", temperature=0.3)
        prompt = PromptTemplate.from_template(ANALYSIS_PROMPT)
        chain = prompt | model
        state[1] = "done"; state[2] = "active"; render()
        response = chain.invoke({"text": text_input[:9000]})
        raw_json = response.content.strip()
        raw_json = re.sub(r'^```json\s*', '', raw_json)
        raw_json = re.sub(r'^```\s*', '', raw_json)
        raw_json = re.sub(r'\s*```$', '', raw_json)
        data = json.loads(raw_json)
        state[2] = "done"; state[3] = "active"; render(); time.sleep(0.3)
        state[3] = "done"; render(); time.sleep(0.2)
        progress_placeholder.empty()
        return data
    except json.JSONDecodeError:
        progress_placeholder.empty()
        st.error("Model returned non-JSON. Try again — free tier occasionally truncates responses.")
        return None
    except Exception as e:
        progress_placeholder.empty()
        st.error(f"Analysis error: {e}")
        return None


def render_analysis_card(data, key_prefix=""):
    score = data.get("investor_score", 0)
    verdict = data.get("verdict", "WATCH")
    score_color, verdict_bg, verdict_color = get_score_colors(score)

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
                <div class="metric-chip"><div class="chip-label">Sector</div><div class="chip-value">{data.get('sector','—')}</div></div>
                <div class="metric-chip"><div class="chip-label">Stage</div><div class="chip-value">{data.get('stage','—')}</div></div>
                <div class="metric-chip"><div class="chip-label">Funding Ask</div><div class="chip-value">{data.get('funding_ask','—')}</div></div>
                <div class="metric-chip"><div class="chip-label">Market Size</div><div class="chip-value">{data.get('market_size','—')[:35]}...</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    breakdown = data.get("score_breakdown", {})
    if breakdown:
        st.markdown('<div class="card"><div class="card-title">Score Breakdown</div>', unsafe_allow_html=True)
        cols = st.columns(len(breakdown))
        labels = {
            "market_opportunity": "Market Opp.", "team_quality": "Team", "product_differentiation": "Differentiation",
            "traction_evidence": "Traction", "business_model_clarity": "Biz Model", "risk_level": "Risk Mgmt",
        }
        for i, (k, v) in enumerate(breakdown.items()):
            pct = int(v) * 10
            clr = "#00D4AA" if pct >= 70 else "#F0C040" if pct >= 50 else "#FF4D6D"
            with cols[i]:
                st.markdown(f"""
                <div style="text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace; font-size:1.4rem; font-weight:600; color:{clr};">{v}<span style="font-size:0.7rem; color:#8A94A8;">/10</span></div>
                    <div style="font-size:0.62rem; color:#8A94A8; text-transform:uppercase; letter-spacing:0.08em; margin-top:0.2rem;">{labels.get(k, k)}</div>
                    <div class="risk-bar-track"><div class="risk-bar-fill" style="width:{pct}%; background:{clr};"></div></div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card"><div class="card-title">Investment Thesis</div>
    <div class="thesis-block">{data.get('investment_thesis','')}</div></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Fundamentals</div>', unsafe_allow_html=True)
    for label, key in [("Problem", "problem"), ("Solution", "solution"), ("Business Model", "business_model"),
                        ("Traction", "traction"), ("Team", "team"), ("Competitive Advantage", "competitive_advantage")]:
        st.markdown(f'<div class="info-row"><div class="info-key">{label}</div><div class="info-val">{data.get(key, "Not mentioned")}</div></div>', unsafe_allow_html=True)

    competitors = data.get("competitors", [])
    if competitors:
        st.markdown('<div class="section-heading">Competitive Landscape</div>', unsafe_allow_html=True)
        rows = "".join([f'<tr><td>{c.get("name","")}</td><td style="color:#8A94A8;">{c.get("weakness","")}</td></tr>' for c in competitors])
        company = data.get("company_name", "This company")
        st.markdown(f'<div class="card"><table class="comp-table"><thead><tr><th>Competitor</th><th>Weakness vs {company}</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Signal Analysis</div>', unsafe_allow_html=True)
    red_flags = data.get("red_flags", [])
    green_flags = data.get("green_flags", [])
    red_items = "".join([f'<div class="flag-item"><span style="color:#FF4D6D;">✕</span> {f}</div>' for f in red_flags])
    green_items = "".join([f'<div class="flag-item"><span style="color:#00D4AA;">✓</span> {f}</div>' for f in green_flags])
    st.markdown(f"""
    <div class="flag-row">
        <div class="flag-col"><div class="flag-header red">⚠ Red Flags</div>{red_items or '<div class="flag-item" style="color:#8A94A8;">None identified</div>'}</div>
        <div class="flag-col"><div class="flag-header green">✦ Green Flags</div>{green_items or '<div class="flag-item" style="color:#8A94A8;">None identified</div>'}</div>
    </div>
    """, unsafe_allow_html=True)

    risks = data.get("risks", [])
    if risks:
        st.markdown('<div class="section-heading">Risk Register</div>', unsafe_allow_html=True)
        risk_items = "".join([f'<div style="display:flex;gap:0.6rem;padding:0.6rem 0;border-bottom:1px solid #1C2030;font-size:0.84rem;"><div style="width:7px;height:7px;border-radius:50%;background:#FF4D6D;margin-top:0.45rem;flex-shrink:0;"></div>{r}</div>' for r in risks])
        st.markdown(f'<div class="card">{risk_items}</div>', unsafe_allow_html=True)

    report_lines = [
        "DEALLENS DUE DILIGENCE REPORT", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}", "="*60, "",
        f"COMPANY: {data.get('company_name','—')}", f"ONE-LINER: {data.get('one_liner','—')}",
        f"SECTOR: {data.get('sector','—')} | STAGE: {data.get('stage','—')}", f"FUNDING ASK: {data.get('funding_ask','—')}", "",
        f"INVESTOR SCORE: {score}/100 — {verdict}", f"RATIONALE: {data.get('score_rationale','')}", "",
        "INVESTMENT THESIS", data.get('investment_thesis',''), "",
        f"PROBLEM: {data.get('problem','')}", f"SOLUTION: {data.get('solution','')}", f"BUSINESS MODEL: {data.get('business_model','')}",
        f"MARKET SIZE: {data.get('market_size','')}", f"TRACTION: {data.get('traction','')}", f"TEAM: {data.get('team','')}",
        f"COMPETITIVE ADVANTAGE: {data.get('competitive_advantage','')}", "",
        "GREEN FLAGS", *[f"  + {g}" for g in green_flags], "",
        "RED FLAGS", *[f"  ! {r}" for r in red_flags], "",
        "RISKS", *[f"  - {r}" for r in risks],
    ]
    st.markdown('<div class="section-heading">Export</div>', unsafe_allow_html=True)
    dl_col, _ = st.columns([1, 3])
    with dl_col:
        st.download_button("⬇ Download Report (.txt)", data="\n".join(report_lines),
            file_name=f"deallens_{data.get('company_name','report').replace(' ','_').lower()}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain", key=f"dl_{key_prefix}")


# ─────────────────────────────────────────────────────────────
# SIDEBAR — History
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-text" style="font-size:1.1rem;">Deal<span>Lens</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline" style="margin-bottom:1.5rem;">Analysis History</div>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown('<div style="font-size:0.78rem; color:#8A94A8;">No analyses yet. Run one to see it here.</div>', unsafe_allow_html=True)
    else:
        for i, entry in enumerate(reversed(st.session_state.history)):
            idx = len(st.session_state.history) - 1 - i
            d = entry["data"]
            sc = d.get("investor_score", 0)
            clr, _, _ = get_score_colors(sc)
            if st.button(f"{d.get('company_name','Untitled')}", key=f"hist_{idx}", use_container_width=True):
                st.session_state.selected_history = idx
            st.markdown(f'<div style="font-size:0.68rem;color:#8A94A8;margin:-0.6rem 0 0.6rem 0.2rem;font-family:JetBrains Mono,monospace;">Score: <span style="color:{clr};font-weight:700;">{sc}</span> · {entry["timestamp"]}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.session_state.compare_mode = st.toggle("Compare Mode", value=st.session_state.compare_mode)
    if st.session_state.compare_mode:
        st.markdown('<div style="font-size:0.72rem;color:#8A94A8;">Run two analyses, then compare them side by side below.</div>', unsafe_allow_html=True)

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
    analysis_mode = st.radio("Source", ["📄 PDF Upload", "✏️ Manual Text Input"], horizontal=True, label_visibility="collapsed")

pdf_file = None
manual_text = ""

if analysis_mode == "📄 PDF Upload":
    pdf_file = st.file_uploader("Drop pitch deck PDF", type=["pdf"], label_visibility="collapsed")
    st.markdown("""
    <div style="font-size:0.75rem; color:#8A94A8; margin-top:0.5rem;">
    ⚠️ Image-based PDFs (scanned decks) won't extract text — use Manual Text Input instead.<br>
    💡 To get text: open PDF → Ctrl+A → Ctrl+C → paste below in Manual mode.
    </div>
    """, unsafe_allow_html=True)
else:
    manual_text = st.text_area("Paste pitch deck text", height=220,
        placeholder="Paste the full text of the pitch deck here — problem, solution, market size, traction, team, ask...",
        label_visibility="collapsed")

has_input = (pdf_file is not None) or (manual_text.strip() != "")
analyze_btn = st.button("🔬 Run Due Diligence Analysis") if has_input else False
if not has_input:
    st.markdown('<div style="font-size:0.8rem;color:#8A94A8;margin-top:0.5rem;">Provide a pitch deck to begin.</div>', unsafe_allow_html=True)

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

    progress_placeholder = st.empty()
    result = run_analysis(pitch_text, progress_placeholder)

    if result:
        st.session_state.history.append({"data": result, "timestamp": datetime.now().strftime("%H:%M")})
        st.session_state.selected_history = len(st.session_state.history) - 1
        st.rerun()

# ─────────────────────────────────────────────────────────────
# DISPLAY: Compare mode or single result
# ─────────────────────────────────────────────────────────────
if st.session_state.compare_mode and len(st.session_state.history) >= 2:
    st.markdown('<div class="section-heading">Compare</div>', unsafe_allow_html=True)
    names = [h["data"].get("company_name", f"Analysis {i+1}") for i, h in enumerate(st.session_state.history)]
    c1, c2 = st.columns(2)
    with c1:
        sel_a = st.selectbox("Company A", range(len(names)), format_func=lambda i: names[i], index=max(0, len(names)-2), key="cmp_a")
    with c2:
        sel_b = st.selectbox("Company B", range(len(names)), format_func=lambda i: names[i], index=len(names)-1, key="cmp_b")

    if sel_a is not None and sel_b is not None:
        da = st.session_state.history[sel_a]["data"]
        db = st.session_state.history[sel_b]["data"]
        sa, sb = da.get("investor_score", 0), db.get("investor_score", 0)
        ca, _, _ = get_score_colors(sa)
        cb, _, _ = get_score_colors(sb)

        colA, colVs, colB = st.columns([2, 1, 2])
        with colA:
            st.markdown(f'<div class="card" style="text-align:center;"><div class="score-label">{da.get("company_name","—")}</div><div class="score-number" style="color:{ca};">{sa}</div></div>', unsafe_allow_html=True)
        with colVs:
            st.markdown('<div style="text-align:center; padding-top:2.2rem;"><span class="vs-badge">VS</span></div>', unsafe_allow_html=True)
        with colB:
            st.markdown(f'<div class="card" style="text-align:center;"><div class="score-label">{db.get("company_name","—")}</div><div class="score-number" style="color:{cb};">{sb}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-title">Side-by-Side Breakdown</div>', unsafe_allow_html=True)
        rows = ""
        for label, key in [("Sector", "sector"), ("Stage", "stage"), ("Funding Ask", "funding_ask"), ("Business Model", "business_model"), ("Traction", "traction")]:
            rows += f'<tr><td style="width:150px;">{label}</td><td>{da.get(key,"—")}</td><td>{db.get(key,"—")}</td></tr>'
        st.markdown(f"""
        <table class="comp-table">
            <thead><tr><th></th><th>{da.get('company_name','A')}</th><th>{db.get('company_name','B')}</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)
elif st.session_state.history:
    idx = st.session_state.get("selected_history", len(st.session_state.history) - 1)
    idx = min(idx, len(st.session_state.history) - 1)
    st.markdown('<div class="section-heading">Analysis Results</div>', unsafe_allow_html=True)
    render_analysis_card(st.session_state.history[idx]["data"], key_prefix=str(idx))
else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">🔬</div>
        <div class="empty-state-title">No analysis yet</div>
        <div class="empty-state-sub">Upload a pitch deck or paste text above to run your first due diligence report.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="font-size:0.7rem; color:#8A94A8; margin-top:2rem; padding-top:1rem; border-top:1px solid #1C2030;">
DealLens is an AI-assisted due diligence tool. Output is for informational purposes only and does not constitute investment advice.
</div>
""", unsafe_allow_html=True)