import pytest

pytest.importorskip('httpx')
from fastapi.testclient import TestClient
pytest.importorskip('pandas')
pytest.importorskip('sklearn')

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from unittest.mock import patch

from mlflow_model_server.main import app


def test_predict_endpoint():
    # Train simple model
    X = pd.DataFrame({'f1': [0, 1], 'f2': [0, 1]})
    y = [0, 1]
    model = RandomForestClassifier(n_estimators=1, random_state=0)
    model.fit(X, y)

    input_payload = {"data": [{"f1": 0, "f2": 0}, {"f1": 1, "f2": 1}]}

    with patch('mlflow_model_server.main.load_model', return_value=model):
        client = TestClient(app)
        response = client.post('/predict', json=input_payload)

    assert response.status_code == 200
    body = response.json()
    assert 'predictions' in body
    assert len(body['predictions']) == len(input_payload['data'])
