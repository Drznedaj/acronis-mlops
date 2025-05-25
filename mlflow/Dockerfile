FROM python:3.12-slim

RUN pip install mlflow scikit-learn pandas matplotlib

RUN useradd -m -u 1000 mlflow && \
    mkdir -p /mlflow/db /mlflow/artifacts && \
    chown -R mlflow:mlflow /mlflow && \
    chmod -R 755 /mlflow

USER mlflow

EXPOSE 5000