"""API FastAPI pour la prediction du rendement agricole (Yield_tons_per_hectare).

Le modele (Pipeline sklearn : preprocessing + regression) est telecharge au
demarrage depuis le Hub Hugging Face (leskimou/projet_12, fichier model.pkl).
"""

from contextlib import asynccontextmanager
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI
from huggingface_hub import hf_hub_download
from pydantic import BaseModel, Field

HF_REPO_ID = "leskimou/projet_12"
HF_FILENAME = "model.pkl"

CROPS = ["Barley", "Cotton", "Maize", "Rice", "Soybean", "Wheat"]
REGIONS = ["East", "North", "South", "West"]
SOIL_TYPES = ["Chalky", "Clay", "Loam", "Peaty", "Sandy", "Silt"]
WEATHER_CONDITIONS = ["Cloudy", "Rainy", "Sunny"]

model = None  # charge au demarrage (lifespan)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    model_path = hf_hub_download(repo_id=HF_REPO_ID, filename=HF_FILENAME)
    model = joblib.load(model_path)
    yield


app = FastAPI(title="Crop Yield API", lifespan=lifespan)


class Context(BaseModel):
    Region: Literal["East", "North", "South", "West"]
    Soil_Type: Literal["Chalky", "Clay", "Loam", "Peaty", "Sandy", "Silt"]
    Rainfall_mm: float
    Temperature_Celsius: float
    Fertilizer_Used: bool
    Irrigation_Used: bool
    Weather_Condition: Literal["Cloudy", "Rainy", "Sunny"]
    Days_to_Harvest: int
    Pesticides_tonnes_avg_proxy: float | None = Field(
        default=None, description="Optionnel, impute par le modele si absent"
    )


class PredictRequest(Context):
    Crop: Literal["Barley", "Cotton", "Maize", "Rice", "Soybean", "Wheat"]


class PredictResponse(BaseModel):
    Crop: str
    predicted_yield: float


def _predict_for_crops(context: Context, crops: list[str]) -> list[PredictResponse]:
    rows = pd.DataFrame([{**context.model_dump(), "Crop": crop} for crop in crops])
    predictions = model.predict(rows)
    return [
        PredictResponse(Crop=crop, predicted_yield=float(pred))
        for crop, pred in zip(crops, predictions)
    ]


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    context = Context(**request.model_dump(exclude={"Crop"}))
    return _predict_for_crops(context, [request.Crop])[0]


@app.post("/recommend", response_model=list[PredictResponse])
def recommend(context: Context) -> list[PredictResponse]:
    results = _predict_for_crops(context, CROPS)
    return sorted(results, key=lambda r: r.predicted_yield, reverse=True)
