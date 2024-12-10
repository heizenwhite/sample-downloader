import boto3
import requests
import gzip
import shutil
from itertools import product
from datetime import timedelta, datetime
from zipfile import ZipFile
import os


async def fetch_files(valid_combinations, start_date, end_date, storage, download_folder):
    """
    Download files from S3 or Wasabi for the given valid combinations and date range.
    """
    session = boto3.Session()

    if storage == "s3":
        s3_client = session.client("s3")
        bucket_name = "kaiko-market-data"  # Example S3 bucket
    elif storage == "wasabi":
        s3_client = session.client(
            "s3",
            aws_access_key_id="YOUR_WASABI_ACCESS_KEY",
            aws_secret_access_key="YOUR_WASABI_SECRET_KEY",
            endpoint_url="https://s3.us-east-2.wasabisys.com"
        )
        bucket_name = "your-wasabi-bucket"  # Example Wasabi bucket
    else:
        raise ValueError("Unsupported storage type.")
    
    # Prepare ZIP file for downloads
    zip_path = os.path.join(download_folder, "downloaded_data.zip")
    with ZipFile(zip_path, "w") as zip_file:
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            
            for exchange, cls, code in valid_combinations:
                prefix = f"{cls}/{exchange}/{code}/{date_str}/"
                response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
                
                if "Contents" in response:
                    for obj in response["Contents"]:
                        file_key = obj["Key"]
                        local_file_path = os.path.join(download_folder, os.path.basename(file_key))
                        
                        # Download file
                        s3_client.download_file(bucket_name, file_key, local_file_path)
                        
                        # Unzip if necessary
                        if local_file_path.endswith(".gz"):
                            csv_path = local_file_path[:-3]
                            with gzip.open(local_file_path, "rb") as gz_in:
                                with open(csv_path, "wb") as csv_out:
                                    shutil.copyfileobj(gz_in, csv_out)
                            os.remove(local_file_path)
                            local_file_path = csv_path
                        
                        # Add to ZIP
                        zip_file.write(local_file_path, arcname=os.path.basename(local_file_path))
                        os.remove(local_file_path)
            
            current_date += timedelta(days=1)
    
    return zip_path


def generate_prefixes(
    product: str,
    exchange_code: list,
    instrument_class: list = None,
    instrument_code: list = None,
    index_code: list = None,
    granularity: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
):
    """
    Generate prefixes dynamically based on the product and input parameters.
    """
    prefixes = []
    date_range = [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range((end_date - start_date).days + 1)
    ]

    if product in ["Order Book Snapshots", "Full Order Book", "Top Of Book"]:
        for date in date_range:
            for exch in exchange_code:
                for instr_class in instrument_class:
                    for instr_code in instrument_code:
                        prefixes.append(
                            f"s3://bucket-name/{product.lower().replace(' ', '_')}/{exch}/{instr_class}/{instr_code}/{date}/"
                        )
    elif product == "Trades":
        for date in date_range:
            for exch in exchange_code:
                for instr_code in instrument_code:
                    prefixes.append(
                        f"trades-data/tick_csv/v1/gz_v1/{exch}/{instr_code}/{date.replace('-', '_')}/"
                    )
    elif product == "OHLCV/VWAP/COHLCVVWAP":
        if not granularity:
            raise ValueError("Granularity must be specified for this product.")
        for date in date_range:
            for exch in exchange_code:
                for instr_code in instrument_code:
                    prefixes.append(
                        f"trades-data/aggro_csv/v1/csv_v1/cohlcvvwap_v1/{granularity}/{exch}/{instr_code}/{date[:7]}/"
                    )
    elif product == "Indices":
        for date in date_range:
            for index in index_code:
                prefixes.append(
                    f"indices-backfill/index_v1/v1/extensive/{index}/{date[:7]}/"
                )
    return prefixes


def compress_files(files, output_folder):
    """
    Compress files into a ZIP archive.
    """
    os.makedirs(output_folder, exist_ok=True)
    zip_path = os.path.join(output_folder, "downloaded_files.zip")
    with ZipFile(zip_path, "w") as zipf:
        for file in files:
            zipf.write(file, arcname=os.path.basename(file))
    return zip_path