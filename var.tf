variable "project_id" {
  type        = string
  description = "The GCP Project ID where all resources will be deployed."
  default     = "plated-client-499118-m4"
}

variable "region" {
  type        = string
  description = "The default GCP region for regional infrastructure components."
  default     = "us-central1"
}

variable "public_subnet_cidr" {
  type        = string
  description = "The IP range (CIDR) block allocated for the public web/frontend subnet."
  default     = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  type        = string
  description = "The IP range (CIDR) block allocated for private application backends, databases, and caches."
  default     = "10.0.2.0/24"
}