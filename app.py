<<<<<<< HEAD
import streamlit as st
import requests

# -----------------------------
# API KEYS & CONFIG
# -----------------------------
TMDB_API_KEY = "f676b00029651576a5a060c3ac7e1167"
TMDB_LANGUAGE = "en-US"

RAPIDAPI_URL = "https://netflix54.p.rapidapi.com/season/episodes/"
RAPIDAPI_HEADERS = {
    "x-rapidapi-host": "netflix54.p.rapidapi.com",
    "x-rapidapi-key": "49bbbc0c53msh2368c300ca5b001p101de5jsn3dc6e5c2199b"
}


# -----------------------------
# FUNCTIONS
# -----------------------------
def fetch_trending(content_type, time_window="day"):
    url = f"https://api.themoviedb.org/3/trending/{content_type}/{time_window}"
    params = {"api_key": TMDB_API_KEY, "language": TMDB_LANGUAGE}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])[:10]
    return []


def fetch_dramas():
    url = "https://api.themoviedb.org/3/discover/tv"
    params = {
        "api_key": TMDB_API_KEY,
        "language": TMDB_LANGUAGE,
        "with_genres": "18",  # Drama genre ID
        "sort_by": "popularity.desc",
        "page": 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])[:10]
    return []





# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Movie Analytics", layout="wide")
st.title("🎬 Scalable Movie Analytics Platform")

# Sidebar menu
menu = st.sidebar.radio(
    "Choose a section",
    ["Trending Movies", "Trending TV Shows", "Popular Dramas"]
)

if menu == "Trending Movies":
    st.header("🔥 Top 10 Trending Movies")
    movies = fetch_trending("movie")
    for idx, movie in enumerate(movies, 1):
        title = movie.get("title", "N/A")
        date = movie.get("release_date", "N/A")
        overview = movie.get("overview", "No overview available.")
        st.subheader(f"{idx}. {title} ({date})")
        st.write(overview)
        poster_path = movie.get("poster_path")
        if poster_path:
            st.image(f"https://image.tmdb.org/t/p/w200{poster_path}")

elif menu == "Trending TV Shows":
    st.header("📺 Top 10 Trending TV Shows")
    shows = fetch_trending("tv")
    for idx, show in enumerate(shows, 1):
        title = show.get("name", "N/A")
        date = show.get("first_air_date", "N/A")
        overview = show.get("overview", "No overview available.")
        st.subheader(f"{idx}. {title} ({date})")
        st.write(overview)
        poster_path = show.get("poster_path")
        if poster_path:
            st.image(f"https://image.tmdb.org/t/p/w200{poster_path}")

elif menu == "Popular Dramas":
    st.header("🎭 Top 10 Popular Drama TV Shows")
    dramas = fetch_dramas()
    for idx, drama in enumerate(dramas, 1):
        title = drama.get("name", "N/A")
        date = drama.get("first_air_date", "N/A")
        overview = drama.get("overview", "No overview available.")
        st.subheader(f"{idx}. {title} ({date})")
        st.write(overview)
        poster_path = drama.get("poster_path")
        if poster_path:
            st.image(f"https://image.tmdb.org/t/p/w200{poster_path}")


    else:
        st.warning("No episodes found for this season ID.")
=======
import streamlit as st
import requests
from datetime import datetime, timedelta, date
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError

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

def fetch_dramas_custom_range(start_date, end_date, max_pages=10):
    """Fetch dramas and filter locally by custom date range"""
    # Ensure we are working with datetime objects
    if isinstance(start_date, date) and not isinstance(start_date, datetime):
        start_date = datetime.combine(start_date, datetime.min.time())
    if isinstance(end_date, date) and not isinstance(end_date, datetime):
        end_date = datetime.combine(end_date, datetime.max.time())

    all_dramas = []
    url = "https://api.themoviedb.org/3/discover/tv"

    for page in range(1, max_pages + 1):
        params = {
            "api_key": TMDB_API_KEY,
            "language": TMDB_LANGUAGE,
            "with_genres": "18",
            "sort_by": "popularity.desc",
            "page": page,
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            results = response.json().get("results", [])
            all_dramas.extend(results)
        else:
            break

    # Local filtering by first_air_date
    filtered = []
    for d in all_dramas:
        air_date = d.get("first_air_date") or d.get("release_date")
        if air_date:
            try:
                air_date_obj = datetime.strptime(air_date, "%Y-%m-%d")
                if start_date <= air_date_obj <= end_date:
                    filtered.append(d)
            except:
                continue

    if not filtered:
        st.warning(
            f"No dramas found between {start_date.strftime('%Y-%m-%d')} "
            f"and {end_date.strftime('%Y-%m-%d')} "
            f"(searched {len(all_dramas)} dramas). Try widening the date range."
        )

    # Sort by popularity
    filtered_sorted = sorted(filtered, key=lambda x: x.get("popularity", 0), reverse=True)
    return filtered_sorted[:10]

def print_items(items, label):
    st.subheader(label)
    if not items:
        st.warning("No results found.")
    for idx, item in enumerate(items, 1):
        title = item.get("title") or item.get("name") or "N/A"
        date_str = item.get("release_date") or item.get("first_air_date") or "N/A"
        overview = item.get("overview") or "No overview available."
        st.markdown(f"**{idx}. {title} ({date_str})**")
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
        items = fetch_dramas(page=1)
    else:  # Custom Range (simulate with local filtering)
        start_date = st.sidebar.date_input("Start Date", datetime.today() - timedelta(days=30))
        end_date = st.sidebar.date_input("End Date", datetime.today())
        if st.sidebar.button("Fetch Dramas"):
            items = fetch_dramas_custom_range(start_date, end_date, max_pages=10)
        else:
            items = []
    print_items(items, f"Top 10 {trend_type} - {time_window}")

    
>>>>>>> 0b238e1145de953090263e0a91d01434054373ca
