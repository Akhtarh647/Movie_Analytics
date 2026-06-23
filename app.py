from fastapi import FastAPI, Depends, HTTPException
import os
import redis
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import json

app = FastAPI(title="FastAPI Movie Analytics")

# Environment Variables config (From Cloud Run deployment settings)
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "movie_admin")
DB_NAME = os.getenv("DB_NAME", "movies")
DB_PASSWORD = os.getenv("DB_PASSWORD", "SecurePassword123!")
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")

TMDB_API_KEY = "f676b00029651576a5a060c3ac7e1167"
TMDB_LANGUAGE = "en-US"

# Initialize Redis Client connection
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True, socket_connect_timeout=2)
except Exception:
    redis_client = None

# Connection helper for Cloud SQL PostgreSQL
def get_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        yield conn
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.get("/")
def root():
    return {"status": "running", "platform": "FastAPI + Redis + PostgreSQL"}

@app.get("/trending/{content_type}")
def get_trending(content_type: str, db = Depends(get_db)):
    if content_type not in ["movie", "tv"]:
        raise HTTPException(status_code=400, detail="Invalid content type. Use 'movie' or 'tv'.")

    cache_key = f"trending_{content_type}"

    # 1. Check Redis cache first
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return {"source": "Redis Cache", "results": json.loads(cached_data)}
        except Exception:
            pass

    # 2. Cache miss -> Call TMDB API
    url = f"https://api.themoviedb.org/3/trending/{content_type}/day"
    params = {"api_key": TMDB_API_KEY, "language": TMDB_LANGUAGE}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch from TMDB")

    results = response.json().get("results", [])[:10]

    # 3. Store raw structures inside Cloud SQL PostgreSQL (Log search metrics or audit metadata)
    try:
        cursor = db.cursor()
        # Creating sample system log table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_logs (
                id SERIAL PRIMARY KEY,
                search_type VARCHAR(50),
                results_count INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute(
            "INSERT INTO search_logs (search_type, results_count) VALUES (%s, %s);",
            (cache_key, len(results))
        )
        db.commit()
        cursor.close()
    except Exception:
        pass

    # 4. Save into Redis cache for 1 hour (3600 seconds)
    if redis_client:
        try:
            redis_client.setex(cache_key, 3600, json.dumps(results))
        except Exception:
            pass

    return {"source": "Live TMDB API + DB Logged", "results": results}