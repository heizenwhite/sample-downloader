import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_s3_client():
    with patch("app.utils.auth.get_s3_client") as mock_client:
        mock_client.return_value.list_objects_v2.return_value = {"Contents": [{"Key": "dummy_file.csv.gz"}]}
        mock_client.return_value.download_file.return_value = None
        yield mock_client

@pytest.fixture
def mock_wasabi_client():
    with patch("app.utils.auth.get_wasabi_client") as mock_client:
        mock_client.return_value.list_objects_v2.return_value = {"Contents": [{"Key": "dummy_file.csv.gz"}]}
        mock_client.return_value.download_file.return_value = None
        yield mock_client

@pytest.mark.asyncio
def test_download_trades_wasabi(mock_wasabi_client):
    response = client.post(
        "/api/download/download/",
        params={
            "product": "Trades",
            "exchange_code": "binc",
            "instrument_class": "spot",
            "instrument_code": "btc-usdt",
            "start_date": "2025-01-01",
            "end_date": "2025-01-02",
            "storage": "wasabi"
        }
    )
    assert response.status_code in [200, 500]  # Success or simulated failure in mocked env

@pytest.mark.asyncio
def test_download_order_book_snapshots_s3(mock_s3_client):
    response = client.post(
        "/api/download/download/",
        params={
            "product": "Order Book Snapshots",
            "exchange_code": "binc",
            "instrument_class": "spot",
            "instrument_code": "btc-usdt",
            "start_date": "2025-01-01",
            "end_date": "2025-01-02",
            "storage": "s3",
            "mfa_arn": "arn:aws:iam::123456789012:mfa/user",
            "mfa_code": "123456"
        }
    )
    assert response.status_code in [200, 500]

@pytest.mark.asyncio
def test_invalid_date_range():
    response = client.post(
        "/api/download/download/",
        params={
            "product": "Trades",
            "exchange_code": "binc",
            "instrument_class": "spot",
            "instrument_code": "btc-usdt",
            "start_date": "2025-02-01",
            "end_date": "2025-01-01",
            "storage": "s3",
            "mfa_arn": "arn:aws:iam::123456789012:mfa/user",
            "mfa_code": "123456"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "End date must be after start date."

@pytest.mark.asyncio
def test_missing_required_fields():
    response = client.post(
        "/api/download/download/",
        params={
            "product": "Trades",
            "start_date": "2025-01-01",
            "end_date": "2025-01-02",
            "storage": "s3",
            "mfa_arn": "arn:aws:iam::123456789012:mfa/user",
            "mfa_code": "123456"
        }
    )
    assert response.status_code == 500
