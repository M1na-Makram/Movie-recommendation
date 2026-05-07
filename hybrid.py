"""
Hybrid Recommendation Engine
Combines Content-Based and Collaborative Filtering via weighted averaging.
"""
import pandas as pd
import numpy as np


class HybridRecommender:
    def __init__(self, cb_filter, cf_filter, cb_weight=0.4, cf_weight=0.6):
        self.cb = cb_filter
        self.cf = cf_filter
        self.cb_weight = cb_weight
        self.cf_weight = cf_weight

    def _normalize(self, scores):
        """Min-max normalize a series to [0, 1]."""
        mn, mx = scores.min(), scores.max()
        if mx - mn == 0:
            return scores * 0.0
        return (scores - mn) / (mx - mn)

    def recommend(self, user_id, ratings_df, movies_df, top_n=10):
        """
        Generate hybrid recommendations by combining normalized scores
        from both content-based and collaborative filtering.
        """
        # Get content-based recommendations (more than top_n to have overlap)
        cb_recs = self.cb.get_recommendations_for_user(user_id, ratings_df, top_n=100)
        cf_recs = self.cf.get_recommendations_for_user(user_id, movies_df, top_n=100)

        if cb_recs.empty and cf_recs.empty:
            return pd.DataFrame()

        # Normalize scores
        if not cb_recs.empty:
            cb_recs["cb_norm"] = self._normalize(cb_recs["cb_score"])
        if not cf_recs.empty:
            cf_recs["cf_norm"] = self._normalize(cf_recs["cf_score"])

        # Merge on movie_id
        if not cb_recs.empty and not cf_recs.empty:
            merged = pd.merge(
                cb_recs[["movie_id", "title", "genres", "cb_norm"]],
                cf_recs[["movie_id", "cf_norm"]],
                on="movie_id",
                how="outer",
            )
        elif not cb_recs.empty:
            merged = cb_recs[["movie_id", "title", "genres", "cb_norm"]].copy()
            merged["cf_norm"] = 0.0
        else:
            merged = cf_recs[["movie_id", "title", "genres", "cf_norm"]].copy()
            merged["cb_norm"] = 0.0

        # Fill missing movie info
        if "title" not in merged.columns or merged["title"].isna().any() or "tmdb_id" not in merged.columns:
            title_map = movies_df.set_index("movie_id")["title"].to_dict()
            genre_map = movies_df.set_index("movie_id")["genres"].to_dict()
            tmdb_map = movies_df.set_index("movie_id")["tmdb_id"].to_dict()
            
            merged["title"] = merged["movie_id"].map(title_map)
            merged["genres"] = merged["movie_id"].map(genre_map)
            merged["tmdb_id"] = merged["movie_id"].map(tmdb_map)

        merged["cb_norm"] = merged["cb_norm"].fillna(0)
        merged["cf_norm"] = merged["cf_norm"].fillna(0)

        # Weighted combination
        merged["hybrid_score"] = (
            self.cb_weight * merged["cb_norm"] + self.cf_weight * merged["cf_norm"]
        )

        merged = merged.sort_values("hybrid_score", ascending=False).head(top_n)
        merged = merged.reset_index(drop=True)
        return merged
