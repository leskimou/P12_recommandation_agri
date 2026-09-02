"""Tests fonctionnels : appels HTTP reels via TestClient, modele mocke (DummyModel)."""

from conftest import VALID_CONTEXT


def test_health_reports_model_loaded(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model_loaded": True}


def test_predict_returns_yield_for_crop(client):
    response = client.post("/predict", json={**VALID_CONTEXT, "Crop": "Wheat"})
    assert response.status_code == 200
    assert response.json() == {"Crop": "Wheat", "predicted_yield": 5.0}


def test_predict_rejects_invalid_crop(client):
    response = client.post("/predict", json={**VALID_CONTEXT, "Crop": "Potato"})
    assert response.status_code == 422


def test_predict_rejects_out_of_range_field(client):
    response = client.post("/predict", json={**VALID_CONTEXT, "Crop": "Wheat", "Rainfall_mm": -5})
    assert response.status_code == 422


def test_recommend_returns_all_crops_sorted_desc(client):
    response = client.post("/recommend", json=VALID_CONTEXT)
    assert response.status_code == 200
    body = response.json()
    assert [r["Crop"] for r in body] == ["Wheat", "Maize", "Rice", "Barley", "Soybean", "Cotton"]
    yields = [r["predicted_yield"] for r in body]
    assert yields == sorted(yields, reverse=True)


def test_recommend_rejects_missing_field(client):
    payload = {k: v for k, v in VALID_CONTEXT.items() if k != "Region"}
    response = client.post("/recommend", json=payload)
    assert response.status_code == 422
