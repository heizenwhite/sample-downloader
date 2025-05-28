# app/utils/auth.py

import boto3
import os
from dotenv import load_dotenv

# Optional: Automatically load from .env file
load_dotenv()

def get_s3_client():
    """
    Returns a boto3 S3 client using environment credentials.
    """
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")

    if not access_key or not secret_key:
        raise ValueError("S3 credentials not found in environment variables")

    return boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="us-east-1"  # Replace with your actual region if needed
    )

def get_wasabi_client():
    """
    Returns a boto3 Wasabi client using environment credentials.
    """
    access_key = os.getenv("WASABI_ACCESS_KEY")
    secret_key = os.getenv("WASABI_SECRET_KEY")

    if not access_key or not secret_key:
        raise ValueError("Wasabi credentials not found in environment variables")

    return boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url="https://s3.us-east-2.wasabisys.com",  # Adjust as needed
        region_name="us-east-1"
    )
