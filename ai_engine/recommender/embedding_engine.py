from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class EmbeddingSmartphoneRecommender:
    """
    Semantic recommender using sentence embeddings.

    - Safe with filtered dataframes
    - Stateless per recommend() call
    - Compatible with classic recommender output
    """

    def __init__(self, df):
        self.df = df.copy()
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Cache full-model embeddings
        self.model_names = self.df["model"].astype(str).tolist()
        self.full_embeddings = self.model.encode(self.model_names, normalize_embeddings=True)

    def _embed_text(self, text: str):
        return self.model.encode([text], normalize_embeddings=True)

    def recommend(self, query: str, top_n: int = 3, df_override=None):
        """
        Recommend phones based on semantic similarity to a text query.
        """
        df = df_override.copy() if df_override is not None else self.df.copy()

        if df.empty:
            return df

        # Build embeddings aligned to df (CRITICAL FIX)
        model_names = df["model"].astype(str).tolist()
        embeddings = self.model.encode(model_names, normalize_embeddings=True)

        query_vec = self._embed_text(query)

        scores = cosine_similarity(embeddings, query_vec).flatten()

        df["match_score"] = scores
        df["feature_scores"] = [{} for _ in range(len(df))]

        return df.sort_values("match_score", ascending=False).head(top_n)[
            ["model", "match_score", "feature_scores"]
        ]
