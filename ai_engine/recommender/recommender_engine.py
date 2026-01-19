"""
ai_engine/recommender/recommender_engine.py
===========================================
Human-like smartphone recommendation engine.
"""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from numpy.linalg import norm
from sklearn.metrics.pairwise import cosine_similarity

from ai_engine.recommender.brand_normalizer import resolve_brand

# -------------------------
# LOAD ARTIFACTS
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

PROCESSED_DF = joblib.load(ASSETS_DIR / "processed_df.pkl")
SCALER = joblib.load(ASSETS_DIR / "scaler.pkl")


class SmartphoneRecommender:
    FEATURES = [
        "price",
        "cam_resolution",
        "battery",
        "ram",
        "display_size",
        "weight",
        "release_year",
    ]

    BASE_WEIGHTS = {
        "price": 0.25,
        "cam_resolution": 0.20,
        "battery": 0.15,
        "ram": 0.10,
        "display_size": 0.10,
        "weight": 0.05,
        "release_year": 0.15,
    }

    def __init__(self):
        self.df = PROCESSED_DF.copy()
        self.scaler = SCALER

    # -------------------------
    # NORMALIZATION
    # -------------------------
    @staticmethod
    def _normalize_rows(X):
        return X / (norm(X, axis=1, keepdims=True) + 1e-8)

    def build_user_vector(self, user_input: dict):
        vec = np.array([[user_input.get(f, 0) for f in self.FEATURES]], dtype=float)
        vec_scaled = self.scaler.transform(vec)
        return self._normalize_rows(vec_scaled)

    # -------------------------
    # DYNAMIC WEIGHTING
    # -------------------------
    def _dynamic_weights(self, user_input: dict):
        weights = self.BASE_WEIGHTS.copy()

        profile = user_input.get("performance_profile", "balanced")

        if profile == "performance":
            weights["ram"] += 0.05
            weights["release_year"] += 0.05
            weights["price"] -= 0.05

        elif profile == "battery":
            weights["battery"] += 0.07
            weights["weight"] += 0.03
            weights["price"] -= 0.05

        # Normalize
        total = sum(weights.values())
        return {k: v / total for k, v in weights.items()}

    # -------------------------
    # FEATURE MATCHING
    # -------------------------
    def _feature_matches(self, row, user_input: dict):
        matches = {}
        budget = user_input.get("price", 0)

        matches["price"] = (
            max(0, 1 - abs(row["price"] - budget) / budget)
            if budget else 0.5
        )

        for f in ["cam_resolution", "battery", "ram"]:
            desired = user_input.get(f, 0)
            matches[f] = min(1, row[f] / desired) if desired else 0.5

        desired = user_input.get("display_size", 0)
        matches["display_size"] = (
            max(0, 1 - abs(row["display_size"] - desired) / desired)
            if desired else 0.5
        )

        desired = user_input.get("weight", 0)
        matches["weight"] = (
            max(0, 1 - abs(row["weight"] - desired) / desired)
            if desired else 0.5
        )

        y_min, y_max = self.df["release_year"].min(), self.df["release_year"].max()
        matches["release_year"] = (
            (row["release_year"] - y_min) / (y_max - y_min)
            if y_max > y_min else 0.5
        )

        return matches

    # -------------------------
    # HUMAN PENALTIES
    # -------------------------
    def _human_penalty(self, row, user_input: dict):
        penalty = 1.0

        # Unrealistic expectations
        if user_input.get("price", 0) < 400 and row["cam_resolution"] > 100:
            penalty -= 0.10

        if user_input.get("performance_profile") == "performance" and row["ram"] < 6:
            penalty -= 0.15

        if user_input.get("battery", 0) > 5000 and row["weight"] > 220:
            penalty -= 0.05

        return max(penalty, 0.6)

    # -------------------------
    # MAIN RECOMMEND
    # -------------------------
    def recommend(self, user_input: dict, top_n: int = 5):
        brand_info = resolve_brand(user_input.get("brand"), self.df)
        df = brand_info["filtered_df"]

        if df is None or df.empty:
            df = self.df.copy()
            brand_info["match_type"] = "fallback"

        df = df.reset_index(drop=True)

        X = df[self.FEATURES].astype(float).values
        X_scaled = self.scaler.transform(X)
        X_norm = self._normalize_rows(X_scaled)

        user_vec = self.build_user_vector(user_input)
        sim_scores = cosine_similarity(X_norm, user_vec).flatten()

        weights = self._dynamic_weights(user_input)

        final_scores = []
        feature_scores = []

        for _, row in df.iterrows():
            matches = self._feature_matches(row, user_input)
            score = sum(weights[f] * matches[f] for f in weights)
            score *= self._human_penalty(row, user_input)

            final_scores.append(score)
            feature_scores.append(matches)

        df["match_score"] = 0.4 * sim_scores + 0.6 * np.array(final_scores)
        df["feature_scores"] = feature_scores

        ranked = df.sort_values("match_score", ascending=False).head(top_n)

        return {
            "brand_info": brand_info,
            "items": ranked[["brand", "model", "match_score", "feature_scores"]].to_dict("records"),
        }


RECOMMENDER = SmartphoneRecommender()

def recommend(user_input: dict, top_n: int = 5):
    return RECOMMENDER.recommend(user_input, top_n=top_n)
