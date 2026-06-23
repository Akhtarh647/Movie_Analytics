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
# 1. ENVIRONMENT VARIABLES (Non-Sensitive Configurations)
# =================================================================
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "plated-client-499118-m4")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "movies")
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")

# =================================================================
# 2. GOOGLE SECRET MANAGER INTEGRATION
# =================================================================
def get_secret(secret_id, project_id=GCP_PROJECT_ID, version_id="latest"):
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8").strip()
    except Exception as e:
        # Fallback to local environment variables if Secret Manager is not accessible locally
        print(f"Secret Manager Error for {secret_id}: {str(e)}")
        return os.getenv(secret_id.upper().replace("-", "_"))

# Dynamic secrets retrieval from Google Cloud Secret Manager
TMDB_API_KEY = get_secret("tmdb-api-key")
DB_USER = get_secret("database-user")
DB_PASSWORD = get_secret("database-password")

# =================================================================
# 3. BACKEND INFRASTRUCTURE CONNECTIONS (Redis & PostgreSQL)
# =================================================================
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True, socket_connect_timeout=2)
except Exception:
    redis_client = None

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

# =================================================================
# 4. ROUTING LOGIC WITH CACHING & METRICS LOGGING
# =================================================================
@app.route('/')
def index():
    menu = request.args.get('menu', 'movies')
    cache_key = f"trending_{menu}_cache"
    source = "Redis Cache"

    # Step A: Check Redis Cache for Instant Serving
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return render_template("index.html", current_menu=menu, source=source, results=json.loads(cached_data))
        except Exception:
            pass

    # Step B: Cache Miss -> Fetch Fresh Data via Secret Key Managed Endpoint
    source = "Live API + Cloud SQL Logged"
    results = []
    
    try:
        if menu == "movies":
            url = "https://api.themoviedb.org/3/trending/movie/day"
            response = requests.get(url, params={"api_key": TMDB_API_KEY})
            results = response.json().get("results", [])[:10]
        elif menu == "tv":
            url = "https://api.themoviedb.org/3/trending/tv/day"
            response = requests.get(url, params={"api_key": TMDB_API_KEY})
            results = response.json().get("results", [])[:10]
        elif menu == "dramas":
            url = "https://api.themoviedb.org/3/discover/tv"
            params = {
                "api_key": TMDB_API_KEY,
                "with_genres": "18",
                "sort_by": "popularity.desc"
            }
            response = requests.get(url, params=params)
            results = response.json().get("results", [])[:10]
    except Exception:
        results = []

    # Step C: Log Request Transaction inside PostgreSQL (Using User and Password from Secrets)
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

    # Step D: Cache Data in Redis for Future Quick Loads (1 Hour Expiry)
    if redis_client and results:
        try:
            redis_client.setex(cache_key, 3600, json.dumps(results))
        except Exception:
            pass

    return render_template("index.html", current_menu=menu, source=source, results=results)

# Uvicorn interface entrypoint wrapper
from asgiref.wsgi import WsgiToAsgi
asgi_app = WsgiToAsgi(app)