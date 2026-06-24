# ==========================================
# 1. DATABASE PASSWORD SECRET & VERSION
# ==========================================
resource "google_secret_manager_secret" "db_password" {
  secret_id = "database-password" # Live console se 100% match
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password_val" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = "SecurePassword123"
}

# ==========================================
# 2. TMDB API KEY SECRET SLOT ONLY
# ==========================================
resource "google_secret_manager_secret" "tmdb_api_key" {
  secret_id = "tmdb-api-key" # Live console se 100% match
  replication {
    auto {}
  }
}

# ==========================================
# 3. IAM PERMISSIONS FOR CLOUD RUN SERVICE ACCOUNT (sa-700)
# ==========================================
resource "google_secret_manager_secret_iam_member" "db_password_accessor" {
  secret_id = google_secret_manager_secret.db_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:sa-700@plated-client-499118-m4.iam.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "tmdb_api_accessor" {
  secret_id = google_secret_manager_secret.tmdb_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:sa-700@plated-client-499118-m4.iam.gserviceaccount.com"
}