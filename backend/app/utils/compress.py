import os
from zipfile import ZipFile

def compress_files(file_paths: list, output_zip_path: str) -> str:
    """
    Compress a list of files into a ZIP archive.

    Args:
        file_paths (list): List of file paths to include in the zip.
        output_zip_path (str): The output zip file path.

    Returns:
        str: The path to the created zip file.
    """
    os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)
    
    with ZipFile(output_zip_path, "w") as zipf:
        for file_path in file_paths:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname=arcname)
    
    return output_zip_path
