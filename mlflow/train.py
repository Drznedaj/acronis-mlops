import argparse
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
import os


def load_and_prepare_data(dataset_type: str) -> tuple:
    df = pd.read_csv(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "data",
            "telecom_customer_churn.csv"
        )
    )

    if dataset_type == "sample":
        df = df.sample(n=1000, random_state=42)

    # Drop irrelevant columns
    df = df.drop(columns=["Customer ID", "Churn Category", "Churn Reason"])

    # Convert Total Charges and others to numeric
    numeric_cols = [
        "Total Charges", "Total Refunds", "Total Extra Data Charges",
        "Total Long Distance Charges", "Total Revenue"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna()

    # Use 'Customer Status' as binary target (Assume: "Churned" is positive class)
    df["Target"] = df["Customer Status"].map({"Churned": 1, "Joined": 0, "Stayed": 0})

    # Drop original status field
    df = df.drop(columns=["Customer Status"])

    # One-hot encode all categoricals
    categorical_cols = df.select_dtypes(include="object").columns
    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    X = df.drop("Target", axis=1)
    y = df["Target"]

    return train_test_split(X, y, test_size=0.2, random_state=42)


def plot_feature_importance(importances, feature_names):
    indices = np.argsort(importances)[::-1]
    plt.figure(figsize=(10, 6))
    plt.title("Feature Importances")
    plt.bar(range(len(importances)), importances[indices], align="center")
    plt.xticks(range(len(importances)), [feature_names[i] for i in indices], rotation=90)
    plt.tight_layout()

    os.makedirs("mlflow/artifacts", exist_ok=True)
    plot_path = "mlflow/artifacts/feature_importance.png"
    plt.savefig(plot_path)
    return plot_path


def train_model(dataset_type, n_estimators, max_depth, mlflow_uri):
    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment("telecom-churn")

    X_train, X_test, y_train, y_test = load_and_prepare_data(dataset_type)

    with mlflow.start_run(run_name=f"{dataset_type}_rf_run"):
        model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)

        # Log params & metrics
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("dataset", dataset_type)

        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("auc", auc)

        # Log feature importance chart
        plot_path = plot_feature_importance(model.feature_importances_, X_train.columns)
        print("Artifact URI:", mlflow.get_artifact_uri())
        mlflow.log_artifact(plot_path)

        # Log model
        mlflow.sklearn.log_model(model, artifact_path="model")
        # os.makedirs("artifacts", exist_ok=True)
        # joblib.dump(model, "artifacts/model.pkl")
        # mlflow.log_artifact("artifacts/model.pkl", artifact_path="model")

        print(f"Logged MLflow run for dataset={dataset_type} with accuracy={acc:.3f}, AUC={auc:.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["sample", "full"], required=True)
    parser.add_argument("--n_estimators", type=int, default=100)
    parser.add_argument("--max_depth", type=int, default=5)
    parser.add_argument("--mlflow_uri", default="http://localhost:5001")
    args = parser.parse_args()

    train_model(
        dataset_type=args.dataset,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        mlflow_uri=args.mlflow_uri,
    )
