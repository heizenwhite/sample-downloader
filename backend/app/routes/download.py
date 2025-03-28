from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from datetime import datetime
import os

from app.services.s3_handler import fetch_files
from app.utils.prefix_generator import generate_prefixes
from app.utils.cancellation_registry import cancellation_registry  # ✅ for cancellation tracking

router = APIRouter()

def cleanup_folder(folder: str):
    try:
        if os.path.exists(folder) and not os.listdir(folder):
            os.rmdir(folder)
    except Exception as e:
        print(f"⚠️ Failed to clean folder {folder}: {e}")

@router.post("/download/")
async def download_data(
    background_tasks: BackgroundTasks,
    product: str,
    exchange_code: str = None,
    instrument_class: str = None,
    instrument_code: str = None,
    index_code: str = None,
    granularity: str = None,
    start_date: str = None,
    end_date: str = None,
    storage: str = "s3",
    mfa_arn: str = None,
    mfa_code: str = None,
    request_id: str = Query(None),
):
    try:
        if request_id and cancellation_registry.get(request_id):
            raise HTTPException(status_code=499, detail="Download cancelled before starting.")

        print(f"Inputs: product={product}, exchange_code={exchange_code}, instrument_class={instrument_class}, "
              f"instrument_code={instrument_code}, index_code={index_code}, granularity={granularity}, "
              f"start_date={start_date}, end_date={end_date}, storage={storage}")

        # Parse date range
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

        if end_date_obj < start_date_obj:
            return JSONResponse({"detail": "End date must be after start date."}, status_code=400)

        # Generate bucket prefixes
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

        print("Generated Prefixes:")
        for prefix in prefixes:
            print(f" - {prefix}")

        if request_id and cancellation_registry.get(request_id):
            return JSONResponse({"detail": f"Request {request_id} cancelled before starting."}, status_code=400)

        # Prepare download folder
        download_folder = "./downloads/"
        os.makedirs(download_folder, exist_ok=True)

        zip_path = await fetch_files(
            prefixes=prefixes,
            storage=storage,
            download_folder=download_folder,
            mfa_arn=mfa_arn,
            mfa_code=mfa_code,
            request_id=request_id
        )

        # Cleanup zip after sending
        background_tasks.add_task(os.remove, zip_path)
        background_tasks.add_task(cleanup_folder, download_folder)

        return FileResponse(
            path=zip_path,
            filename=os.path.basename(zip_path),
            media_type="application/zip",
            background=background_tasks
        )

    except HTTPException as e:
        return JSONResponse({"detail": e.detail}, status_code=e.status_code)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"detail": str(e)}, status_code=500)

    finally:
        if request_id and request_id in cancellation_registry:
            del cancellation_registry[request_id]  # ✅ Clean up request ID
