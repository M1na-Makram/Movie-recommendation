"""
Content-Based Filtering Module
Uses TF-IDF on movie genres and cosine similarity to find similar movies.
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedFilter:
    def __init__(self, movies_df):
        self.movies = movies_df.copy()
        self.tfidf_matrix = None
        self.similarity_matrix = None
        self._build()

    def _build(self):
        """Build TF-IDF matrix and compute cosine similarity."""
        tfidf = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = tfidf.fit_transform(self.movies["genres"])
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix)

    def get_similar_movies(self, movie_id, top_n=10):
        """Return top-N similar movies for a given movie_id."""
        idx_list = self.movies.index[self.movies["movie_id"] == movie_id].tolist()
        if not idx_list:
            return pd.DataFrame()

        idx = idx_list[0]
        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1: top_n + 1]  # exclude self

        movie_indices = [i[0] for i in sim_scores]
        scores = [i[1] for i in sim_scores]

        result = self.movies.iloc[movie_indices].copy()
        result["similarity_score"] = scores
        return result.reset_index(drop=True)

    def get_recommendations_for_user(self, user_id, ratings_df, top_n=10):
        """
        Recommend movies for a user based on movies they rated highly.
        Average the similarity scores across all movies rated >= 4.
        """
        user_ratings = ratings_df[ratings_df["user_id"] == user_id]
        liked = user_ratings[user_ratings["rating"] >= 4]["movie_id"].tolist()

        if not liked:
            liked = user_ratings.nlargest(3, "rating")["movie_id"].tolist()

        if not liked:
            return pd.DataFrame()

        # Map movie_ids to indices
        all_scores = np.zeros(len(self.movies))
        count = 0
        for mid in liked:
            idx_list = self.movies.index[self.movies["movie_id"] == mid].tolist()
            if idx_list:
                all_scores += self.similarity_matrix[idx_list[0]]
                count += 1

        if count > 0:
            all_scores /= count

        # Exclude already-rated movies
        rated_ids = set(user_ratings["movie_id"].tolist())
        candidates = []
        for i, score in enumerate(all_scores):
            mid = self.movies.iloc[i]["movie_id"]
            if mid not in rated_ids:
                candidates.append((i, score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        top = candidates[:top_n]

        result = self.movies.iloc[[c[0] for c in top]].copy()
        result["cb_score"] = [c[1] for c in top]
        return result.reset_index(drop=True)
