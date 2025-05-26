from airflow.decorators import dag, task
from datetime import timedelta
import subprocess
import mlflow
import pickle
import os
import pendulum

DATASETS = ["sample", "full"]
MLFLOW_URI = "http://host.docker.internal:5001"
EXPERIMENT_NAME = "telecom-churn"

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="churn_train_mlflow_dag",
    default_args=default_args,
    schedule=None,
    start_date=pendulum.datetime(2025, 5, 25, tz="UTC"),
    tags=["mlflow", "churn"],
)
def churn_training_pipeline():

    @task
    def train_model(dataset: str):
        print(f"📦 Training model on: {dataset}")
        subprocess.run([
            "python", "/opt/mlflow/train.py",
            "--dataset", dataset,
            "--n_estimators", "100",
            "--max_depth", "6",
            "--mlflow_uri", MLFLOW_URI
        ], check=True)

    @task
    def pick_and_register_best_model():
        print("🔎 Selecting best model by AUC...")

        mlflow.set_tracking_uri(MLFLOW_URI)
        client = mlflow.tracking.MlflowClient()
        experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)

        if not experiment:
            raise ValueError("Experiment 'telecom-churn' not found.")

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["metrics.auc DESC"],
            max_results=5,
        )

        if not runs:
            raise ValueError("No runs found in experiment.")

        best_run = runs[0]
        run_id = best_run.info.run_id
        client.set_tag(run_id, "best_model", "true")

        print(f"✅ Best run: {run_id}, AUC: {best_run.data.metrics.get('auc')}")

        # === Register model
        model_uri = f"runs:/{run_id}/model"
        model_name = "telecom_churn_model"

        result = mlflow.register_model(model_uri=model_uri, name=model_name)
        print(f"📦 Registered model: {result.name}, version: {result.version}")

        # === Save model as .pkl
        local_dir = "/opt/airflow/model_pickles"
        os.makedirs(local_dir, exist_ok=True)
        local_pickle_path = os.path.join(local_dir, f"best_model_{run_id}.pkl")

        model = mlflow.sklearn.load_model(model_uri)
        with open(local_pickle_path, "wb") as f:
            pickle.dump(model, f)

        print(f"✅ Saved pickle: {local_pickle_path}")
        return run_id

    # Training tasks per dataset
    trained_models = [train_model(ds) for ds in DATASETS]

    # Evaluate and label best model
    best = pick_and_register_best_model()

    trained_models >> best


churn_training_pipeline()
