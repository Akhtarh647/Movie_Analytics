resource "google_cloud_run_v2_service" "app_service" {
  name     = "movie-analytics-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      # -----------------------------------------------------------------
      # BOOTSTRAP TRICK: Is temporary line ko use karein taaki terraform apply bina image ke pass ho jaye.
      # Jab GitHub Actions chalega, toh woh is image ko automatically replace kar dega.
      # -----------------------------------------------------------------
      image = "gcr.io/cloudrun/hello"

      # Real image path jo aap baad mein update karenge (Keep it commented for now):
      # image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.movie_app_repo.repository_id}/movie-app:latest"

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

    vpc_access {
      network_interfaces {
        network    = google_compute_network.vpc.id
        subnetwork = google_compute_subnetwork.private.id
      }
      egress = "ALL_TRAFFIC"
    }
  }

  # Is block mein repository aur secrets dono ka wait karna zaroori hai
  depends_on = [
    google_sql_database_instance.postgres,
    google_redis_instance.cache,
    google_secret_manager_secret_version.db_password_val,
    google_artifact_registry_repository.movie_app_repo,
    google_secret_manager_secret_iam_member.db_password_accessor,
    google_secret_manager_secret_iam_member.tmdb_api_accessor
  ]
}

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.app_service.name
  location = google_cloud_run_v2_service.app_service.location
  role     = "roles/run.viewer"
  member   = "allUsers"
}