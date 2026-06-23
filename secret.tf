# Create Database Password Secret
resource "google_secret_manager_secret" "db_password" {
  secret_id = "database-password"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password_val" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = "SecurePassword123!" # Matches your database user password
}

# Create TMDB API Key Secret Slot (Value can be updated via Console later)
resource "google_secret_manager_secret" "tmdb_api_key" {
  secret_id = "tmdb-api-key"
  replication {
    auto {}
  }
}

# Automatically grants Secret Accessor role to the exact Cloud Run service account
resource "google_secret_manager_secret_iam_member" "db_password_accessor" {
  secret_id = google_secret_manager_secret.db_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:207352957358-compute@developer.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "tmdb_api_accessor" {
  secret_id = google_secret_manager_secret.tmdb_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:207352957358-compute@developer.gserviceaccount.com"
}