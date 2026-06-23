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
