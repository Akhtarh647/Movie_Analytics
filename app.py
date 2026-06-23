from flask import Flask, jsonify
import os
import redis
import requests
import psycopg2
import json

app = Flask(__name__)

# Environment variables matching your infrastructure
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
def home():
    return "<h1>Flask Movie Analytics Live (via Uvicorn)!</h1>"

@app.route('/movies')
def get_movies():
    cache_key = "trending_movies_cache"

    if redis_client:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return jsonify({"source": "Redis Cache", "results": json.loads(cached_data)})

    url = "https://api.themoviedb.org/3/trending/movie/day"
    response = requests.get(url, params={"api_key": TMDB_API_KEY})
    movies = response.json().get("results", [])[:10]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS api_logs (id SERIAL, type TEXT, count INT);")
        cursor.execute("INSERT INTO api_logs (type, count) VALUES (%s, %s);", ("movies", len(movies)))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass

    if redis_client:
        redis_client.setex(cache_key, 3600, json.dumps(movies))

    return jsonify({"source": "Live API + Cloud SQL Logged", "results": movies})

# Required wrapper to let Uvicorn read Flask natively as an ASGI target
from asgiref.wsgi import WsgiToAsgi
asgi_app = WsgiToAsgi(app)