"""Reusable UI rendering functions for DealLens."""

from datetime import datetime
import streamlit as st

from config import get_score_colors, BREAKDOWN_LABELS, FUNDAMENTALS_FIELDS, COMPARE_FIELDS, PIPELINE_STEPS, AVAILABLE_MODELS


def render_pipeline(placeholder, state):
    """Renders the staged loading pipeline. `state` is a list of 'pending'/'active'/'done'."""
    html = ""
    for label, s in zip(PIPELINE_STEPS, state):
        html += f'<div class="pipeline-step {s}"><div class="pipeline-dot"></div>{label}</div>'
    placeholder.markdown(f'<div class="card">{html}</div>', unsafe_allow_html=True)


def render_header(now_str: str):
    st.markdown(f"""
    <div class="header-bar">
        <div>
            <div class="logo-text">Deal<span>Lens</span></div>
            <div class="tagline">AI-Powered Due Diligence · Pitch Deck Intelligence</div>
        </div>
        <div class="timestamp">{now_str}</div>
    </div>
    """, unsafe_allow_html=True)


def render_empty_state():
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">🔬</div>
        <div class="empty-state-title">No analysis yet</div>
        <div class="empty-state-sub">Upload a pitch deck or paste text above to run your first due diligence report.</div>
    </div>
    """, unsafe_allow_html=True)


def render_score_card(data: dict):
    score = data.get("investor_score", 0)
    verdict = data.get("verdict", "WATCH")
    score_color, verdict_bg, verdict_color = get_score_colors(score)
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


def render_company_snapshot(data: dict):
    market_size = data.get('market_size', '—')
    market_size_short = market_size[:35] + "..." if len(market_size) > 35 else market_size
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Company Snapshot</div>
        <div style="font-size:1.35rem; font-weight:700; color:#E8EDF5; margin-bottom:0.3rem;">{data.get('company_name','—')}</div>
        <div style="font-size:0.88rem; color:#8A94A8; margin-bottom:1rem;">{data.get('one_liner','')}</div>
        <div class="metric-tape">
            <div class="metric-chip"><div class="chip-label">Sector</div><div class="chip-value">{data.get('sector','—')}</div></div>
            <div class="metric-chip"><div class="chip-label">Stage</div><div class="chip-value">{data.get('stage','—')}</div></div>
            <div class="metric-chip"><div class="chip-label">Funding Ask</div><div class="chip-value">{data.get('funding_ask','—')}</div></div>
            <div class="metric-chip"><div class="chip-label">Market Size</div><div class="chip-value">{market_size_short}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_score_breakdown(data: dict):
    breakdown = data.get("score_breakdown", {})
    if not breakdown:
        return
    st.markdown('<div class="card"><div class="card-title">Score Breakdown</div>', unsafe_allow_html=True)
    cols = st.columns(len(breakdown))
    for i, (k, v) in enumerate(breakdown.items()):
        pct = int(v) * 10
        clr = "#00D4AA" if pct >= 70 else "#F0C040" if pct >= 50 else "#FF4D6D"
        with cols[i]:
            st.markdown(f"""
            <div style="text-align:center;">
                <div style="font-family:'JetBrains Mono',monospace; font-size:1.4rem; font-weight:600; color:{clr};">{v}<span style="font-size:0.7rem; color:#8A94A8;">/10</span></div>
                <div style="font-size:0.62rem; color:#8A94A8; text-transform:uppercase; letter-spacing:0.08em; margin-top:0.2rem;">{BREAKDOWN_LABELS.get(k, k)}</div>
                <div class="risk-bar-track"><div class="risk-bar-fill" style="width:{pct}%; background:{clr};"></div></div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_thesis(data: dict):
    st.markdown(f"""
    <div class="card"><div class="card-title">Investment Thesis</div>
    <div class="thesis-block">{data.get('investment_thesis','')}</div></div>
    """, unsafe_allow_html=True)


def render_fundamentals(data: dict):
    st.markdown('<div class="section-heading">Fundamentals</div>', unsafe_allow_html=True)
    for label, key in FUNDAMENTALS_FIELDS:
        st.markdown(
            f'<div class="info-row"><div class="info-key">{label}</div>'
            f'<div class="info-val">{data.get(key, "Not mentioned")}</div></div>',
            unsafe_allow_html=True,
        )


def render_competitors(data: dict):
    competitors = data.get("competitors", [])
    if not competitors:
        return
    st.markdown('<div class="section-heading">Competitive Landscape</div>', unsafe_allow_html=True)
    rows = "".join([
        f'<tr><td>{c.get("name","")}</td><td style="color:#8A94A8;">{c.get("weakness","")}</td></tr>'
        for c in competitors
    ])
    company = data.get("company_name", "This company")
    st.markdown(
        f'<div class="card"><table class="comp-table">'
        f'<thead><tr><th>Competitor</th><th>Weakness vs {company}</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def render_signal_analysis(data: dict):
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


def render_risk_register(data: dict):
    risks = data.get("risks", [])
    if not risks:
        return
    st.markdown('<div class="section-heading">Risk Register</div>', unsafe_allow_html=True)
    risk_items = "".join([
        f'<div class="risk-item"><div class="risk-dot"></div>{r}</div>' for r in risks
    ])
    st.markdown(f'<div class="card">{risk_items}</div>', unsafe_allow_html=True)


def build_report_text(data: dict) -> str:
    """Builds the plain-text export report."""
    score = data.get("investor_score", 0)
    verdict = data.get("verdict", "WATCH")
    green_flags = data.get("green_flags", [])
    red_flags = data.get("red_flags", [])
    risks = data.get("risks", [])

    lines = [
        "DEALLENS DUE DILIGENCE REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
        "=" * 60, "",
        f"COMPANY: {data.get('company_name','—')}",
        f"ONE-LINER: {data.get('one_liner','—')}",
        f"SECTOR: {data.get('sector','—')} | STAGE: {data.get('stage','—')}",
        f"FUNDING ASK: {data.get('funding_ask','—')}", "",
        f"INVESTOR SCORE: {score}/100 — {verdict}",
        f"RATIONALE: {data.get('score_rationale','')}", "",
        "INVESTMENT THESIS",
        data.get('investment_thesis',''), "",
        f"PROBLEM: {data.get('problem','')}",
        f"SOLUTION: {data.get('solution','')}",
        f"BUSINESS MODEL: {data.get('business_model','')}",
        f"MARKET SIZE: {data.get('market_size','')}",
        f"TRACTION: {data.get('traction','')}",
        f"TEAM: {data.get('team','')}",
        f"COMPETITIVE ADVANTAGE: {data.get('competitive_advantage','')}", "",
        "GREEN FLAGS", *[f"  + {g}" for g in green_flags], "",
        "RED FLAGS", *[f"  ! {r}" for r in red_flags], "",
        "RISKS", *[f"  - {r}" for r in risks],
    ]
    return "\n".join(lines)


def render_export(data: dict, key_prefix: str):
    st.markdown('<div class="section-heading">Export</div>', unsafe_allow_html=True)
    report_text = build_report_text(data)
    dl_col, _ = st.columns([1, 3])
    with dl_col:
        st.download_button(
            "⬇ Download Report (.txt)",
            data=report_text,
            file_name=f"deallens_{data.get('company_name','report').replace(' ','_').lower()}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            key=f"dl_{key_prefix}",
        )


def render_analysis_card(data: dict, key_prefix: str = ""):
    """Renders the full analysis result block for one company."""
    col_score, col_info = st.columns([1, 3])
    with col_score:
        render_score_card(data)
    with col_info:
        render_company_snapshot(data)

    render_score_breakdown(data)
    render_thesis(data)
    render_fundamentals(data)
    render_competitors(data)
    render_signal_analysis(data)
    render_risk_register(data)
    render_export(data, key_prefix)


def render_compare_view(history: list):
    """Renders the side-by-side comparison of two analyses from history."""
    st.markdown('<div class="section-heading">Compare</div>', unsafe_allow_html=True)
    names = [h["data"].get("company_name", f"Analysis {i+1}") for i, h in enumerate(history)]

    c1, c2 = st.columns(2)
    with c1:
        sel_a = st.selectbox("Company A", range(len(names)), format_func=lambda i: names[i],
                              index=max(0, len(names) - 2), key="cmp_a")
    with c2:
        sel_b = st.selectbox("Company B", range(len(names)), format_func=lambda i: names[i],
                              index=len(names) - 1, key="cmp_b")

    da = history[sel_a]["data"]
    db = history[sel_b]["data"]
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
    for label, key in COMPARE_FIELDS:
        rows += f'<tr><td style="width:150px;">{label}</td><td>{da.get(key,"—")}</td><td>{db.get(key,"—")}</td></tr>'
    st.markdown(f"""
    <table class="comp-table">
        <thead><tr><th></th><th>{da.get('company_name','A')}</th><th>{db.get('company_name','B')}</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_history(history: list, compare_mode: bool):
    """Renders the sidebar with analysis history and the compare-mode toggle. Returns updated compare_mode."""
    st.markdown('<div class="logo-text" style="font-size:1.1rem;">Deal<span>Lens</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline" style="margin-bottom:1.5rem;">Analysis History</div>', unsafe_allow_html=True)

    if not history:
        st.markdown('<div style="font-size:0.78rem; color:#8A94A8;">No analyses yet. Run one to see it here.</div>', unsafe_allow_html=True)
    else:
        for i, entry in enumerate(reversed(history)):
            idx = len(history) - 1 - i
            d = entry["data"]
            sc = d.get("investor_score", 0)
            clr, _, _ = get_score_colors(sc)
            if st.button(f"{d.get('company_name','Untitled')}", key=f"hist_{idx}", use_container_width=True):
                st.session_state.selected_history = idx
            st.markdown(
                f'<div style="font-size:0.68rem;color:#8A94A8;margin:-0.6rem 0 0.6rem 0.2rem;'
                f'font-family:JetBrains Mono,monospace;">Score: <span style="color:{clr};font-weight:700;">{sc}</span> · {entry["timestamp"]}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    compare_mode = st.toggle("Compare Mode", value=compare_mode)
    if compare_mode:
        st.markdown('<div style="font-size:0.72rem;color:#8A94A8;">Run two analyses, then compare them side by side below.</div>', unsafe_allow_html=True)

    if history:
        st.markdown("---")
        if st.button("🗑 Clear History", use_container_width=True):
            st.session_state.confirm_clear = True

    return compare_mode


def render_model_picker():
    """Renders a dropdown to pick which Groq model to use. Returns the selected model key."""
    labels = [f"{v['label']} · {v['speed']}" for v in AVAILABLE_MODELS.values()]
    keys = list(AVAILABLE_MODELS.keys())
    selected_label = st.selectbox("Model", labels, label_visibility="collapsed")
    selected_key = keys[labels.index(selected_label)]
    desc = AVAILABLE_MODELS[selected_key]["desc"]
    st.markdown(f'<div style="font-size:0.68rem;color:#8A94A8;margin-top:-0.5rem;">{desc}</div>', unsafe_allow_html=True)
    return selected_key


def render_ocr_badge(ocr_available: bool):
    if ocr_available:
        st.markdown(
            '<div style="font-size:0.72rem; color:#00D4AA; margin-top:0.4rem;">'
            '✓ OCR fallback enabled — scanned PDFs will be attempted automatically</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="font-size:0.72rem; color:#8A94A8; margin-top:0.4rem;">'
            'ℹ OCR not installed — image-based PDFs will need Manual Text Input. '
            '<a href="#" style="color:#5BC4FF;">See setup guide</a></div>',
            unsafe_allow_html=True,
        )


def render_batch_leaderboard(results: list):
    """
    Renders a ranked leaderboard from batch analysis results.
    `results` is a list of {filename, data, error}.
    """
    st.markdown('<div class="section-heading">Batch Results — Ranked</div>', unsafe_allow_html=True)

    successful = [r for r in results if r["data"] is not None]
    failed = [r for r in results if r["data"] is None]

    successful.sort(key=lambda r: r["data"].get("investor_score", 0), reverse=True)

    if not successful:
        st.warning("No decks could be analyzed. Check the errors below.")
    else:
        rows = ""
        for rank, r in enumerate(successful, start=1):
            d = r["data"]
            score = d.get("investor_score", 0)
            clr, _, _ = get_score_colors(score)
            verdict = d.get("verdict", "WATCH")
            rank_badge = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
            rows += f"""
            <tr>
                <td style="font-weight:700;">{rank_badge}</td>
                <td>{d.get('company_name', r['filename'])}</td>
                <td>{d.get('sector','—')}</td>
                <td style="color:{clr}; font-weight:700;">{score}/100</td>
                <td>{verdict}</td>
            </tr>
            """
        st.markdown(f"""
        <div class="card">
            <table class="comp-table">
                <thead><tr><th>Rank</th><th>Company</th><th>Sector</th><th>Score</th><th>Verdict</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    if failed:
        st.markdown(f'<div style="font-size:0.78rem; color:#FF4D6D; margin-top:1rem;">⚠ {len(failed)} file(s) failed to analyze:</div>', unsafe_allow_html=True)
        for r in failed:
            st.markdown(f'<div style="font-size:0.75rem; color:#8A94A8; margin-left:1rem;">• {r["filename"]}: {r["error"]}</div>', unsafe_allow_html=True)


def render_multi_model_comparison(results: dict):
    """
    Renders side-by-side scores from multiple models analyzing the same deck.
    `results` is {model_name: (data, error)}.
    """
    st.markdown('<div class="section-heading">Multi-Model Comparison</div>', unsafe_allow_html=True)

    valid_results = {k: v for k, v in results.items() if v[0] is not None}
    if not valid_results:
        st.warning("All models failed to return valid results. Try again.")
        return

    cols = st.columns(len(valid_results))
    for i, (model_name, (data, _)) in enumerate(valid_results.items()):
        score = data.get("investor_score", 0)
        clr, bg, border = get_score_colors(score)
        model_label = AVAILABLE_MODELS.get(model_name, {}).get("label", model_name)
        with cols[i]:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:0.65rem; color:#8A94A8; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.5rem;">{model_label}</div>
                <div class="score-number" style="color:{clr}; font-size:2.2rem;">{score}</div>
                <div class="score-verdict" style="background:{bg}; color:{clr}; border:1px solid {border}40; margin-top:0.5rem; display:inline-block;">{data.get('verdict','—')}</div>
                <div style="font-size:0.72rem; color:#8A94A8; margin-top:0.8rem; line-height:1.5;">{data.get('score_rationale','')}</div>
            </div>
            """, unsafe_allow_html=True)

    scores = [d.get("investor_score", 0) for d, _ in valid_results.values()]
    if len(scores) > 1:
        spread = max(scores) - min(scores)
        agreement = "High agreement" if spread <= 5 else "Moderate agreement" if spread <= 15 else "Low agreement — models diverge significantly"
        agreement_color = "#00D4AA" if spread <= 5 else "#F0C040" if spread <= 15 else "#FF4D6D"
        st.markdown(f"""
        <div class="card" style="margin-top:1rem;">
            <div class="card-title">Model Agreement</div>
            <div style="font-size:0.85rem; color:{agreement_color}; font-weight:600;">{agreement}</div>
            <div style="font-size:0.75rem; color:#8A94A8; margin-top:0.3rem;">Score spread: {spread} points across {len(scores)} models</div>
        </div>
        """, unsafe_allow_html=True)