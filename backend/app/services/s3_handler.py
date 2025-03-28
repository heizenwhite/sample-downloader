# services/s3_handler.py

import boto3
import gzip
import shutil
import os
from app.utils.auth import get_s3_client, get_wasabi_client
from app.utils.compress import compress_files
from app.utils.cancellation_registry import cancellation_registry  # ✅ correct import

class DownloadCancelled(Exception):
    pass

async def fetch_files(
    prefixes,
    storage,
    download_folder,
    request_id=None,  # ✅ MFA removed, only request_id remains
    bucket_type="indices-backfill",  # ✅ MFA removed, only bucket_type remains
):
    """
    Download files from S3 or Wasabi for the given prefixes.
    """
    os.makedirs(download_folder, exist_ok=True)

    # Select S3 or Wasabi client
    if storage == "s3":
        # S3 will always use the kaiko-market-data bucket
        s3_client = get_s3_client()
        bucket_name = "kaiko-market-data"  # Fixed bucket name for S3

    elif storage == "wasabi":
        s3_client = get_wasabi_client()

        # Select bucket based on bucket_type for Wasabi
        if bucket_type == "indices-backfill":
            bucket_name = "indices-backfill"  # Wasabi bucket for backfill data
        elif bucket_type == "indices-data":
            bucket_name = "indices-data"  # Wasabi bucket for indices data
        else:
            raise ValueError(f"Unsupported bucket type for Wasabi: {bucket_type}")
    else:
        raise ValueError("Unsupported storage type")

    downloaded_files = []

    try:
        for prefix in prefixes:
            if request_id and cancellation_registry.get(request_id):
                print(f"❌ Cancelled before processing prefix: {prefix}")
                raise DownloadCancelled(f"Request {request_id} was cancelled")

            # Fetch the list of objects for the given prefix
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            if "Contents" in response:
                for obj in response["Contents"]:
                    if request_id and cancellation_registry.get(request_id):
                        print(f"❌ Cancelled while processing file: {obj['Key']}")
                        raise DownloadCancelled(f"Request {request_id} was cancelled")

                    file_key = obj["Key"]
                    local_file_path = os.path.join(download_folder, os.path.basename(file_key))

                    print(f"⬇️ Downloading {file_key}...")

                    s3_client.download_file(bucket_name, file_key, local_file_path)

                    if request_id and cancellation_registry.get(request_id):
                        print(f"❌ Cancelled after downloading {file_key}")
                        raise DownloadCancelled(f"Request {request_id} was cancelled")

                    # Decompress if .gz
                    if local_file_path.endswith(".gz"):
                        decompressed_path = local_file_path[:-3]
                        with gzip.open(local_file_path, "rb") as f_in:
                            with open(decompressed_path, "wb") as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        os.remove(local_file_path)
                        local_file_path = decompressed_path

                    downloaded_files.append(local_file_path)

            else:
                print(f"❌ No files found for prefix: {prefix}")

        # Final check before compressing
        if request_id and cancellation_registry.get(request_id):
            print("❌ Cancelled before zipping files")
            raise DownloadCancelled(f"Request {request_id} was cancelled")

        zip_path = os.path.join(download_folder, "downloaded_data.zip")
        if downloaded_files:
            compress_files(downloaded_files, zip_path)
            print(f"✅ Files compressed into {zip_path}")
        else:
            print("❌ No files downloaded to compress.")

        return zip_path, downloaded_files

    finally:
        # Clean up partially downloaded files if cancelled
        if request_id and cancellation_registry.get(request_id):
            print("🧹 Cleaning up partial downloads due to cancellation...")
            for f in downloaded_files:
                if os.path.exists(f):
                    os.remove(f)
            if os.path.exists(download_folder):
                try:
                    os.rmdir(download_folder)
                except:
                    pass
