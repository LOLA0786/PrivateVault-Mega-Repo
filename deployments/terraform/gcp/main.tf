provider "google" {
  project = "intent-engine-482103"
  region  = "us-central1"
}

resource "google_container_cluster" "privatevault_cluster" {
  name     = "privatevault-prod-cluster"
  location = "us-central1-a"

  # Enabling Autopilot for "Plug-and-Play" scaling
  enable_autopilot = true

  release_channel {
    channel = "REGULAR"
  }

  ip_allocation_policy {
    cluster_ipv4_cidr_block  = "/14"
    services_ipv4_cidr_block = "/20"
  }
}

output "kubernetes_cluster_name" {
  value = google_container_cluster.privatevault_cluster.name
}
