terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }

  required_version = ">= 1.1.0"
}

provider "docker" {}

resource "docker_network" "mlflow_net" {
  name = "mlflow_network"
}

resource "docker_image" "registry" {
  name = "registry:2"
}

resource "docker_container" "registry" {
  name  = "local_registry"
  image = docker_image.registry.name
  ports {
    internal = 5050
    external = 5050
  }
  networks_advanced {
    name = docker_network.mlflow_net.name
  }
}

resource "docker_image" "mlflow" {
  name = "mlflow:local"
  build {
    context = abspath("${path.module}/../mlflow")
  }
}

resource "docker_volume" "mlflow_db" {
  name = "mlflow_db"
}

resource "docker_volume" "mlflow_artifacts" {
  name = "mlflow_artifacts"
}

resource "docker_container" "mlflow" {
  name  = "mlflow_server"
  image = docker_image.mlflow.name

  ports {
    internal = 5000
    external = 5001
  }

  volumes {
    volume_name    = docker_volume.mlflow_db.name
    container_path = "/mlflow/db"
  }

  volumes {
    volume_name    = docker_volume.mlflow_artifacts.name
    container_path = "/mlflow/artifacts"
  }

  networks_advanced {
    name = docker_network.mlflow_net.name
  }

  command = [
    "mlflow", "server",
    "--backend-store-uri", "sqlite:////mlflow/db/mlflow.db",
    "--default-artifact-root", "file:/mlflow/artifacts",
    "--artifacts-destination", "/mlflow/artifacts",
    "--serve-artifacts",
    "--host", "0.0.0.0"
  ]
}
