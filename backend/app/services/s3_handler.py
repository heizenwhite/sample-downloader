import boto3
import gzip
import shutil
from datetime import timedelta
from zipfile import ZipFile
import os

async def fetch_files(prefixes, storage, download_folder, mfa_arn=None, mfa_code=None):
    """
    Download files using prefixes from S3 or Wasabi.
    """
    if storage == "s3":
        if not mfa_arn or not mfa_code:
            raise ValueError("MFA ARN and Code are required for S3 access.")
        
        sts_client = boto3.client("sts")
        token_response = sts_client.get_session_token(
            DurationSeconds=3600,
            SerialNumber=mfa_arn,
            TokenCode=mfa_code
        )
        credentials = token_response["Credentials"]
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        bucket_name = "kaiko-market-data"

    elif storage == "wasabi":
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("WASABI_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("WASABI_SECRET_KEY"),
            endpoint_url="https://s3.us-east-2.wasabisys.com"
        )
        bucket_name = "indices-backfill"
    else:
        raise ValueError("Unsupported storage type")

    # Prepare ZIP file for downloads
    zip_path = os.path.join(download_folder, "downloaded_data.zip")
    with ZipFile(zip_path, "w") as zip_file:
        for prefix in prefixes:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            if "Contents" in response:
                for obj in response["Contents"]:
                    file_key = obj["Key"]
                    local_file_path = os.path.join(download_folder, os.path.basename(file_key))
                    s3_client.download_file(bucket_name, file_key, local_file_path)

                    # Unzip if needed
                    if local_file_path.endswith(".gz"):
                        csv_path = local_file_path[:-3]
                        with gzip.open(local_file_path, "rb") as gz_in:
                            with open(csv_path, "wb") as csv_out:
                                shutil.copyfileobj(gz_in, csv_out)
                        os.remove(local_file_path)
                        local_file_path = csv_path

                    zip_file.write(local_file_path, arcname=os.path.basename(local_file_path))
                    os.remove(local_file_path)

    return zip_path

# ---------------------------------------------------
# Generate Prefixes Logic
# ---------------------------------------------------
def generate_prefixes(
    product: str,
    exchange_code: list = [],
    instrument_class: list = [],
    instrument_code: list = [],
    index_code: list = [],
    granularity: str = None,
    start_date=None,
    end_date=None
):
    prefixes = []
    date_range = [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range((end_date - start_date).days + 1)
    ]

    if product in ["Index", "Index Multi-Asset"]:
        for date in date_range:
            for index in index_code:
                PT = "PT5S"
                if any(x in index for x in ["LDN", "NYC", "SGP"]):
                    PT = "PT24H"
                elif "1S" in index:
                    PT = "PT1S"
                elif "RT" in index:
                    PT = "PT1H"
                index_type = "index_fixing" if any(x in index for x in ["LDN", "NYC", "SGP"]) else "real_time"
                date_part = date[:7] if PT in ["PT24H", "PT1H"] else date
                prefix = (
                    f"index_v1/v1/extensive/{index.lower()}/{index_type}/{PT}/"
                    f"{index.lower()}_{index_type}_vwm_twap_100_{date_part}.csv.gz"
                )
                prefixes.append(prefix)

    elif product in ["Order Book Snapshots", "Full Order Book", "Top Of Book", "Trades", "Derivatives"]:
        for date in date_range:
            year_month = date[:7]
            for exch in exchange_code:
                for cls in instrument_class:
                    for code in instrument_code:
                        prefix = (
                            f"{product.lower().replace(' ', '_')}/{exch}/{cls}/{code}/{year_month}/"
                            f"{product.lower().replace(' ', '_')}_{exch}_{cls}_{code}_{date}.csv.gz"
                        )
                        prefixes.append(prefix)

    elif product in ["COHLCVVWAP", "OHLCV", "VWAP"]:
        if not granularity:
            raise ValueError("Granularity is required for this product.")
        for date in date_range:
            year_folder = date[:4] if granularity in ["1d", "4h", "1h"] else date[:7]
            for exch in exchange_code:
                for cls in instrument_class:
                    for code in instrument_code:
                        prefix = (
                            f"{product.lower()}/{granularity}/{exch}/{cls}/{code}/{year_folder}/"
                            f"{product.lower().replace(' ', '_')}_{exch}_{cls}_{code}_{date}.csv.gz"
                        )
                        prefixes.append(prefix)
    else:
        raise ValueError("Unsupported product type.")
    
    return prefixes
