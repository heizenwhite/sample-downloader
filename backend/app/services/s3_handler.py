import boto3
import gzip
import shutil
import os
from app.utils.auth import get_s3_client, get_wasabi_client
from app.utils.compress import compress_files
from app.routes.cancel import cancellation_registry

class DownloadCancelled(Exception):
    pass

async def fetch_files(
    prefixes,
    storage,
    download_folder,
    mfa_arn=None,
    mfa_code=None,
    request_id=None,
):
    os.makedirs(download_folder, exist_ok=True)

    if storage == "s3":
        s3_client = get_s3_client(mfa_arn, mfa_code)
        bucket_name = "kaiko-market-data"
    elif storage == "wasabi":
        s3_client = get_wasabi_client()
        bucket_name = "indices-backfill"
    else:
        raise ValueError("Unsupported storage type")

    downloaded_files = []

    try:
        for prefix in prefixes:
            if request_id and cancellation_registry.get(request_id):
                print(f"❌ Cancelled before prefix: {prefix}")
                raise DownloadCancelled()

            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            if "Contents" in response:
                for obj in response["Contents"]:
                    if request_id and cancellation_registry.get(request_id):
                        print(f"❌ Cancelled before file: {obj['Key']}")
                        raise DownloadCancelled()

                    file_key = obj["Key"]
                    local_file_path = os.path.join(download_folder, os.path.basename(file_key))

                    print(f"⬇️ Streaming download {file_key}...")

                    # CHUNKED STREAMING
                    with open(local_file_path, "wb") as f:
                        s3_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
                        for chunk in s3_obj['Body'].iter_chunks(chunk_size=5 * 1024 * 1024):  # 5MB chunks
                            if request_id and cancellation_registry.get(request_id):
                                print(f"❌ Cancelled mid-download: {file_key}")
                                raise DownloadCancelled()
                            f.write(chunk)

                    # Decompression logic
                    if local_file_path.endswith(".gz"):
                        decompressed_path = local_file_path[:-3]
                        with gzip.open(local_file_path, "rb") as f_in:
                            with open(decompressed_path, "wb") as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        os.remove(local_file_path)
                        local_file_path = decompressed_path

                    downloaded_files.append(local_file_path)

        if request_id and cancellation_registry.get(request_id):
            print("❌ Cancelled before zipping")
            raise DownloadCancelled()

        zip_path = os.path.join(download_folder, "downloaded_data.zip")
        compress_files(downloaded_files, zip_path)

        return zip_path

    finally:
        if request_id and cancellation_registry.get(request_id):
            print("🧹 Cleaning up due to cancellation...")
            for f in downloaded_files:
                if os.path.exists(f):
                    os.remove(f)
