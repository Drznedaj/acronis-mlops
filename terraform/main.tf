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
    context = "${path.module}/../mlflow"
  }
}

resource "docker_container" "mlflow" {
  name  = "mlflow_server"
  image = docker_image.mlflow.name
  ports {
    internal = 5001
    external = 5002
  }
  env = [
    "BACKEND_STORE_URI=sqlite:///mlflow.db",
    "ARTIFACT_ROOT=/mlflow/artifacts"
  ]
  volumes {
    host_path      = abspath("${path.module}/../mlflow")
    container_path = "/mlflow"
  }
  networks_advanced {
    name = docker_network.mlflow_net.name
  }
}
