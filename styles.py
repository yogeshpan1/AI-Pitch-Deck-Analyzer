"""CSS for the DealLens finance-terminal aesthetic."""

CUSTOM_CSS = """
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

.risk-item {
    display: flex; gap: 0.6rem; padding: 0.6rem 0; border-bottom: 1px solid #1C2030; font-size: 0.84rem; color: #E8EDF5;
}
.risk-item:last-child { border-bottom: none; }
.risk-dot { width: 7px; height: 7px; border-radius: 50%; background: #FF4D6D; margin-top: 0.45rem; flex-shrink: 0; }

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
"""