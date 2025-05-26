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

resource "docker_volume" "mlflow_storage" {
  name = "mlflow_storage"
  
  driver_opts = {
    type   = "none"
    device = "/Users/nemanjazaric/repos/acronis-mlops/mlflow"
    o      = "bind"
  }
}

resource "docker_container" "mlflow" {
  name  = "mlflow_server"
  image = docker_image.mlflow.name

  ports {
    internal = 5000
    external = 5001
  }

  # Single volume mounted at /mlflow
  volumes {
    volume_name    = docker_volume.mlflow_storage.name
    container_path = "/tmp/mlflow"
    read_only      = false
  }

  networks_advanced {
    name = docker_network.mlflow_net.name
  }

  command = [
    "mlflow", "server",
    "--backend-store-uri", "sqlite:////mlflow/db/mlflow.db",
    "--default-artifact-root", "file:/tmp/mlflow/artifacts",
    "--artifacts-destination", "/tmp/mlflow/artifacts",
    "--serve-artifacts",
    "--host", "0.0.0.0"
  ]
}

resource "docker_image" "mlflow_model_api" {
  name = "mlflow-model-api"
  build {
    context = abspath("${path.module}/../mlflow_model_server")
  }
}

resource "docker_volume" "models" {
  name = "models"

  driver_opts = {
    type   = "none"
    device = "/Users/nemanjazaric/repos/acronis-mlops/airflow/models"
    o      = "bind"
  }
}

resource "docker_container" "model_api" {
  name  = "model_api"
  image = docker_image.mlflow_model_api.name

  ports {
    internal = 8000
    external = 8000
  }

  env = [
    "MLFLOW_TRACKING_URI=http://mlflow:5001"
  ]

  volumes {
    volume_name    = docker_volume.models.name
    container_path = "/opt/models"
    read_only      = true
  }

  networks_advanced {
    name = docker_network.mlflow_net.name
  }

  depends_on = [
    docker_container.mlflow
  ]

  command = [
    "uvicorn", "main:app",
    "--host", "0.0.0.0",
    "--port", "8000"
  ]
}
