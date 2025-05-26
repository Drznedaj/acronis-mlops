#!/bin/bash

# Build and push to local registry
docker build -t mlflow-model-api .
docker tag mlflow-model-api localhost:5000/mlflow-model-api
docker push localhost:5000/mlflow-model-api

# Run container from local registry
docker run -d --name model-api \
  -p 8000:8000 \
  -e MLFLOW_TRACKING_URI=http://host.docker.internal:5001 \
  localhost:5000/mlflow-model-api
