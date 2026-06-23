from flask import Flask, render_template, request
import os
import redis
import requests
import psycopg2
import json

app = Flask(__name__)

# Environment Variables from GCP Setup
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "movie_admin")
DB_NAME = os.getenv("DB_NAME", "movies")
DB_PASSWORD = os.getenv("DB_PASSWORD", "SecurePassword123!")
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")

TMDB_API_KEY = "f676b00029651576a5a060c3ac7e1167"

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True, socket_connect_timeout=2)
except Exception:
    redis_client = None

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

@app.route('/')
def index():
    # Detect navigation click, default is 'movies'
    menu = request.args.get('menu', 'movies')
    cache_key = f"trending_{menu}_cache"
    source = "Redis Cache"

    # Step 1: Check Redis Cache
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return render_template("index.html", current_menu=menu, source=source, results=json.loads(cached_data))
        except Exception:
            pass

    # Step 2: Cache Miss -> Call TMDB API
    source = "Live API + Cloud SQL Logged"
    tmdb_type = "movie" if menu == "movies" else "tv"
    url = f"https://api.themoviedb.org/3/trending/{tmdb_type}/day"
    
    response = requests.get(url, params={"api_key": TMDB_API_KEY})
    results = response.json().get("results", [])[:10]

    # Step 3: Cloud SQL Logging
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS api_logs (id SERIAL, type TEXT, count INT);")
        cursor.execute("INSERT INTO api_logs (type, count) VALUES (%s, %s);", (menu, len(results)))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass

    # Step 4: Write to Redis Cache
    if redis_client:
        try:
            redis_client.setex(cache_key, 3600, json.dumps(results))
        except Exception:
            pass

    return render_template("index.html", current_menu=menu, source=source, results=results)

# Uvicorn entry wrapper integration
from asgiref.wsgi import WsgiToAsgi
asgi_app = WsgiToAsgi(app)