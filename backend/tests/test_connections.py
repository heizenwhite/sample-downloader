import boto3
import pytest
from botocore.stub import Stubber

@pytest.fixture
def s3_stubbed_client():
    client = boto3.client("s3")
    stubber = Stubber(client)
    stubber.add_response("list_buckets", {"Buckets": []})  # dummy response
    stubber.activate()
    yield client
    stubber.deactivate()

@pytest.fixture
def wasabi_stubbed_client():
    client = boto3.client(
        "s3",
        aws_access_key_id="fake_key",
        aws_secret_access_key="fake_secret",
        endpoint_url="https://s3.us-east-2.wasabisys.com"
    )
    stubber = Stubber(client)
    stubber.add_response("list_buckets", {"Buckets": []})  # dummy response
    stubber.activate()
    yield client
    stubber.deactivate()

def test_s3_connection(s3_stubbed_client):
    response = s3_stubbed_client.list_buckets()
    assert "Buckets" in response
    assert isinstance(response["Buckets"], list)

def test_wasabi_connection(wasabi_stubbed_client):
    response = wasabi_stubbed_client.list_buckets()
    assert "Buckets" in response
    assert isinstance(response["Buckets"], list)
