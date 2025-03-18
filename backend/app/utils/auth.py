import boto3
import os

def get_s3_client(mfa_arn: str, mfa_code: str):
    """
    Returns a boto3 S3 client authenticated with MFA.
    """
    sts_client = boto3.client("sts")
    token_response = sts_client.get_session_token(
        DurationSeconds=3600,
        SerialNumber=mfa_arn,
        TokenCode=mfa_code
    )
    credentials = token_response["Credentials"]

    return boto3.client(
        "s3",
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

def get_wasabi_client():
    """
    Returns a boto3 Wasabi client using backend environment variables.
    """
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("WASABI_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("WASABI_SECRET_KEY"),
        endpoint_url="https://s3.us-east-2.wasabisys.com"
    )
