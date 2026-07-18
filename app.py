"""
DealLens — AI-Powered Pitch Deck Due Diligence Tool

Entry point. Handles page setup, input collection, and orchestrates
the AI engine + UI components. All heavy lifting lives in:
  - config.py         constants and thresholds
  - styles.py         CSS
  - prompts.py         the AI prompt template
  - ai_engine.py        PDF extraction + Groq call (single/batch/multi-model)
  - ocr_engine.py       OCR fallback for scanned PDFs
  - database.py         SQLite persistence for analysis history
  - ui_components.py     all render_* functions
"""

import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from styles import CUSTOM_CSS
from config import MIN_TEXT_LENGTH, MIN_PDF_TEXT_LENGTH, MAX_BATCH_FILES, GROQ_MODEL, AVAILABLE_MODELS
from ai_engine import (
    extract_pdf_text,
    extract_pdf_text_with_ocr_fallback,
    run_analysis,
    run_analysis_silent,
    run_multi_model_analysis,
)
from ocr_engine import is_ocr_available
import database as db
from ui_components import (
    render_pipeline,
    render_header,
    render_empty_state,
    render_analysis_card,
    render_compare_view,
    render_sidebar_history,
    render_model_picker,
    render_ocr_badge,
    render_batch_leaderboard,
    render_multi_model_comparison,
)

st.set_page_config(
    page_title="DealLens · AI Due Diligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

db.init_db()
OCR_READY = is_ocr_available()

# ── Session state ──
if "compare_mode" not in st.session_state:
    st.session_state.compare_mode = False
if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False

history = db.load_all_analyses()

# ── Sidebar ──
with st.sidebar:
    st.session_state.compare_mode = render_sidebar_history(history, st.session_state.compare_mode)

    if st.session_state.confirm_clear:
        st.warning("Delete all saved analyses? This can't be undone.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, clear", use_container_width=True):
                db.clear_all()
                st.session_state.confirm_clear = False
                st.rerun()
        with c2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.confirm_clear = False
                st.rerun()

# ── Header ──
render_header(datetime.now().strftime("%Y-%m-%d  %H:%M UTC"))

# ── Mode tabs ──
tab_single, tab_batch, tab_multimodel = st.tabs(["📄 Single Analysis", "📚 Batch Mode", "🔀 Multi-Model Compare"])

# ═════════════════════════════════════════════════════════════
# TAB 1 — Single Analysis
# ═════════════════════════════════════════════════════════════
with tab_single:
    st.markdown('<div class="section-heading">Input</div>', unsafe_allow_html=True)

    mode_col, model_col = st.columns([2, 1])
    with mode_col:
        analysis_mode = st.radio(
            "Source", ["📄 PDF Upload", "✏️ Manual Text Input"],
            horizontal=True, label_visibility="collapsed", key="single_mode",
        )
    with model_col:
        selected_model = render_model_picker()

    pdf_file = None
    manual_text = ""

    if analysis_mode == "📄 PDF Upload":
        pdf_file = st.file_uploader("Drop pitch deck PDF", type=["pdf"], label_visibility="collapsed", key="single_pdf")
        render_ocr_badge(OCR_READY)
        st.markdown("""
        <div style="font-size:0.75rem; color:#8A94A8; margin-top:0.5rem;">
        💡 If OCR isn't available and the deck is scanned: open PDF → Ctrl+A → Ctrl+C → paste in Manual mode.
        </div>
        """, unsafe_allow_html=True)
    else:
        manual_text = st.text_area(
            "Paste pitch deck text", height=220,
            placeholder="Paste the full text of the pitch deck here — problem, solution, market size, traction, team, ask...",
            label_visibility="collapsed", key="single_text",
        )

    has_input = (pdf_file is not None) or (manual_text.strip() != "")
    analyze_btn = st.button("🔬 Run Due Diligence Analysis", key="single_run") if has_input else False
    if not has_input:
        st.markdown('<div style="font-size:0.8rem;color:#8A94A8;margin-top:0.5rem;">Provide a pitch deck to begin.</div>', unsafe_allow_html=True)

    if analyze_btn:
        pitch_text = ""

        if pdf_file is not None:
            with open("temp_deck.pdf", "wb") as f:
                f.write(pdf_file.getbuffer())
            try:
                pitch_text, method = extract_pdf_text_with_ocr_fallback("temp_deck.pdf", MIN_PDF_TEXT_LENGTH)
                if not pitch_text:
                    st.warning("⚠️ This PDF appears image-based and OCR couldn't extract usable text. Switch to Manual Text Input.")
                    st.stop()
                elif method == "ocr":
                    st.info("📷 Text extracted via OCR (scanned PDF detected).")
            except Exception as e:
                st.error(f"PDF read error: {e}")
                st.stop()
        else:
            pitch_text = manual_text.strip()

        if len(pitch_text) < MIN_TEXT_LENGTH:
            st.warning("Not enough text to analyze. Please provide more content.")
            st.stop()

        progress_placeholder = st.empty()
        result, error = run_analysis(pitch_text, progress_placeholder, render_pipeline, model_name=selected_model)

        if error:
            st.error(error)
        elif result:
            new_id = db.save_analysis(result, model_used=selected_model)
            st.session_state.selected_history = new_id
            st.rerun()

    # ── Display results ──
    if st.session_state.compare_mode and len(history) >= 2:
        render_compare_view(history)
    elif history:
        selected_id = st.session_state.get("selected_history")
        matching = [h for h in history if h["id"] == selected_id]
        entry = matching[0] if matching else history[-1]
        st.markdown('<div class="section-heading">Analysis Results</div>', unsafe_allow_html=True)
        render_analysis_card(entry["data"], key_prefix=str(entry["id"]))
    else:
        render_empty_state()

# ═════════════════════════════════════════════════════════════
# TAB 2 — Batch Mode
# ═════════════════════════════════════════════════════════════
with tab_batch:
    st.markdown('<div class="section-heading">Batch Upload</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.8rem; color:#8A94A8; margin-bottom:0.8rem;">Upload up to {MAX_BATCH_FILES} pitch decks. Each will be scored and ranked into a leaderboard.</div>', unsafe_allow_html=True)

    batch_files = st.file_uploader(
        "Upload multiple PDFs", type=["pdf"], accept_multiple_files=True,
        label_visibility="collapsed", key="batch_pdfs",
    )
    render_ocr_badge(OCR_READY)

    if batch_files and len(batch_files) > MAX_BATCH_FILES:
        st.warning(f"Only the first {MAX_BATCH_FILES} files will be processed.")
        batch_files = batch_files[:MAX_BATCH_FILES]

    run_batch = st.button(f"🔬 Analyze {len(batch_files) if batch_files else 0} Deck(s)", key="batch_run") if batch_files else False

    if run_batch:
        results = []
        progress_bar = st.progress(0, text="Starting batch analysis...")

        for i, f in enumerate(batch_files):
            progress_bar.progress((i) / len(batch_files), text=f"Analyzing {f.name} ({i+1}/{len(batch_files)})...")
            temp_path = f"temp_batch_{i}.pdf"
            with open(temp_path, "wb") as out:
                out.write(f.getbuffer())

            text, method = extract_pdf_text_with_ocr_fallback(temp_path, MIN_PDF_TEXT_LENGTH)
            if not text:
                results.append({"filename": f.name, "data": None, "error": "Could not extract text (image-based, no OCR available)"})
                continue

            data, error = run_analysis_silent(text)
            if data:
                db.save_analysis(data, model_used=GROQ_MODEL)
            results.append({"filename": f.name, "data": data, "error": error})

        progress_bar.progress(1.0, text="Done!")
        progress_bar.empty()
        render_batch_leaderboard(results)
    elif not batch_files:
        st.markdown('<div style="font-size:0.8rem;color:#8A94A8;margin-top:1rem;">Upload multiple pitch decks to rank them against each other.</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════
# TAB 3 — Multi-Model Comparison
# ═════════════════════════════════════════════════════════════
with tab_multimodel:
    st.markdown('<div class="section-heading">Cross-Model Validation</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.8rem; color:#8A94A8; margin-bottom:0.8rem;">Run the same pitch deck through multiple AI models to see how much they agree. Useful for sanity-checking a single model\'s score.</div>', unsafe_allow_html=True)

    mm_text = st.text_area(
        "Paste pitch deck text", height=180,
        placeholder="Paste pitch deck text here to compare across models...",
        label_visibility="collapsed", key="mm_text",
    )

    model_choices = st.multiselect(
        "Models to compare",
        options=list(AVAILABLE_MODELS.keys()),
        default=list(AVAILABLE_MODELS.keys())[:2],
        format_func=lambda k: AVAILABLE_MODELS[k]["label"],
    )

    run_mm = st.button("🔀 Run Cross-Model Comparison", key="mm_run") if (mm_text.strip() and len(model_choices) >= 2) else False
    if mm_text.strip() and len(model_choices) < 2:
        st.markdown('<div style="font-size:0.78rem;color:#F0C040;">Select at least 2 models to compare.</div>', unsafe_allow_html=True)

    if run_mm:
        mm_progress = st.empty()
        results = run_multi_model_analysis(mm_text.strip(), model_choices, mm_progress)
        render_multi_model_comparison(results)
    elif not mm_text.strip():
        st.markdown('<div style="font-size:0.8rem;color:#8A94A8;margin-top:1rem;">Paste pitch text above to compare model outputs side by side.</div>', unsafe_allow_html=True)

# ── Footer ──
st.markdown("""
<div style="font-size:0.7rem; color:#8A94A8; margin-top:2rem; padding-top:1rem; border-top:1px solid #1C2030;">
DealLens is an AI-assisted due diligence tool. Output is for informational purposes only and does not constitute investment advice.
</div>
""", unsafe_allow_html=True)