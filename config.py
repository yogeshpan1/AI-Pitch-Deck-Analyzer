"""App-wide constants: model settings, color palette, thresholds."""

# ── AI Model ──
GROQ_MODEL = "openai/gpt-oss-20b"
GROQ_TEMPERATURE = 0.3
MAX_INPUT_CHARS = 9000
MIN_TEXT_LENGTH = 80
MIN_PDF_TEXT_LENGTH = 100

# ── Available models for multi-model comparison ──
# All free-tier on Groq. Shown to the user as "Fast" vs "Deep" analysis.
AVAILABLE_MODELS = {
    "openai/gpt-oss-20b": {"label": "GPT-OSS 20B", "speed": "Fast", "desc": "Quick, reliable JSON output"},
    "openai/gpt-oss-120b": {"label": "GPT-OSS 120B", "speed": "Deep", "desc": "Slower, more nuanced reasoning"},
    "llama-3.3-70b-versatile": {"label": "Llama 3.3 70B", "speed": "Balanced", "desc": "Alternative model family for cross-checking"},
}

# ── Batch mode ──
MAX_BATCH_FILES = 8

# ── Score thresholds → colors ──
# (min_score, text_color, bg_color, border_color)
SCORE_TIERS = [
    (80, "#00D4AA", "rgba(0,212,170,0.12)", "#00D4AA"),   # STRONG PASS
    (65, "#5BC4FF", "rgba(91,196,255,0.12)", "#5BC4FF"),  # PASS
    (50, "#F0C040", "rgba(240,192,64,0.12)", "#F0C040"),  # WATCH
    (0, "#FF4D6D", "rgba(255,77,109,0.12)", "#FF4D6D"),   # SOFT PASS / REJECT
]

# ── Score breakdown labels ──
BREAKDOWN_LABELS = {
    "market_opportunity": "Market Opp.",
    "team_quality": "Team",
    "product_differentiation": "Differentiation",
    "traction_evidence": "Traction",
    "business_model_clarity": "Biz Model",
    "risk_level": "Risk Mgmt",
}

# ── Fundamentals section fields ──
FUNDAMENTALS_FIELDS = [
    ("Problem", "problem"),
    ("Solution", "solution"),
    ("Business Model", "business_model"),
    ("Traction", "traction"),
    ("Team", "team"),
    ("Competitive Advantage", "competitive_advantage"),
]

# ── Compare table fields ──
COMPARE_FIELDS = [
    ("Sector", "sector"),
    ("Stage", "stage"),
    ("Funding Ask", "funding_ask"),
    ("Business Model", "business_model"),
    ("Traction", "traction"),
]

# ── Pipeline loading steps ──
PIPELINE_STEPS = [
    "Reading document",
    "Extracting key metrics",
    "Scoring investment signal",
    "Finalizing report",
]


def get_score_colors(score: int):
    """Returns (text_color, bg_color, border_color) for a given investor score."""
    for threshold, text_color, bg_color, border_color in SCORE_TIERS:
        if score >= threshold:
            return text_color, bg_color, border_color
    return SCORE_TIERS[-1][1:]