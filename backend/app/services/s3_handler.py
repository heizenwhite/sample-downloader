from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import shutil
import os

from app.utils.auth import get_s3_client, get_wasabi_client
from app.utils.compress import compress_files
from app.utils.cancellation_registry import cancellation_registry

# 20 GiB maximum total download
MAX_DOWNLOAD_SIZE_BYTES = 20 * 1024**3

class DownloadCancelled(Exception):
    pass

def download_and_decompress(s3_client, bucket_name, key, download_folder, request_id):
    # cancellation check
    if request_id and cancellation_registry.get(request_id):
        return None

    local_path = os.path.join(download_folder, os.path.basename(key))
    try:
        # download
        print(f"⬇️ Downloading {key}...")
        s3_client.download_file(bucket_name, key, local_path)

        # DO NOT decompress — keep .gz as-is
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

    # choose client + bucket
    if storage == "s3":
        s3_client = get_s3_client()
        bucket = "kaiko-market-data"
    else:
        s3_client = get_wasabi_client()
        bucket = bucket_type == "indices-backfill" and "indices-backfill" or "indices-data"

    print(f"📦 Using bucket: {bucket}")

    downloaded_files = []
    skipped_files = []
    total_size = 0

    try:
        with ThreadPoolExecutor(max_workers=24) as executor:
            futures = []

            for prefix in prefixes:
                if request_id and cancellation_registry.get(request_id):
                    raise DownloadCancelled

                # list objects under this prefix
                resp = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
                contents = resp.get("Contents", [])
                if not contents:
                    skipped_files.append({
                        "key": prefix,
                        "reason": "not_found"
                    })
                    print(f"❌ No files for prefix {prefix}")
                    continue

                for obj in contents:
                    key = obj["Key"]
                    size = obj.get("Size", 0)

                    # size‐limit check
                    if total_size + size > MAX_DOWNLOAD_SIZE_BYTES:
                        skipped_files.append({
                          "key": key,
                          "reason": "size_limit_exceeded"
                        })
                        print(f"⚠️ Skipping {key}, size {size} would exceed limit")
                    else:
                        total_size += size
                        futures.append(
                            executor.submit(
                              download_and_decompress,
                              s3_client, bucket, key,
                              download_folder, request_id
                            )
                        )

            # collect results
            for future in as_completed(futures):
                path = future.result()
                if path:
                    downloaded_files.append(path)

        # zip
        zip_path = os.path.join(download_folder, "downloaded_data.zip")
        if downloaded_files:
            compress_files(downloaded_files, zip_path)
            print(f"✅ Compressed into {zip_path}")
        else:
            print("❌ No files downloaded to compress.")

        return zip_path, downloaded_files, skipped_files

    finally:
        # on cancellation cleanup
        if request_id and cancellation_registry.get(request_id):
            print("🧹 Cleaning up partial downloads...")
            for f in downloaded_files:
                try: os.remove(f)
                except: pass
            try:
                os.rmdir(download_folder)
            except: pass
