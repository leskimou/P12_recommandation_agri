import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main  # noqa: E402


class DummyModel:
    """Rendement fixe par culture, pour verifier deterministiquement le tri de /recommend."""

    CROP_YIELD = {
        "Wheat": 5.0,
        "Maize": 4.0,
        "Rice": 3.0,
        "Barley": 2.0,
        "Soybean": 1.0,
        "Cotton": 0.5,
    }

    def predict(self, rows: pd.DataFrame):
        return rows["Crop"].map(self.CROP_YIELD).to_numpy()


VALID_CONTEXT = {
    "Region": "East",
    "Soil_Type": "Clay",
    "Rainfall_mm": 550.0,
    "Temperature_Celsius": 25.0,
    "Fertilizer_Used": True,
    "Irrigation_Used": True,
    "Weather_Condition": "Sunny",
    "Days_to_Harvest": 100,
}


@pytest.fixture
def client():
    """TestClient avec un modele factice : evite tout appel reseau vers Hugging Face."""
    with (
        patch("main.hf_hub_download", return_value="dummy/path"),
        patch("main.joblib.load", return_value=DummyModel()),
    ):
        with TestClient(main.app) as test_client:
            yield test_client
