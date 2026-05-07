"""
Poster fetching utility using TMDB API.
"""
import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor

CACHE_FILE = os.path.join(os.path.dirname(__file__), "data", "poster_cache.json")
TMDB_API_KEY = "8b77e1b4a573845c17267cfc801a693d"
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w300"
PLACEHOLDER = "https://images.unsplash.com/photo-1485846234645-a62644f84728?q=80&w=300&auto=format&fit=crop"

def _load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def _save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)
    except:
        pass

def get_poster_url(tmdb_id, title=None):
    """Get poster URL for a movie."""
    cache = _load_cache()
    cache_key = str(tmdb_id) if tmdb_id and tmdb_id != 0 else (title or "")
    if not cache_key:
        return PLACEHOLDER
    
    if cache_key in cache:
        path = cache[cache_key]
        return f"{TMDB_IMG_BASE}{path}" if path else PLACEHOLDER

    try:
        # Try by ID first
        if tmdb_id and tmdb_id != 0:
            tid = str(int(float(tmdb_id)))
            resp = requests.get(
                f"https://api.themoviedb.org/3/movie/{tid}?api_key={TMDB_API_KEY}",
                timeout=5
            )
            if resp.status_code == 200:
                path = resp.json().get("poster_path")
                if path:
                    cache[cache_key] = path
                    _save_cache(cache)
                    return f"{TMDB_IMG_BASE}{path}"

        # Fallback: search by title
        if title:
            resp = requests.get(
                f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}",
                timeout=5
            )
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                if results:
                    path = results[0].get("poster_path")
                    if path:
                        cache[cache_key] = path
                        _save_cache(cache)
                        return f"{TMDB_IMG_BASE}{path}"
    except Exception as e:
        print(f"Poster fetch error: {e}")

    return PLACEHOLDER

def get_posters_parallel(movie_data):
    """Fetch posters in parallel. movie_data: list of (tmdb_id, title) tuples."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_poster_url, mid, title) for mid, title in movie_data]
        return [f.result() for f in futures]
