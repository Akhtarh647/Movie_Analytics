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

    url = f"https://api.themoviedb.org/3/discover/{content_type}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": TMDB_LANGUAGE,
        "sort_by": "popularity.desc",
        "page": 1,
        "primary_release_date.gte": first_day_last_month.strftime("%Y-%m-%d"),
        "primary_release_date.lte": last_day_last_month.strftime("%Y-%m-%d"),
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
st.title("🎬 Trending Movies & Shows")

trend_type = st.sidebar.radio("Choose Content Type", ["Movies", "TV Shows"])
time_window = st.sidebar.radio("Choose Time Window", ["Today", "This Week", "Last Month"])

if trend_type == "Movies":
    if time_window == "Today":
        items = fetch_trending("movie", "day")
    elif time_window == "This Week":
        items = fetch_trending("movie", "week")
    else:  # Last Month
        items = fetch_trending_last_month("movie")
    print_items(items, f"Top 10 {trend_type} - {time_window}")

else:  # TV Shows
    if time_window == "Today":
        items = fetch_trending("tv", "day")
    elif time_window == "This Week":
        items = fetch_trending("tv", "week")
    else:  # Last Month
        items = fetch_trending_last_month("tv")
    print_items(items, f"Top 10 {trend_type} - {time_window}")
