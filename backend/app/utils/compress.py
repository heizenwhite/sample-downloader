from zipfile import ZipFile, ZIP_DEFLATED
import os

def compress_files(gz_file_paths: list, output_zip_path: str) -> str:
    os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)

    with ZipFile(output_zip_path, "w", compression=ZIP_DEFLATED) as zipf:
        for i, file_path in enumerate(gz_file_paths, 1):
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname=arcname)
            print(f"🗜️ [{i}/{len(gz_file_paths)}] Added {arcname} (gz as-is)")

    return output_zip_path
