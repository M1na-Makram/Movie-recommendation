# CineMatch AI: Hybrid Movie Recommendation System Evaluation

## 1. Executive Summary
The CineMatch AI project successfully implements a hybrid recommendation engine utilizing the MovieLens 100K dataset. The system integrates Content-Based Filtering (via TF-IDF and Cosine Similarity) and Collaborative Filtering (via SVD Matrix Factorization). The integration is achieved through a weighted ensemble, accessible via a high-performance, visually stunning Streamlit GUI.

## 2. Model Implementations

### 2.1 Content-Based Filtering
- **Feature Extraction:** TF-IDF Vectorization was applied to movie genres. Stop words were removed to reduce noise.
- **Similarity Metric:** Cosine similarity was used to compute distance between movie vectors, ensuring scale-invariant comparisons.
- **Workflow:** For any given user, the algorithm aggregates the TF-IDF vectors of their highly-rated movies (rating >= 4.0) to construct a localized user profile, which is then compared against unseen items.

### 2.2 Collaborative Filtering
- **Algorithm:** Singular Value Decomposition (SVD) provided by the Surprise library.
- **Hyperparameters:**
  - `n_factors`: 50 (latent space dimensionality)
  - `n_epochs`: 20 (stochastic gradient descent iterations)
  - `learning_rate (lr_all)`: 0.005
  - `regularization (reg_all)`: 0.02
- **Workflow:** The model uncovers latent behavioral traits by mapping user-item interactions to lower-dimensional representations, accurately predicting preferences for unseen movies.

### 2.3 Hybrid Approach
- **Integration:** Outputs from both models undergo Min-Max normalization to standard bounds `[0, 1]`.
- **Ensemble Strategy:** Weighted linear combination. By default, Collaborative Filtering is weighted at `60%` and Content-Based at `40%`, prioritizing global trends while injecting niche genre matches.

## 4. Key Insights & Conclusion
1. **Cold-Start Mitigation:** The Content-Based component allows the engine to recommend movies with fewer ratings based purely on item metadata (genres).
2. **Personalization Depth:** Collaborative Filtering excels at surfacing non-obvious, cross-genre recommendations based on latent community patterns.
3. **Interactive UI:** The Streamlit GUI empowers users to dynamically adjust hybrid weights, offering a transparent, customizable recommendation experience.
