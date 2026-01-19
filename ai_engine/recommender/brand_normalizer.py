# ai_engine/recommender/brand_normalizer.py

import difflib
import pandas as pd


def normalize_brand_name(brand: str) -> str:
    """
    Normalize user input brand string.
    """
    if not brand:
        return ""
    return brand.strip().lower()


def resolve_brand(user_brand: str, df: pd.DataFrame) -> dict:
    """
    Resolve user brand to dataset brand.

    Returns a dict with:
    - resolved_brand
    - match_type: exact | closest | fallback
    - confidence
    - filtered_df
    - suggestion: list of close brands if no exact match
    """

    # Defensive checks
    if df is None or df.empty or "brand" not in df.columns:
        return {
            "resolved_brand": None,
            "match_type": "fallback",
            "confidence": 0.0,
            "filtered_df": df,
            "suggestion": []
        }

    user_brand_norm = normalize_brand_name(user_brand)

    # Normalize dataset brands
    df = df.copy()
    df["brand_norm"] = df["brand"].astype(str).str.lower().str.strip()
    available_brands = df["brand_norm"].unique().tolist()

    # 1️⃣ Exact match
    if user_brand_norm in available_brands:
        filtered_df = df[df["brand_norm"] == user_brand_norm]
        return {
            "resolved_brand": filtered_df["brand"].iloc[0],
            "match_type": "exact",
            "confidence": 1.0,
            "filtered_df": filtered_df.drop(columns=["brand_norm"]),
            "suggestion": []
        }

    # 2️⃣ Closest match (fuzzy)
    if user_brand_norm:
        matches = difflib.get_close_matches(
            user_brand_norm,
            available_brands,
            n=3,
            cutoff=0.6
        )
        if matches:
            closest = matches[0]
            filtered_df = df[df["brand_norm"] == closest]
            return {
                "resolved_brand": filtered_df["brand"].iloc[0],
                "match_type": "closest",
                "confidence": 0.7,
                "filtered_df": filtered_df.drop(columns=["brand_norm"]),
                "suggestion": matches
            }

    # 3️⃣ Fallback: no brand filter
    return {
        "resolved_brand": None,
        "match_type": "fallback",
        "confidence": 0.3,
        "filtered_df": df.drop(columns=["brand_norm"]),
        "suggestion": available_brands[:3]  # top 3 available brands
    }
