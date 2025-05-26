from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from model_loader import load_model

app = FastAPI()

class InputData(BaseModel):
    data: list[dict]

@app.post("/predict")
def predict(input_data: InputData):
    try:
        model = load_model()
        df = pd.DataFrame(input_data.data)
        preds = model.predict(df)
        return {"predictions": preds.tolist()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
