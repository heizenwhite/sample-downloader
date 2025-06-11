from zipfile import ZipFile, ZIP_DEFLATED
from concurrent.futures import ThreadPoolExecutor
import os


def compress_files(file_paths: list, output_zip_path: str) -> str:
    os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)

    with ZipFile(output_zip_path, "w", compression=ZIP_DEFLATED, allowZip64=True) as zipf:
        for i, file_path in enumerate(file_paths, 1):
            try:
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname=arcname)
                print(f"🗜️ [{i}/{len(file_paths)}] Compressed {arcname} (streamed)")
            except Exception as e:
                print(f"❌ Failed to compress {file_path}: {e}")

    return output_zip_path

