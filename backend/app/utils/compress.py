from zipfile import ZipFile, ZIP_DEFLATED
from concurrent.futures import ThreadPoolExecutor
import os

def _compress_individual_file(file_path):
    arcname = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        data = f.read()
    return arcname, data

def compress_files(file_paths: list, output_zip_path: str, max_workers: int = 24) -> str:
    os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)

    with ZipFile(output_zip_path, "w", compression=ZIP_DEFLATED) as zipf:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(_compress_individual_file, path) for path in file_paths]
            for i, future in enumerate(futures, 1):
                arcname, data = future.result()
                zipf.writestr(arcname, data)
                print(f"🗜️ [{i}/{len(file_paths)}] Compressed {arcname}")

    return output_zip_path
