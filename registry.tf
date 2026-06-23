resource "google_artifact_registry_repository" "movie_app_repo" {
  location      = var.region
  repository_id = "movie-analytics-repo"
  description   = "Docker repository for the Movie Analytics backend application"
  format        = "DOCKER"
}