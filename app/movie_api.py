import os
import requests
import asyncio
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def _fetch_sync():
    # यह फंक्शन सिंक्रोनस तरीके से API से डेटा लाएगा
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=en-US&page=1"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    results = response.json().get("results", [])
    
    movies = []
    for m in results:
        # main.py और models.py को जो Keys चाहिए, हम उन्हें यहाँ मैप कर रहे हैं
        movies.append({
            "tmdb_id": m.get("id"),  # TMDB 'id' को 'tmdb_id' में बदला
            "title": m.get("title"),
            "overview": m.get("overview"),
            "poster_path": m.get("poster_path"),
            "backdrop_path": m.get("backdrop_path"),
            "vote_average": m.get("vote_average"),
            "release_date": m.get("release_date"),
        })
    return movies

async def fetch_popular_movies():
    # main.py 'await' का इस्तेमाल कर रहा है, इसलिए इसे async बनाया है
    return await asyncio.to_thread(_fetch_sync)
async def fetch_movie_trailer(tmdb_id: int):
    def _fetch():
        # TMDB के videos endpoint से ट्रेलर मांगें
        url = f"{BASE_URL}/movie/{tmdb_id}/videos?api_key={API_KEY}&language=en-US"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        videos = response.json().get("results", [])
        
        # पहले YouTube का 'Trailer' ढूंढें
        for video in videos:
            if video.get("site") == "YouTube" and video.get("type") == "Trailer":
                return video.get("key")
                
        # अगर 'Trailer' न मिले, तो कोई भी YouTube वीडियो (Teaser आदि) ले लें
        for video in videos:
            if video.get("site") == "YouTube":
                return video.get("key")
        return None
    return await asyncio.to_thread(_fetch)

# app/movie_api.py में जोड़ें
async def fetch_movie_stream_link(tmdb_id: int):
    """
    यहाँ आपको कोई भी ओपन-सोर्स स्ट्रीमिंग API (जैसे vidsrc, 8Stream आदि) 
    कॉल करनी होगी जो IMDB ID या TMDB ID लेकर HLS (.m3u8) लिंक देती है।
    """
    # उदाहरण के लिए (यह सिर्फ एक नकली लिंक है, आपको असली API डालनी होगी):
    # url = f"https://api.some-streaming-site.com/movie/{tmdb_id}?lang=hi"
    # response = requests.get(url)
    # return response.json().get("stream_url")
    
    # अभी के लिए हम एक अच्छी क्वालिटी का टेस्ट HLS लिंक दे रहे हैं
    return "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"


# app/movie_api.py में जोड़ें

# भाषा कोड: hi=हिंदी, ta=तमिल, te=तेलुगु, en=अंग्रेज़ी
LANGUAGES = ["hi", "ta", "te", "en"]

from datetime import datetime, timedelta

# ... (पुराना कोड)

async def fetch_movies_by_language():
    all_movies = []
    # पिछले 180 दिनों की तारीख निकालें (नई रिलीज़ के लिए)
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    
    # हम हर भाषा के लिए दो क्वेरीज़ चलाएंगे: एक 'Popular' और एक 'New Releases'
    languages = ["hi", "ta", "te", "en"]
    
    for lang in languages:
        # --- क्वेरी 1: लोकप्रिय मूवीज़ (Popular) ---
        try:
            url = f"{BASE_URL}/discover/movie"
            params = {
                "api_key": API_KEY,
                "with_original_language": lang,
                "sort_by": "popularity.desc",
                "page": 1
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            movies = response.json().get("results", [])
            for m in movies:
                all_movies.append({
                    "tmdb_id": m.get("id"),
                    "title": m.get("title"),
                    "overview": m.get("overview"),
                    "poster_path": m.get("poster_path"),
                    "backdrop_path": m.get("backdrop_path"),
                    "vote_average": m.get("vote_average"),
                    "release_date": m.get("release_date"),
                })
        except Exception as e:
            print(f"Error fetching popular movies for {lang}: {e}")

        # --- क्वेरी 2: नई रिलीज़ (New Releases) ---
        try:
            url = f"{BASE_URL}/discover/movie"
            params = {
                "api_key": API_KEY,
                "with_original_language": lang,
                "primary_release_date.gte": six_months_ago, # <-- यहाँ नई रिलीज़ का फ़िल्टर लगा है
                "sort_by": "primary_release_date.desc", # <-- तारीख के हिसाब से सॉर्ट
                "page": 1
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            new_movies = response.json().get("results", [])
            for m in new_movies:
                # डुप्लीकेट से बचने के लिए चेक करें
                if not any(movie['tmdb_id'] == m.get("id") for movie in all_movies):
                    all_movies.append({
                        "tmdb_id": m.get("id"),
                        "title": m.get("title"),
                        "overview": m.get("overview"),
                        "poster_path": m.get("poster_path"),
                        "backdrop_path": m.get("backdrop_path"),
                        "vote_average": m.get("vote_average"),
                        "release_date": m.get("release_date"),
                    })
        except Exception as e:
            print(f"Error fetching new releases for {lang}: {e}")
            
    return all_movies