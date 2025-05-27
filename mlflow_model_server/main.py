import logging
import time
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from model_loader import load_model

# Setup logging
logging.basicConfig(
    filename="/opt/models/model_server.log",  # this is inside mounted volume
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = FastAPI()

class InputData(BaseModel):
    data: list[dict]

@app.post("/predict")
def predict(input_data: InputData):
    start_time = time.time()
    try:
        model = load_model()
        df = pd.DataFrame(input_data.data)
        preds = model.predict(df)

        duration = round((time.time() - start_time) * 1000, 2)
        logging.info(f"Prediction_count={len(preds)} duration_ms={duration}")
        return {"predictions": preds.tolist()}
    except Exception as e:
        logging.error(f"Prediction_failed error={str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
