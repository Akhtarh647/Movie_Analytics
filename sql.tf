# 1. Cloud SQL PostgreSQL Instance
resource "google_sql_database_instance" "postgres" {
  name             = "movie-analytics-db"
  database_version = "POSTGRES_15"
  region           = var.region

  # Ensures VPC peering is fully running before creating the database
  depends_on = [google_service_networking_connection.private_vpc_connection]

  settings {
    tier = "db-f1-micro" # Development tier. For production, scale up (e.g., db-custom-2-7680)

    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = google_compute_network.vpc.id
      enable_private_path_for_google_cloud_services = true
    }

    backup_configuration {
      enabled    = true
      start_time = "02:00" # Automated daily backups at 2 AM
    }
  }

  # Avoids accidental deletion of your database when running terraform destroy
  deletion_protection = false
}

# 2. PostgreSQL Database
resource "google_sql_database" "movie_db" {
  name     = "movies"
  instance = google_sql_database_instance.postgres.name
}

# 3. Database Master User
resource "google_sql_user" "db_user" {
  name     = "movie_admin"
  instance = google_sql_database_instance.postgres.name
  password = "SecurePassword123!" # Ideally sourced via Secret Manager or a TF variable
}