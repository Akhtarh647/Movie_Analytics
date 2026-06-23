resource "google_cloud_run_v2_service" "app_service" {
  name     = "movie-analytics-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL" # Allows public internet traffic to reach your API

  template {
    containers {
      # Points to your image path in Artifact Registry
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.movie_app_repo.repository_id}/movie-app:latest"

      # Injects standard environment configurations
      env {
        name  = "DB_HOST"
        value = google_sql_database_instance.postgres.private_ip_address
      }
      env {
        name  = "DB_USER"
        value = google_sql_user.db_user.name
      }
      env {
        name  = "DB_NAME"
        value = google_sql_database.movie_db.name
      }
      env {
        name  = "REDIS_HOST"
        value = google_redis_instance.cache.host
      }

      # Mounts credentials securely directly out of Secret Manager
      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_password.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "TMDB_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.tmdb_api_key.secret_id
            version = "latest"
          }
        }
      }
    }

    # Connects Cloud Run directly inside your private network subnets
    vpc_access {
      network_interfaces {
        network    = google_compute_network.vpc.id
        subnetwork = google_compute_subnetwork.private.id
      }
      egress = "ALL_TRAFFIC" # Routes all outbound API traffic (like TMDB calls) through Cloud NAT
    }
  }

  # Ensure resources are built sequentially to avoid dependency failures
  depends_on = [
    google_sql_database_instance.postgres,
    google_redis_instance.cache,
    google_secret_manager_secret_version.db_password_val
  ]
}

# Makes the Cloud Run API publicly accessible without requiring IAM tokens
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.app_service.name
  location = google_cloud_run_v2_service.app_service.location
  role     = "roles/run.viewer"
  member   = "allUsers"
}