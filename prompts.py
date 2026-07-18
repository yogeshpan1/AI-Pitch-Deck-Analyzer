"""Prompt templates used to instruct the AI model."""

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