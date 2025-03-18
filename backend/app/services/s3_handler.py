import boto3
import gzip
import shutil
import os
from datetime import timedelta
from app.utils.auth import get_s3_client, get_wasabi_client
from app.utils.compress import compress_files


async def fetch_files(
    prefixes,
    storage,
    download_folder,
    mfa_arn=None,
    mfa_code=None
):
    """
    Download files from S3 or Wasabi for the given prefixes.
    """
    # Create download folder
    os.makedirs(download_folder, exist_ok=True)

    # Select client depending on storage
    if storage == "s3":
        s3_client = get_s3_client(mfa_arn, mfa_code)
        bucket_name = "kaiko-market-data"
    elif storage == "wasabi":
        s3_client = get_wasabi_client()
        bucket_name = "indices-backfill"
    else:
        raise ValueError("Unsupported storage type")

    downloaded_files = []

    for prefix in prefixes:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if "Contents" in response:
            for obj in response["Contents"]:
                file_key = obj["Key"]
                local_file_path = os.path.join(download_folder, os.path.basename(file_key))

                # Download file
                s3_client.download_file(bucket_name, file_key, local_file_path)

                # Decompress .gz if necessary
                if local_file_path.endswith(".gz"):
                    decompressed_path = local_file_path[:-3]
                    with gzip.open(local_file_path, "rb") as f_in:
                        with open(decompressed_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(local_file_path)
                    local_file_path = decompressed_path

                downloaded_files.append(local_file_path)

    # Compress downloaded files into ZIP
    zip_path = os.path.join(download_folder, "downloaded_data.zip")
    compress_files(downloaded_files, zip_path)

    # Clean up extracted files (optional)
    for f in downloaded_files:
        os.remove(f)

    return zip_path
