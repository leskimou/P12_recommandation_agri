"""Tests unitaires : validation pydantic des entrees, sans HTTP ni modele."""

import pytest
from pydantic import ValidationError

from conftest import VALID_CONTEXT
from main import Context, PredictRequest


def test_valid_context_parses():
    ctx = Context(**VALID_CONTEXT)
    assert ctx.Region == "East"
    assert ctx.Pesticides_tonnes_avg_proxy is None


def test_valid_predict_request_parses():
    req = PredictRequest(**VALID_CONTEXT, Crop="Wheat")
    assert req.Crop == "Wheat"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("Region", "Nowhere"),
        ("Soil_Type", "Concrete"),
        ("Weather_Condition", "Snowy"),
    ],
)
def test_invalid_categorical_rejected(field, value):
    with pytest.raises(ValidationError):
        Context(**{**VALID_CONTEXT, field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("Rainfall_mm", 99.9),
        ("Rainfall_mm", 1000.1),
        ("Temperature_Celsius", 14.9),
        ("Temperature_Celsius", 40.1),
        ("Days_to_Harvest", 59),
        ("Days_to_Harvest", 150),
        ("Pesticides_tonnes_avg_proxy", 13734.9),
        ("Pesticides_tonnes_avg_proxy", 20043.1),
    ],
)
def test_out_of_range_numeric_rejected(field, value):
    with pytest.raises(ValidationError):
        Context(**{**VALID_CONTEXT, field: value})


def test_unknown_field_rejected():
    with pytest.raises(ValidationError):
        Context(**VALID_CONTEXT, extra_field=1)


def test_pesticides_accepts_valid_value():
    ctx = Context(**VALID_CONTEXT, Pesticides_tonnes_avg_proxy=16000.0)
    assert ctx.Pesticides_tonnes_avg_proxy == 16000.0


def test_invalid_crop_rejected():
    with pytest.raises(ValidationError):
        PredictRequest(**VALID_CONTEXT, Crop="Potato")
