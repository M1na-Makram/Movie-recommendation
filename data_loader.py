"""
Data Ingestion and Preprocessing Module
Prioritizes loading data from the 'data2' directory (CSV format) 
if available, otherwise falls back to MovieLens 100K.
"""
import os
import pandas as pd
import numpy as np
import requests
import zipfile

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA2_DIR = os.path.join(os.path.dirname(__file__), "data2")
DATASET_URL = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"

def download_dataset():
    """Download MovieLens 100K fallback if needed."""
    os.makedirs(DATA_DIR, exist_ok=True)
    zip_path = os.path.join(DATA_DIR, "ml-100k.zip")
    extract_path = os.path.join(DATA_DIR, "ml-100k")
    if os.path.exists(extract_path):
        return extract_path
    
    r = requests.get(DATASET_URL, stream=True)
    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(DATA_DIR)
    os.remove(zip_path)
    return extract_path

def load_all():
    """Load ratings and movies, prioritizing data2 CSV files."""
    
    # Check for data2 (CSV version)
    if os.path.exists(DATA2_DIR) and os.path.exists(os.path.join(DATA2_DIR, "movies.csv")):
        print("Loading high-resolution data from 'data2'...")
        
        movies = pd.read_csv(os.path.join(DATA2_DIR, "movies.csv"))
        ratings = pd.read_csv(os.path.join(DATA2_DIR, "ratings.csv"))
        
        # Rename columns to match project standards
        movies.rename(columns={'movieId': 'movie_id'}, inplace=True)
        ratings.rename(columns={'userId': 'user_id', 'movieId': 'movie_id'}, inplace=True)
        
        # Load TMDB IDs from links.csv for poster images
        links_path = os.path.join(DATA2_DIR, "links.csv")
        if os.path.exists(links_path):
            links = pd.read_csv(links_path)
            links.rename(columns={'movieId': 'movie_id'}, inplace=True)
            links['tmdb_id'] = pd.to_numeric(links['tmdbId'], errors='coerce').fillna(0).astype(int)
            movies = movies.merge(links[['movie_id', 'tmdb_id']], on='movie_id', how='left')
            movies['tmdb_id'] = movies['tmdb_id'].fillna(0).astype(int)
        else:
            movies['tmdb_id'] = 0
        
        # Format genres: Replace '|' with ' ' for TF-IDF
        movies['genres'] = movies['genres'].str.replace('|', ' ', regex=False)
        
        # Handle missing values
        movies['title'] = movies['title'].fillna("Unknown")
        movies['genres'] = movies['genres'].fillna("unknown")
        
        # We don't have a users.csv in data2 usually, so we'll create a dummy
        users = pd.DataFrame({'user_id': ratings['user_id'].unique()})
        
        return ratings, movies, users

    # Fallback to ml-100k (Original logic)
    print("Falling back to MovieLens 100K dataset...")
    path = download_dataset()
    
    # Load Ratings
    ratings = pd.read_csv(
        os.path.join(path, "u.data"),
        sep="\t",
        names=["user_id", "movie_id", "rating", "timestamp"],
    )
    
    # Load Movies
    genre_names = ["unknown", "Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"]
    movies = pd.read_csv(
        os.path.join(path, "u.item"),
        sep="|",
        encoding="latin-1",
        header=None,
        names=["movie_id", "title", "release_date", "video_release_date", "imdb_url"] + genre_names,
    )
    
    def get_genres(row):
        return " ".join([g for g in genre_names if row[g] == 1])
    
    movies["genres"] = movies.apply(get_genres, axis=1)
    movies = movies[["movie_id", "title", "genres"]]
    
    # Load Users
    users = pd.read_csv(
        os.path.join(path, "u.user"),
        sep="|",
        names=["user_id", "age", "gender", "occupation", "zip_code"],
    )
    
    return ratings, movies, users
