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