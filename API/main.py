"""API FastAPI pour la prediction du rendement agricole (Yield_tons_per_hectare).

Le modele (Pipeline sklearn : preprocessing + regression) est telecharge au
demarrage depuis le Hub Hugging Face (leskimou/projet_12, fichier model.pkl).
"""

import os
from contextlib import asynccontextmanager
from typing import Literal

import joblib
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader
from huggingface_hub import hf_hub_download
from pydantic import BaseModel, ConfigDict, Field

HF_REPO_ID = "leskimou/projet_12"
HF_FILENAME = "model.pkl"

API_KEY = os.environ.get("API_KEY")
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

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


def require_api_key(key: str | None = Depends(_api_key_header)) -> None:
    # ponytail: pas de cle -> auth desactivee (dev local), a definir en prod/Docker Hub
    if API_KEY and key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


class Context(BaseModel):
    model_config = ConfigDict(extra="forbid")

    Region: Literal["East", "North", "South", "West"]
    Soil_Type: Literal["Chalky", "Clay", "Loam", "Peaty", "Sandy", "Silt"]
    Rainfall_mm: float = Field(ge=100.0, le=1000.0, description="Precipitations en mm")
    Temperature_Celsius: float = Field(ge=15.0, le=40.0)
    Fertilizer_Used: bool
    Irrigation_Used: bool
    Weather_Condition: Literal["Cloudy", "Rainy", "Sunny"]
    Days_to_Harvest: int = Field(ge=60, le=149)
    Pesticides_tonnes_avg_proxy: float | None = Field(
        default=None, ge=13735.0, le=20043.0, description="Optionnel, impute par le modele si absent"
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


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict", response_model=PredictResponse, dependencies=[Depends(require_api_key)])
def predict(request: PredictRequest) -> PredictResponse:
    context = Context(**request.model_dump(exclude={"Crop"}))
    return _predict_for_crops(context, [request.Crop])[0]


@app.post("/recommend", response_model=list[PredictResponse], dependencies=[Depends(require_api_key)])
def recommend(context: Context) -> list[PredictResponse]:
    results = _predict_for_crops(context, CROPS)
    return sorted(results, key=lambda r: r.predicted_yield, reverse=True)
