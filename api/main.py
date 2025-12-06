import os
import joblib
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# ------------------------------
# Correct Model Directory Setup
# ------------------------------

# BASE_DIR = FWI Predicator/
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# model directory path
MODEL_DIR = os.path.join(BASE_DIR, "model")

# Full file paths of model & scaler
MODEL_PATH = os.path.join(MODEL_DIR, "fwi_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

print("Loading Model From:", MODEL_PATH)
print("Loading Scaler From:", SCALER_PATH)

# Load model and scaler
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# ------------------------------
# Input Schema
# ------------------------------
class FWIInput(BaseModel):
    Temperature: float
    RH: float
    Ws: float
    Rain: float
    FFMC: float
    DMC: float
    DC: float
    ISI: float
    BUI: float

# ------------------------------
# Prediction API
# ------------------------------
@app.post("/predict")
def predict_fwi(data: FWIInput):

    user_data = [[
        data.Temperature, data.RH, data.Ws, data.Rain,
        data.FFMC, data.DMC, data.DC, data.ISI, data.BUI
    ]]

    # Scale input
    scaled = scaler.transform(user_data)

    # Predict
    prediction = model.predict(scaled)[0]

    return {"FWI_prediction": float(prediction)}
