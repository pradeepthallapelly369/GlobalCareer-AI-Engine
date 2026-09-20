"""
Intelligent Tier Router for colibri-studio
Classifies prompts and maps them to Tier 1 through Tier 5
based on computational complexity, task type, and hardware availability.
"""

import re
from typing import Dict, Any
from models_config import TIER_MODELS

# Keywords and heuristics for each tier
TIER_PATTERNS = {
    "tier1": [
        r"\b(theorem|proof|formal proof|axiom|calculus|quantum|kernel optimization|distributed consensus|paxos|raft)\b",
        r"\b(assembly|compiler optimization|simd intrinsic|low-level memory model|microarchitecture|cache coherency)\b",
        r"\b(frontier reasoning|game theory equilibrium|cryptographic protocol|zero knowledge)\b"
    ],
    "tier2": [
        r"\b(refactor|architect|multi-file|full-stack|docker-compose|kubernetes|microservice architecture)\b",
        r"\b(multimodal|image recognition|ocr|document parsing|deep code review|ast analysis)\b",
        r"\b(concurrency deadlock|race condition|memory leak debugging|performance profiling)\b"
    ],
    "tier3": [
        r"\b(fastapi|flask|express|rest api|endpoint|crud|sql query|index optimization|database schema)\b",
        r"\b(etl pipeline|data transform|pandas|data ingestion|automation script|cron)\b",
        r"\b(unit test|integration test|pytest|mocking|documentation generator)\b"
    ],
    "tier4": [
        r"\b(fix syntax|regex|regular expression|explain this function|convert python to js|typescript interface)\b",
        r"\b(css styling|html layout|center div|flexbox|quick review|brainstorm ideas)\b",
        r"\b(write a polite email|summarize in 3 bullet points|rephrase|translate)\b"
    ],
    "tier5": [
        r"\b(hello|hi|hey|greetings|who are you|what can you do|ping|test)\b",
        r"\b(classify|sentiment|positive or negative|is this spam|extract json|boolean check)\b",
        r"\b(format as markdown table|list top 5|simple calculation|uppercase|trim)\b"
    ]
}

def analyze_prompt_complexity(prompt: str) -> Dict[str, Any]:
    text = prompt.lower().strip()
    words = text.split()
    word_count = len(words)
    
    scores = {"tier1": 0.0, "tier2": 0.0, "tier3": 0.0, "tier4": 0.0, "tier5": 0.0}
    reasons = []

    # Check keyword patterns
    for tier, patterns in TIER_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                weight = 3.0 if tier in ("tier1", "tier2") else 2.0
                scores[tier] += len(matches) * weight
                reasons.append(f"Matched {tier.upper()} keywords: {', '.join(set(matches))}")

    # Heuristics based on prompt length and structural indicators
    if word_count > 150 or "```" in prompt:
        scores["tier1"] += 2.0
        scores["tier2"] += 3.0
        reasons.append("Long detailed prompt / contains code blocks")
    elif word_count > 60:
        scores["tier2"] += 2.0
        scores["tier3"] += 3.0
        reasons.append("Moderate complexity prompt")
    elif word_count < 12:
        scores["tier5"] += 3.0
        scores["tier4"] += 1.5
        reasons.append("Short prompt / single-line command")

    # If no strong match, default to Tier 4 (Compact) or Tier 3 (Balanced)
    selected_tier = max(scores, key=scores.get)
    if scores[selected_tier] == 0:
        selected_tier = "tier4"
        reasons.append("Defaulting to Tier 4 (Compact MoE) for general balance")

    model_meta = TIER_MODELS[selected_tier]

    return {
        "selected_tier": selected_tier,
        "model_name": model_meta["name"],
        "badge": model_meta["badge"],
        "total_params": model_meta["total_params"],
        "active_params": model_meta["active_params"],
        "hardware_status": model_meta["hardware_status"],
        "confidence": min(1.0, 0.5 + (scores[selected_tier] * 0.1)),
        "reasons": reasons if reasons else ["Matched general workflow intent"],
        "scores": scores
    }
