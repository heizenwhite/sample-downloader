from concurrent.futures import ThreadPoolExecutor, as_completed
import boto3
import gzip
import shutil
import os
from app.utils.auth import get_s3_client, get_wasabi_client
from app.utils.compress import compress_files
from app.utils.cancellation_registry import cancellation_registry

class DownloadCancelled(Exception):
    pass

def download_and_decompress(s3_client, bucket_name, key, download_folder, request_id):
    if request_id and cancellation_registry.get(request_id):
        print(f"❌ Cancelled before processing file: {key}")
        return None

    local_path = os.path.join(download_folder, os.path.basename(key))
    try:
        print(f"⬇️ Downloading {key}...")
        s3_client.download_file(bucket_name, key, local_path)

        if local_path.endswith(".gz"):
            decompressed_path = local_path[:-3]
            with gzip.open(local_path, "rb") as f_in, open(decompressed_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(local_path)
            return decompressed_path
        else:
            return local_path
    except Exception as e:
        print(f"❌ Failed to download {key}: {e}")
        return None

async def fetch_files(
    prefixes,
    storage,
    download_folder,
    request_id=None,
    bucket_type="indices-backfill",
):
    os.makedirs(download_folder, exist_ok=True)

    if storage == "s3":
        s3_client = get_s3_client()
        bucket_name = "kaiko-market-data"
    elif storage == "wasabi":
        s3_client = get_wasabi_client()
        bucket_name = "indices-backfill" if bucket_type == "indices-backfill" else "indices-data"
    else:
        raise ValueError("Unsupported storage type")

    print(f"📦 Using bucket: {bucket_name}")
    downloaded_files = []

    try:
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = []

            for prefix in prefixes:
                if request_id and cancellation_registry.get(request_id):
                    print(f"❌ Cancelled before processing prefix: {prefix}")
                    raise DownloadCancelled(f"Request {request_id} was cancelled")

                response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
                if "Contents" not in response:
                    print(f"❌ No files found for prefix: {prefix}")
                    continue

                for obj in response["Contents"]:
                    key = obj["Key"]
                    futures.append(executor.submit(
                        download_and_decompress,
                        s3_client,
                        bucket_name,
                        key,
                        download_folder,
                        request_id
                    ))

            for future in as_completed(futures):
                result = future.result()
                if result:
                    downloaded_files.append(result)

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
