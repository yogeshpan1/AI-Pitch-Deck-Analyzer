import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

from styles import CUSTOM_CSS
from ai_engine import extract_pdf_text, analyze

load_dotenv()
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

st.set_page_config(page_title="DealLens · AI Due Diligence", page_icon="🔬", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

MODELS = {
    "openai/gpt-oss-20b": "GPT-OSS 20B · Fast",
    "openai/gpt-oss-120b": "GPT-OSS 120B · Deep",
    "llama-3.3-70b-versatile": "Llama 3.3 70B",
}
MIN_TEXT_LENGTH = 80
MIN_PDF_TEXT_LENGTH = 100

if "results" not in st.session_state:
    st.session_state.results = []


def score_colors(score):
    if score >= 80:
        return "#00D4AA", "rgba(0,212,170,0.12)"
    if score >= 65:
        return "#5BC4FF", "rgba(91,196,255,0.12)"
    if score >= 50:
        return "#F0C040", "rgba(240,192,64,0.12)"
    return "#FF4D6D", "rgba(255,77,109,0.12)"


def render_result(data):
    score = data.get("investor_score", 0)
    color, bg = score_colors(score)

    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown(f"""
        <div class="card" style="text-align:center; padding:2rem 1rem;">
            <div class="score-label">Investor Score</div>
            <div class="score-number" style="color:{color};">{score}</div>
            <div style="font-size:0.65rem;color:#8A94A8;">/100</div>
            <div class="score-verdict" style="background:{bg};color:{color};border:1px solid {color}40;margin-top:0.8rem;display:inline-block;">
                {data.get('verdict','WATCH')}
            </div>
            <div style="font-size:0.72rem;color:#8A94A8;margin-top:1rem;">{data.get('score_rationale','')}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        market = data.get('market_size', '—')
        if len(market) > 40:
            market = market[:40] + "..."
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Company Snapshot</div>
            <div style="font-size:1.3rem;font-weight:700;">{data.get('company_name','—')}</div>
            <div style="font-size:0.85rem;color:#8A94A8;margin-bottom:1rem;">{data.get('one_liner','')}</div>
            <div class="metric-tape">
                <div class="metric-chip"><div class="chip-label">Sector</div><div class="chip-value">{data.get('sector','—')}</div></div>
                <div class="metric-chip"><div class="chip-label">Stage</div><div class="chip-value">{data.get('stage','—')}</div></div>
                <div class="metric-chip"><div class="chip-label">Funding Ask</div><div class="chip-value">{data.get('funding_ask','—')}</div></div>
                <div class="metric-chip"><div class="chip-label">Market Size</div><div class="chip-value">{market}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    breakdown = data.get("score_breakdown", {})
    if breakdown:
        st.markdown('<div class="card"><div class="card-title">Score Breakdown</div>', unsafe_allow_html=True)
        cols = st.columns(len(breakdown))
        for col, (label, value) in zip(cols, breakdown.items()):
            pct = int(value) * 10
            c = "#00D4AA" if pct >= 70 else "#F0C040" if pct >= 50 else "#FF4D6D"
            with col:
                st.markdown(f"""
                <div style="text-align:center;">
                    <div style="font-family:monospace;font-size:1.3rem;font-weight:600;color:{c};">{value}<span style="font-size:0.7rem;color:#8A94A8;">/10</span></div>
                    <div style="font-size:0.6rem;color:#8A94A8;text-transform:uppercase;margin-top:0.2rem;">{label.replace('_',' ')}</div>
                    <div class="risk-bar-track"><div class="risk-bar-fill" style="width:{pct}%;background:{c};"></div></div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
        <div class="card-title">Investment Thesis</div>
        <div class="thesis-block">{data.get('investment_thesis','')}</div>
    </div>
    """, unsafe_allow_html=True)

    fields = [
        ("Problem", "problem"), ("Solution", "solution"), ("Business Model", "business_model"),
        ("Traction", "traction"), ("Team", "team"), ("Competitive Advantage", "competitive_advantage"),
    ]
    for label, key in fields:
        st.markdown(f"""
        <div class="info-row">
            <div class="info-key">{label}</div>
            <div class="info-val">{data.get(key, "Not mentioned")}</div>
        </div>
        """, unsafe_allow_html=True)

    red = data.get("red_flags", [])
    green = data.get("green_flags", [])
    red_html = "".join(f'<div class="flag-item">✕ {f}</div>' for f in red) or '<div class="flag-item" style="color:#8A94A8;">None</div>'
    green_html = "".join(f'<div class="flag-item">✓ {f}</div>' for f in green) or '<div class="flag-item" style="color:#8A94A8;">None</div>'
    st.markdown(f"""
    <div class="flag-row">
        <div class="flag-col"><div class="flag-header red">⚠ Red Flags</div>{red_html}</div>
        <div class="flag-col"><div class="flag-header green">✦ Green Flags</div>{green_html}</div>
    </div>
    """, unsafe_allow_html=True)

    risks = data.get("risks", [])
    if risks:
        risk_html = "".join(f'<div class="risk-item"><div class="risk-dot"></div>{r}</div>' for r in risks)
        st.markdown(f'<div class="card">{risk_html}</div>', unsafe_allow_html=True)


def run_single_analysis_tab():
    mode_col, model_col = st.columns([2, 1])
    with mode_col:
        mode = st.radio("Source", ["📄 PDF Upload", "✏️ Manual Text"], horizontal=True, label_visibility="collapsed")
    with model_col:
        model_choice = st.selectbox("Model", list(MODELS.keys()), format_func=lambda k: MODELS[k], label_visibility="collapsed")

    pdf_file, manual_text = None, ""
    if mode == "📄 PDF Upload":
        pdf_file = st.file_uploader("PDF", type=["pdf"], label_visibility="collapsed")
        st.caption("⚠️ Scanned/image-based PDFs won't extract text. If that happens, open the PDF → Ctrl+A → Ctrl+C → paste in Manual mode.")
    else:
        manual_text = st.text_area("Text", height=200, placeholder="Paste pitch deck text here...", label_visibility="collapsed")

    has_input = pdf_file is not None or manual_text.strip() != ""

    if st.button("🔬 Run Analysis", disabled=not has_input):
        if pdf_file:
            with open("temp.pdf", "wb") as f:
                f.write(pdf_file.getbuffer())
            text = extract_pdf_text("temp.pdf")
            if len(text) < MIN_PDF_TEXT_LENGTH:
                st.warning("This PDF appears image-based — no text extracted. Switch to Manual Text mode.")
                st.stop()
        else:
            text = manual_text.strip()

        if len(text) < MIN_TEXT_LENGTH:
            st.warning("Not enough text to analyze.")
            st.stop()

        with st.spinner("Analyzing..."):
            data, error = analyze(text, model_choice)

        if error:
            st.error(error)
        else:
            st.session_state.results.append(data)
            st.rerun()

    if not st.session_state.results:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🔬</div>
            <div class="empty-state-title">No analysis yet</div>
            <div class="empty-state-sub">Upload a pitch deck or paste text above.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown('<div class="section-heading">Latest Result</div>', unsafe_allow_html=True)
    render_result(st.session_state.results[-1])

    earlier = st.session_state.results[:-1]
    if earlier:
        with st.expander(f"View {len(earlier)} earlier result(s) this session"):
            for r in reversed(earlier):
                st.markdown(f"**{r.get('company_name','—')}** — Score: {r.get('investor_score',0)}/100 ({r.get('verdict','')})")


def run_compare_tab():
    st.caption("Run the same pitch text through multiple models to see how much they agree. Low agreement is a signal to double-check manually rather than trust one AI's score.")

    text = st.text_area("Pitch text", height=180, placeholder="Paste pitch deck text to compare across models...", label_visibility="collapsed")
    chosen = st.multiselect("Models", list(MODELS.keys()), default=list(MODELS.keys())[:2], format_func=lambda k: MODELS[k])

    if not st.button("🔀 Compare Models", disabled=not (text.strip() and len(chosen) >= 2)):
        return

    results = {}
    with st.spinner("Running models..."):
        for model in chosen:
            data, _ = analyze(text.strip(), model)
            if data:
                results[model] = data

    if not results:
        st.error("All models failed. Try again.")
        return

    cols = st.columns(len(results))
    for col, (model, data) in zip(cols, results.items()):
        score = data.get("investor_score", 0)
        color, bg = score_colors(score)
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:0.65rem;color:#8A94A8;text-transform:uppercase;">{MODELS[model]}</div>
                <div class="score-number" style="color:{color};font-size:2.2rem;">{score}</div>
                <div class="score-verdict" style="background:{bg};color:{color};border:1px solid {color}40;margin-top:0.5rem;display:inline-block;">{data.get('verdict','—')}</div>
                <div style="font-size:0.72rem;color:#8A94A8;margin-top:0.8rem;">{data.get('score_rationale','')}</div>
            </div>
            """, unsafe_allow_html=True)

    scores = [d.get("investor_score", 0) for d in results.values()]
    if len(scores) > 1:
        spread = max(scores) - min(scores)
        label = "High agreement" if spread <= 5 else "Moderate agreement" if spread <= 15 else "Low agreement — models diverge"
        color = "#00D4AA" if spread <= 5 else "#F0C040" if spread <= 15 else "#FF4D6D"
        st.markdown(f"""
        <div class="card" style="margin-top:1rem;">
            <b style="color:{color};">{label}</b>
            <div style="font-size:0.75rem;color:#8A94A8;margin-top:0.3rem;">Score spread: {spread} points</div>
        </div>
        """, unsafe_allow_html=True)


# ── Page ──
st.markdown(f"""
<div class="header-bar">
    <div>
        <div class="logo-text">Deal<span>Lens</span></div>
        <div class="tagline">AI-Powered Due Diligence · Pitch Deck Intelligence</div>
    </div>
    <div class="timestamp">{datetime.now().strftime('%Y-%m-%d  %H:%M UTC')}</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📄 Analyze", "🔀 Multi-Model Compare"])
with tab1:
    run_single_analysis_tab()
with tab2:
    run_compare_tab()

st.markdown('<div style="font-size:0.7rem;color:#8A94A8;margin-top:2rem;padding-top:1rem;border-top:1px solid #1C2030;">DealLens is an AI-assisted due diligence tool. Not investment advice.</div>', unsafe_allow_html=True)