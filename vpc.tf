# =================================================================
# 1. NETWORK CORE (VPC & SUBNETS)
# =================================================================
resource "google_compute_network" "vpc" {
  name                    = "movie-analytics-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "public" {
  name          = "public-subnet"
  ip_cidr_range = var.public_subnet_cidr
  region        = var.region
  network       = google_compute_network.vpc.id
}

resource "google_compute_subnetwork" "private" {
  name                     = "private-subnet"
  ip_cidr_range            = var.private_subnet_cidr
  region                   = var.region
  network                  = google_compute_network.vpc.id
  private_ip_google_access = true
}

# =================================================================
# 2. PRIVATE NETWORKING INTERFACES (Peering & Connectors)
# =================================================================
resource "google_compute_global_address" "private_ip_alloc" {
  name          = "private-ip-alloc"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]
}

# SERVERLESS CONNECTOR: Yeh block Cloud Run ko internal VPC se jodta hai
resource "google_vpc_access_connector" "connector" {
  name          = "cloudrun-vpc-conn"
  region        = var.region
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.8.0.0/28"
}

# =================================================================
# 3. INTERNET ROUTING GATEWAYS (NAT)
# =================================================================
resource "google_compute_router" "router" {
  name    = "nat-router"
  region  = var.region
  network = google_compute_network.vpc.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "vpc-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"

  subnetwork {
    name                    = google_compute_subnetwork.private.id
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }
}

# =================================================================
# 4. STORAGE & STATE MANAGEMENT (PostgreSQL Instance)
# =================================================================
resource "google_sql_database_instance" "postgres" {
  name             = "movie-analytics-db"
  database_version = "POSTGRES_15"
  region           = var.region
  depends_on       = [google_service_networking_connection.private_vpc_connection]

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = google_compute_network.vpc.id
      enable_private_path_for_google_cloud_services = true
    }

    backup_configuration {
      enabled    = true
      start_time = "02:00"
    }
  }
  deletion_protection = false
}

resource "google_sql_database" "movie_db" {
  name     = "movies"
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "db_user" {
  name     = "movie_admin"
  instance = google_sql_database_instance.postgres.name
  password = "SecurePassword123!"
}

# =================================================================
# 5. SERVERLESS COMPUTE LAYER (Cloud Run Service)
# =================================================================
resource "google_cloud_run_v2_service" "web_app" {
  name     = "movie-analytics-app"
  location = var.region

  template {
    # Is block se Cloud Run ke paas direct VPC connector ki capabilities aa jati hain
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/movie-repo/backend:latest"

      ports {
        container_port = 8080
      }

      # Run-time environment logging declarations
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "DB_HOST"
        value = google_sql_database_instance.postgres.private_ip_address
      }
      env {
        name  = "DB_NAME"
        value = google_sql_database.movie_db.name
      }
      env {
        name  = "REDIS_HOST"
        value = "127.0.0.1" # Standard single layer sandbox loop
      }
    }
  }
}

# Public access block configuration for Cloud Run
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.web_app.name
  location = google_cloud_run_v2_service.web_app.location
  role     = "roles/run.viewer"
  member   = "allUsers"
}