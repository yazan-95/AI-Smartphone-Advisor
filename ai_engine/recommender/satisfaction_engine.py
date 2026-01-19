from pathlib import Path
import joblib
import numpy as np
import pandas as pd


ASSETS_DIR = Path(__file__).resolve().parent / "assets"
MODEL_PATH = ASSETS_DIR / "satisfaction_model.pkl"
SCALER_PATH = ASSETS_DIR / "scaler.pkl"

NUMERIC_FEATURES = [
    "price",
    "cam_resolution",
    "battery",
    "ram",
    "display_size",
    "weight",
    "release_year",
]


class SatisfactionRecommender:
    """
    Predicts and ranks phones by expected user satisfaction.
    Output schema matches other recommenders.
    """

    def __init__(self, raw_df: pd.DataFrame):
        self.df = raw_df.copy()
        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)

    def _build_features(self, df: pd.DataFrame) -> np.ndarray:
        X = df[NUMERIC_FEATURES].astype(float)
        return self.scaler.transform(X)

    @staticmethod
    def _normalize(scores: np.ndarray) -> np.ndarray:
        if scores.max() == scores.min():
            return np.ones_like(scores) * 0.5
        return (scores - scores.min()) / (scores.max() - scores.min())

    def recommend(self, user_input: dict, top_n: int = 3, df_override=None):
        df = df_override.copy() if df_override is not None else self.df.copy()

        if df.empty:
            return df

        X = self._build_features(df)
        raw_scores = self.model.predict(X)

        norm_scores = self._normalize(raw_scores)

        df["match_score"] = norm_scores
        df["feature_scores"] = [{} for _ in range(len(df))]

        return df.sort_values("match_score", ascending=False).head(top_n)[
            ["model", "match_score", "feature_scores"]
        ]
