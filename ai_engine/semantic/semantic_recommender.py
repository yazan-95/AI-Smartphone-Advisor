import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .embedding_model import NLQueryEncoder

class SemanticSmartphoneRecommender:
    def __init__(self, df):
        self.df = df.copy()
        self.df["semantic_text"] = (
            df["brand"] + " " +
            df["model"] + " " +
            df["cam_resolution"].astype(str) + "MP camera " +
            df["battery"].astype(str) + "mAh battery"
        )
        self.embeddings = self._build_embeddings()

    def _build_embeddings(self):
        encoder = NLQueryEncoder.load()
        return encoder.encode(self.df["semantic_text"].tolist())

    def recommend(self, nl_query, top_n=3):
        query_vec = NLQueryEncoder.encode(nl_query)
        sims = cosine_similarity([query_vec], self.embeddings)[0]
        self.df["match_score"] = sims
        self.df["feature_scores"] = [{} for _ in range(len(self.df))]
        return self.df.sort_values("match_score", ascending=False).head(top_n)
