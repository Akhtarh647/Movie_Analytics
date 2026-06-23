import streamlit as st
import requests
from datetime import datetime, timedelta

# -----------------------------
# API KEYS & CONFIG
# -----------------------------
TMDB_API_KEY = "f676b00029651576a5a060c3ac7e1167"
TMDB_LANGUAGE = "en-US"

# -----------------------------
# FUNCTIONS
# -----------------------------
def fetch_trending(content_type, time_window="week"):
    """Daily or weekly trending from TMDB"""
    url = f"https://api.themoviedb.org/3/trending/{content_type}/{time_window}"
    params = {"api_key": TMDB_API_KEY, "language": TMDB_LANGUAGE}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])[:10]
    return []

def fetch_trending_last_month(content_type="movie"):
    """Simulated monthly trends using Discover endpoint"""
    today = datetime.today()
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)
    return fetch_trending_custom_range(content_type, first_day_last_month, last_day_last_month)

def fetch_trending_custom_range(content_type="movie", start_date=None, end_date=None):
    """Fetch trending movies/TV shows within a custom date range"""
    url = f"https://api.themoviedb.org/3/discover/{content_type}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": TMDB_LANGUAGE,
        "sort_by": "popularity.desc",
        "page": 1,
    }
    if start_date:
        params["primary_release_date.gte"] = start_date.strftime("%Y-%m-%d")
    if end_date:
        params["primary_release_date.lte"] = end_date.strftime("%Y-%m-%d")

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])[:10]
    return []

def fetch_dramas(page=1):
    """Fetch popular dramas (genre=18)"""
    url = "https://api.themoviedb.org/3/discover/tv"
    params = {
        "api_key": TMDB_API_KEY,
        "language": TMDB_LANGUAGE,
        "with_genres": "18",  # Drama genre ID
        "sort_by": "popularity.desc",
        "page": page,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])[:10]
    return []

def print_items(items, label):
    st.subheader(label)
    if not items:
        st.warning("No results found.")
    for idx, item in enumerate(items, 1):
        title = item.get("title") or item.get("name") or "N/A"
        date = item.get("release_date") or item.get("first_air_date") or "N/A"
        overview = item.get("overview") or "No overview available."
        st.markdown(f"**{idx}. {title} ({date})**")
        st.write(overview)
        poster_path = item.get("poster_path")
        if poster_path:
            st.image(f"https://image.tmdb.org/t/p/w200{poster_path}")
        st.markdown("---")

# -----------------------------
# STREAMLIT APP
# -----------------------------
st.set_page_config(page_title="Movie & TV Trends", layout="wide")
st.title("🎬 Trending Movies, TV Shows & Dramas")

trend_type = st.sidebar.radio("Choose Content Type", ["Movies", "TV Shows", "Dramas"])
time_window = st.sidebar.radio("Choose Time Window", ["Today", "This Week", "Last Month", "Custom Range"])

if trend_type == "Movies":
    if time_window == "Today":
        items = fetch_trending("movie", "day")
    elif time_window == "This Week":
        items = fetch_trending("movie", "week")
    elif time_window == "Last Month":
        items = fetch_trending_last_month("movie")
    else:  # Custom Range
        start_date = st.sidebar.date_input("Start Date", datetime.today() - timedelta(days=30))
        end_date = st.sidebar.date_input("End Date", datetime.today())
        if st.sidebar.button("Fetch Movies"):
            items = fetch_trending_custom_range("movie", start_date, end_date)
        else:
            items = []
    print_items(items, f"Top 10 {trend_type} - {time_window}")

elif trend_type == "TV Shows":
    if time_window == "Today":
        items = fetch_trending("tv", "day")
    elif time_window == "This Week":
        items = fetch_trending("tv", "week")
    elif time_window == "Last Month":
        items = fetch_trending_last_month("tv")
    else:  # Custom Range
        start_date = st.sidebar.date_input("Start Date", datetime.today() - timedelta(days=30))
        end_date = st.sidebar.date_input("End Date", datetime.today())
        if st.sidebar.button("Fetch TV Shows"):
            items = fetch_trending_custom_range("tv", start_date, end_date)
        else:
            items = []
    print_items(items, f"Top 10 {trend_type} - {time_window}")

else:  # Dramas
    if time_window in ["Today", "This Week", "Last Month"]:  
        # For simplicity, just use page=1 popular dramas
        items = fetch_dramas(page=1)
    else:  # Custom Range (not directly supported, fallback to popular dramas)
        st.sidebar.info("⚠️ Custom range filtering for dramas not available in TMDB API. Showing popular dramas instead.")
        items = fetch_dramas(page=1)
    print_items(items, f"Top 10 {trend_type} - {time_window}")
