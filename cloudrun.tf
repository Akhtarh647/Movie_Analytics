# =================================================================
# SERVERLESS COMPUTE LAYER (Cloud Run Service)
# =================================================================
resource "google_cloud_run_v2_service" "app_service" {
  name     = "movie-analytics-app" # GitHub Actions isi naam ko target kar raha hai
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    # Identity Assigning for Secret Manager Access
    service_account = "sa-700@plated-client-499118-m4.iam.gserviceaccount.com"

    containers {
      # Bootstrap image jo initial apply par pipeline block nahi karegi
      image = "gcr.io/cloudrun/hello"

      # AUTOMATED ENVIRONMENT VARIABLES (No Manual Work)
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "DB_HOST"
        value = google_sql_database_instance.postgres.private_ip_address # Live DB IP Automatic
      }
      env {
        name  = "DB_NAME"
        value = google_sql_database.movie_db.name # Live DB Name Automatic
      }
      env {
        name  = "DB_USER"
        value = google_sql_user.db_user.name # Dynamic connection with movie_admin
      }
      env {
        name  = "REDIS_HOST"
        value = google_redis_instance.cache.host # Live Redis IP Automatic
      }

      # SECRETS FETCHED VIA SECRET MANAGER
      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_password.secret_id
            version = "latest"
          }
        }
      }

      # TMDB API KEY FETCHED VIA SECRET MANAGER FROM LIVE CONSOLE
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

  depends_on = [
    google_sql_database_instance.postgres,
    google_redis_instance.cache,
    google_secret_manager_secret_iam_member.db_password_accessor,
    google_secret_manager_secret_iam_member.tmdb_api_accessor
  ]
}

# Public access block configuration for Cloud Run
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.app_service.name
  location = google_cloud_run_v2_service.app_service.location
  role     = "roles/run.viewer"
  member   = "allUsers"
}