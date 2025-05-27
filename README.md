# 📊 Churn Prediction ML Pipeline

A fully containerized end-to-end MLOps pipeline for customer churn prediction, featuring:

- 🧠 **Model Training & Tracking** with MLflow
- 🎯 **Model Selection** & Registration
- 🚀 **Model Deployment** with FastAPI
- ⚙️ **Workflow Orchestration** via Apache Airflow
- 📦 **Deployment** using Terraform and Docker
- 🧪 **Serving** models via `/predict` API and storing `.pkl` artifacts
- 📈 **Basic Monitoring** via log-based latency/error tracking

---

## 📁 Project Structure

```
.
├── airflow/                  # Airflow DAGs and configs
│   └── dags/churn_train_dag.py
|   └── models/               # Pickled model artifacts (volume mounted)
├── mlflow/                   # MLflow training script and Dockerfile
│   └── train.py
├── mlflow_model_server/      # FastAPI model server
│   ├── main.py
│   ├── model_loader.py
│   ├── Dockerfile
│   ├── requirements.txt
├── data/                    # Training data (mounted into container)
│   └── telecom_customer_churn.csv
├── terraform/
│   └── main.tf              # Terraform config for all containers & volumes
├── monitor_model_server.sh  # Monitoring script for latency & errors
└── README.md
```

---

## 🚀 Getting Started

### 1. ✅ Prerequisites

- [Docker](https://www.docker.com/)
- [Terraform](https://developer.hashicorp.com/terraform/downloads)
- Python 3.12+ (for local tests)

---

### 2. 🛠️ Run the Full System

```bash
cd terraform/
terraform init
terraform apply --auto-approve
```

This will spin up:

- MLflow tracking server (`localhost:5001`)
- Model API server (`localhost:8000`)
- Local Docker registry (`localhost:5050`)

Then spin up Airflow with:

```bash
docker compose up -d
```

---

### 3. 🔄 Run the DAG

Go to Airflow at [http://localhost:8080](http://localhost:8080):

- Trigger the `churn_train_mlflow_dag`
- It will:
  - Train models for different datasets
  - Log metrics, plots, and artifacts to MLflow
  - Pick the best model
  - Register and promote it to "Production"
  - Save it as a `.pkl` in `/model_pickles`
  - Update `best_model.pkl` for serving

---

## 🔬 Predicting with FastAPI

```bash
curl -X POST http://localhost:8000/predict   -H "Content-Type: application/json"   -d @mlflow_model_server input_example.json
```

### ✅ Example Response

```json
{
  "predictions": [0]
}
```

---

## 📦 Artifacts & Model Registry

- MLflow UI: [http://localhost:5001](http://localhost:5001)
- Registered models: `telecom_churn_model`
- Pickled models stored at `./models/`

---

## 🔍 API Endpoints

| Route         | Method | Description                      |
|---------------|--------|----------------------------------|
| `/predict`    | POST   | Predict from input JSON          |

---

## 📈 Basic Monitoring

App logs prediction latency and errors to `/models/model_server.log`.

Run the included script:

```bash
./monitor_model_server.sh
```

You’ll get output like:

```bash
📊 Model Server Monitoring Report
🔹 Total requests this hour: 48
⏱️  Average prediction latency: 113ms
❌ Prediction errors this hour: 1
⚠️  Alerts:
 - All clear ✅
```

---

## 🧼 Cleaning Up

To stop and remove everything:

```bash
terraform destroy --auto-approve
```

And for Airflow:

```bash
docker compose down
```

To reset local registry or volumes:

```bash
docker volume rm $(docker volume ls -q | grep model)
docker rm -f local_registry mlflow_server model_api
```
