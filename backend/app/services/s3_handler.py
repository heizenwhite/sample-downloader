import boto3
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

# Generate file paths dynamically
def generate_file_paths(prefix_template, date_range, exchange_code, instrument_class, instrument_code):
    file_paths = []
    start_date, end_date = map(lambda d: datetime.strptime(d, "%Y-%m-%d"), date_range)

    while start_date <= end_date:
        date_str = start_date.strftime("%Y-%m-%d")
        for code in instrument_code:
            file_path = prefix_template.format(
                exchange_code=exchange_code,
                instrument_class=instrument_class,
                instrument_code=code,
                date=date_str
            )
            file_paths.append(file_path)
        start_date += timedelta(days=1)

    return file_paths

# Download files concurrently
def download_files(request, background_tasks):
    # Initialize S3/Wasabi client
    s3_client = boto3.client(
        "s3" if request.storage_type == "s3" else "wasabi",
        aws_access_key_id=request.credentials["key"],
        aws_secret_access_key=request.credentials["secret"],
        endpoint_url=request.credentials.get("endpoint_url")
    )

    # Generate file paths
    file_paths = generate_file_paths(
        request.prefix_template,
        request.date_range,
        request.exchange_code,
        request.instrument_class,
        request.instrument_code
    )

    # Download each file
    output_dir = "./downloads/"
    os.makedirs(output_dir, exist_ok=True)

    def download_file(file_path):
        local_path = os.path.join(output_dir, os.path.basename(file_path))
        s3_client.download_file(request.bucket_name, file_path, local_path)

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(download_file, file_paths)

    # Optionally zip the files
    # background_tasks.add_task(zip_files, output_dir)

    return "task-id-placeholder"