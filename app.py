from flask import Flask, render_template, request
import os
import redis
import requests
import psycopg2
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

# =================================================================
# NATIVE ENVIRONMENT VARIABLES (Injected directly by Cloud Run)
# =================================================================
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "movies")
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")

# Secrets mapped seamlessly via Environment Variables
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "f676b00029651576a5a060c3ac7e1167")
DB_USER = os.getenv("DB_USER", "movie_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "SecurePassword123!")

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True, socket_connect_timeout=1)
except Exception:
    redis_client = None

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, 
        database=DB_NAME, 
        user=DB_USER, 
        password=DB_PASSWORD, 
        connect_timeout=3
    )

@app.route('/')
def index():
    menu = request.args.get('menu', 'movies')
    cache_key = f"trending_{menu}_cache"
    source = "Redis Cache"

    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return render_template("index.html", current_menu=menu, source=source, results=json.loads(cached_data))
        except Exception:
            pass

    source = "Live API + Cloud SQL Logged"
    results = []
    
    try:
        if menu == "movies":
            url = "https://api.themoviedb.org/3/trending/movie/day"
            response = requests.get(url, params={"api_key": TMDB_API_KEY}, timeout=5)
            results = response.json().get("results", [])[:10]
        elif menu == "tv":
            url = "https://api.themoviedb.org/3/trending/tv/day"
            response = requests.get(url, params={"api_key": TMDB_API_KEY}, timeout=5)
            results = response.json().get("results", [])[:10]
        elif menu == "dramas":
            url = "https://api.themoviedb.org/3/discover/tv"
            params = {
                "api_key": TMDB_API_KEY,
                "with_genres": "18",
                "sort_by": "popularity.desc"
            }
            response = requests.get(url, params=params, timeout=5)
            results = response.json().get("results", [])[:10]
    except Exception:
        results = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS api_logs (id SERIAL, type TEXT, count INT);")
        cursor.execute("INSERT INTO api_logs (type, count) VALUES (%s, %s);", (menu, len(results)))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as db_err:
        print(f"Database sync skipped: {str(db_err)}")

    if redis_client and results:
        try:
            redis_client.setex(cache_key, 3600, json.dumps(results))
        except Exception:
            pass

    return render_template("index.html", current_menu=menu, source=source, results=results)

from asgiref.wsgi import WsgiToAsgi
asgi_app = WsgiToAsgi(app)