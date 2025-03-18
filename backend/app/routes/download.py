from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from itertools import product as cartesian_product
from datetime import datetime
import os
from app.services.s3_handler import fetch_files, generate_prefixes

router = APIRouter()

@router.post("/download/")
async def download_data(
    product: str,
    exchange_code: str = None,
    instrument_class: str = None,
    instrument_code: str = None,
    index_code: str = None,
    granularity: str = None,
    start_date: str = None,
    end_date: str = None,
    storage: str = "s3",
    access_key: str = None,         # Not needed if keys are in backend env
    secret_key: str = None,         # Not needed if keys are in backend env
    mfa_arn: str = None,            # Needed for S3
    mfa_code: str = None            # Needed for S3
):
    try:
        # Debug input parameters
        print(f"Inputs: product={product}, exchange_code={exchange_code}, instrument_class={instrument_class}, "
              f"instrument_code={instrument_code}, index_code={index_code}, granularity={granularity}, "
              f"start_date={start_date}, end_date={end_date}, storage={storage}")

        # Validate and parse dates
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

        if end_date_obj < start_date_obj:
            return JSONResponse({"detail": "End date must be after start date."}, status_code=400)

        # Generate prefixes for files to download
        prefixes = generate_prefixes(
            product=product,
            exchange_code=exchange_code.split(",") if exchange_code else [],
            instrument_class=instrument_class.split(",") if instrument_class else [],
            instrument_code=instrument_code.split(",") if instrument_code else [],
            index_code=index_code.split(",") if index_code else [],
            granularity=granularity,
            start_date=start_date_obj,
            end_date=end_date_obj,
        )

        # Download folder
        download_folder = "./downloads/"
        os.makedirs(download_folder, exist_ok=True)

        # Download files from S3 or Wasabi using prefixes
        zip_path = await fetch_files(
            prefixes=prefixes,
            storage=storage,
            download_folder=download_folder,
            mfa_arn=mfa_arn,
            mfa_code=mfa_code
        )

        return FileResponse(
            path=zip_path,
            filename=os.path.basename(zip_path),
            media_type="application/zip"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"detail": str(e)}, status_code=500)
