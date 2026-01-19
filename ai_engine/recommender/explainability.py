"""
explainability.py
=================
Professional feature-level explanation for smartphone recommendations.

- Structured dictionary output for frontend
- Human-readable sentences for top features
- Fully safe for Django import (no code runs at import time)
"""

from typing import Dict, List, Tuple

# -------------------------------------------------
# UTILITY FUNCTION
# -------------------------------------------------
def get_top_features(feature_scores: Dict[str, float], top_n: int = 3) -> List[Tuple[str, float]]:
    """
    Sort features by match score descending and return top N.
    """
    if not feature_scores:
        return []
    sorted_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_features[:top_n]


# -------------------------------------------------
# MAIN EXPLANATION FUNCTION
# -------------------------------------------------
def explain_recommendation(feature_scores: Dict[str, float], top_k: int = 3) -> Dict[str, List[str]]:
    """
    Given feature_scores dict, return explanation for UI with structured pros/cons.
    """
    if not feature_scores:
        return {"top_features": [], "pros": [], "cons": []}

    # -------------------------------
    # Human-readable top feature reasons
    # -------------------------------
    top_features = get_top_features(feature_scores, top_k)
    reasons = []

    for feature, score in top_features:
        if score < 0.6:
            continue  # only consider strong matches

        label = feature.replace("_", " ").title()
        if feature == "price":
            reasons.append("It fits well within your budget.")
        elif feature == "cam_resolution":
            reasons.append("The camera quality aligns with your expectations.")
        elif feature == "battery":
            reasons.append("The battery capacity supports long daily usage.")
        elif feature == "ram":
            reasons.append("It provides smooth multitasking performance.")
        elif feature == "display_size":
            reasons.append("The screen size matches your viewing preference.")
        elif feature == "weight":
            reasons.append("Its weight matches your comfort preference.")
        elif feature == "release_year":
            reasons.append("It is relatively recent compared to other options.")
        else:
            reasons.append(f"{label} closely matches your preference.")

    # -------------------------------
    # Structured pros & cons
    # -------------------------------
    pros, cons = [], []
    for feature, score in feature_scores.items():
        if score >= 0.7:  # threshold for 'pro'
            pros.append(feature.replace("_", " ").title())
        elif score <= 0.4:  # threshold for 'con'
            cons.append(feature.replace("_", " ").title())

    return {
        "top_features": reasons,
        "pros": pros,
        "cons": cons
    }


# -------------------------------------------------
# ⚠️ REMOVE ALL TEST CODE BELOW
# -------------------------------------------------
# Do NOT call recommend() here
# Keep this module import-safe for Django
