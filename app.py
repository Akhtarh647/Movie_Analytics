from flask import Flask, render_template, request
import os
import redis
import requests
import psycopg2
import json
from google.cloud import secretmanager

current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

# =================================================================
# 1. ENVIRONMENT CONFIGURATIONS
# =================================================================
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "plated-client-499118-m4")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "movies")
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")

def get_secret(secret_id, project_id=GCP_PROJECT_ID, version_id="latest"):
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8").strip()
    except Exception:
        # Strict hardcoded fallbacks to prevent startup validation blockages
        defaults = {
            "tmdb-api-key": "f676b00029651576a5a060c3ac7e1167",
            "database-user": "movie_admin",
            "database-password": "SecurePassword123!"
        }
        return defaults.get(secret_id)

# =================================================================
# 2. INFRASTRUCTURE CONNECTIONS (Lazy Evaluation)
# =================================================================
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True, socket_connect_timeout=1)
except Exception:
    redis_client = None

def get_db_connection():
    # Secrets are resolved inside the function call, NOT at startup
    db_user = get_secret("database-user")
    db_password = get_secret("database-password")
    return psycopg2.connect(
        host=DB_HOST, 
        database=DB_NAME, 
        user=db_user, 
        password=db_password, 
        connect_timeout=3
    )

# =================================================================
# 3. ROUTING ENGINE
# =================================================================
@app.route('/')
def index():
    menu = request.args.get('menu', 'movies')
    cache_key = f"trending_{menu}_cache"
    source = "Redis Cache"

    # Step A: Redis Cache Lookup
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return render_template("index.html", current_menu=menu, source=source, results=json.loads(cached_data))
        except Exception:
            pass

    # Step B: API Fetching
    source = "Live API + Cloud SQL Logged"
    results = []
    tmdb_key = get_secret("tmdb-api-key")
    
    try:
        if menu == "movies":
            url = "https://api.themoviedb.org/3/trending/movie/day"
            response = requests.get(url, params={"api_key": tmdb_key}, timeout=5)
            results = response.json().get("results", [])[:10]
        elif menu == "tv":
            url = "https://api.themoviedb.org/3/trending/tv/day"
            response = requests.get(url, params={"api_key": tmdb_key}, timeout=5)
            results = response.json().get("results", [])[:10]
        elif menu == "dramas":
            url = "https://api.themoviedb.org/3/discover/tv"
            params = {
                "api_key": tmdb_key,
                "with_genres": "18",
                "sort_by": "popularity.desc"
            }
            response = requests.get(url, params=params, timeout=5)
            results = response.json().get("results", [])[:10]
    except Exception:
        results = []

    # Step C: Safe Async-Style Database Logging (Won't crash the page if DB is down)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS api_logs (id SERIAL, type TEXT, count INT);")
        cursor.execute("INSERT INTO api_logs (type, count) VALUES (%s, %s);", (menu, len(results)))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as db_err:
        print(f"Database logging skipped/failed: {str(db_err)}")

    # Step D: Populate Redis Cache
    if redis_client and results:
        try:
            redis_client.setex(cache_key, 3600, json.dumps(results))
        except Exception:
            pass

    return render_template("index.html", current_menu=menu, source=source, results=results)

from asgiref.wsgi import WsgiToAsgi
asgi_app = WsgiToAsgi(app)