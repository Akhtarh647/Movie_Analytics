# ==========================================
# 1. DATABASE PASSWORD SECRET & VERSION
# ==========================================

# Create Database Password Secret Slot
resource "google_secret_manager_secret" "db_password" {
  secret_id = "database-password"
  replication {
    auto {}
  }
}

# Create Database Password Actual Version Value
resource "google_secret_manager_secret_version" "db_password_val" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = "SecurePassword123!"
}


# ==========================================
# 2. TMDB API KEY SECRET SLOT ONLY
# ==========================================

# Terraform sirf yeh khali container banayega. Isme koi key hardcoded nahi hai.
resource "google_secret_manager_secret" "tmdb_api_key" {
  secret_id = "tmdb-api-key"
  replication {
    auto {}
  }
}


# ==========================================
# 3. IAM PERMISSIONS FOR CLOUD RUN
# ==========================================

# Grants Secret Accessor role for Database Password
resource "google_secret_manager_secret_iam_member" "db_password_accessor" {
  secret_id = google_secret_manager_secret.db_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:207352957358-compute@developer.gserviceaccount.com"
}

# Grants Secret Accessor role for TMDB API Key
resource "google_secret_manager_secret_iam_member" "tmdb_api_accessor" {
  secret_id = google_secret_manager_secret.tmdb_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:207352957358-compute@developer.gserviceaccount.com"
}