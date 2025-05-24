FROM python:3.12-slim

RUN pip install mlflow scikit-learn pandas matplotlib

EXPOSE 5000

ENTRYPOINT ["mlflow"]
CMD ["server", "--backend-store-uri", "sqlite:///mlflow.db", "--default-artifact-root", "/mlflow/artifacts", "--host", "0.0.0.0"]
