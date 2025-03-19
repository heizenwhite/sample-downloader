import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class MockResponse:
    def __init__(self):
        self.status_code = 200

    def json(self):
        # Mock dataset similar to Kaiko API response
        return {
            "data": [
                {"exchange_code": "binc", "class": "spot", "code": "btc-usdt"},
                {"exchange_code": "cbse", "class": "perpetual-future", "code": "eth-usd"},
            ]
        }

@pytest.fixture(autouse=True)
def mock_kaiko_api_response(mocker):
    mocker.patch(
        "app.services.kaiko_api.requests.get",
        return_value=MockResponse()
    )

def test_valid_combinations():
    response = client.get(
        "/api/validate/?exchange_code=binc,cbse&instrument_class=spot,perpetual-future&instrument_code=btc-usdt,eth-usd"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["valid_combinations"]) > 0
    assert ["binc", "spot", "btc-usdt"] in data["valid_combinations"]
    assert ["cbse", "perpetual-future", "eth-usd"] in data["valid_combinations"]

def test_invalid_combinations():
    response = client.get(
        "/api/validate/?exchange_code=nonexistent&instrument_class=spot&instrument_code=invalidpair"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["valid_combinations"]) == 0
    assert ["nonexistent", "spot", "invalidpair"] in data["invalid_combinations"]

def test_missing_parameters():
    response = client.get("/api/validate/")
    assert response.status_code == 422  # FastAPI auto-validates missing required params
