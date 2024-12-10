from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import List
from datetime import datetime
import os
from app.services.s3_handler import fetch_files, compress_files, generate_prefixes

router = APIRouter()

@router.post("/download/")
async def download_data(
    product: str,
    exchange_code: str,
    instrument_class: str = None,
    instrument_code: str = None,
    index_code: str = None,
    granularity: str = None,
    start_date: str = None,
    end_date: str = None,
    storage: str = "s3",
    access_key: str = None,
    secret_key: str = None
):
    try:
        # Debug input parameters
        print(f"Inputs: product={product}, exchange_code={exchange_code}, instrument_class={instrument_class}, "
              f"instrument_code={instrument_code}, index_code={index_code}, granularity={granularity}, "
              f"start_date={start_date}, end_date={end_date}, storage={storage}")

        # Validate and parse dates
        from datetime import datetime
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

        if end_date_obj < start_date_obj:
            return JSONResponse(
                {"detail": "End date must be after start date."}, status_code=400
            )

        # Ensure valid combinations are generated
        combinations = list(product(exchange_code.split(","), instrument_class.split(","), instrument_code.split(",")))

        # Generate prefixes
        prefixes = generate_prefixes(
            product=product,
            exchange_code=exchange_code.split(","),
            instrument_class=instrument_class.split(","),
            instrument_code=instrument_code.split(","),
            index_code=index_code.split(",") if index_code else None,
            granularity=granularity,
            start_date=start_date_obj,
            end_date=end_date_obj,
        )

        # Download files
        download_folder = "./downloads/"
        os.makedirs(download_folder, exist_ok=True)

        zip_path = await fetch_files(
            valid_combinations=combinations,
            start_date=start_date_obj,
            end_date=end_date_obj,
            storage=storage,
            download_folder=download_folder,
            access_key=access_key,
            secret_key=secret_key,
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