resource "google_redis_instance" "cache" {
  name               = "movie-cache"
  tier               = "BASIC"
  memory_size_gb     = 1
  region             = var.region
  authorized_network = google_compute_network.vpc.id

  connect_mode = "PRIVATE_SERVICE_ACCESS"

  # Requires the private VPC connection peering from vpc.tf to be live first
  depends_on = [google_service_networking_connection.private_vpc_connection]
}