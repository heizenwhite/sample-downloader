from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.responses import StreamingResponse
from fastapi import Depends
from app.utils.firebase_auth import verify_token
from datetime import datetime
from pydantic import BaseModel
import os

from app.services.s3_handler import fetch_files
from app.utils.prefix_generator import generate_prefixes
from app.utils.cancellation_registry import cancellation_registry

router = APIRouter()

class DownloadRequest(BaseModel):
    product: str
    exchange_code: str = None
    instrument_class: str = None
    instrument_code: str = None
    index_code: str = None
    granularity: str = None
    start_date: str
    end_date: str
    storage: str = "s3"
    request_id: str = None
    bucket: str = "indices-backfill"  # ✅ Add this line

def read_in_chunks(file_path: str, chunk_size: int = 1024 * 1024):
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk

def cleanup_folder(folder: str):
    if not os.path.exists(folder):
        return
    try:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(folder)
    except Exception as e:
        print(f"⚠️ Failed to clean folder {folder}: {e}")



@router.post("/download/")
async def download_data(
    background_tasks: BackgroundTasks,
    req: DownloadRequest,
    user=Depends(verify_token),  # ✅ This enforces authentication
):
    try:
        if req.request_id and cancellation_registry.get(req.request_id):
            raise HTTPException(status_code=499, detail="Download cancelled before starting.")

        print(f"📥 Inputs: {req.model_dump()}")

        # Parse date range
        start_date_obj = datetime.strptime(req.start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(req.end_date, "%Y-%m-%d")

        if end_date_obj < start_date_obj:
            return JSONResponse({"detail": "End date must be after start date."}, status_code=400)

        # Generate prefixes
        prefixes = generate_prefixes(
            product=req.product,
            exchange_code=req.exchange_code.split(",") if req.exchange_code else [],
            instrument_class=req.instrument_class.split(",") if req.instrument_class else [],
            instrument_code=req.instrument_code.split(",") if req.instrument_code else [],
            index_code=req.index_code.split(",") if req.index_code else [],
            granularity=req.granularity,
            start_date=start_date_obj,
            end_date=end_date_obj,
        )

        # Final check
        if req.request_id and cancellation_registry.get(req.request_id):
            return JSONResponse({"detail": f"Request {req.request_id} cancelled before starting."}, status_code=400)

        # Prepare download folder
        download_folder = "./downloads/"
        os.makedirs(download_folder, exist_ok=True)

        zip_path, downloaded_files = await fetch_files(
            prefixes=prefixes,
            storage=req.storage,
            download_folder=download_folder,
            request_id=req.request_id,
            bucket_type=req.bucket  # ✅ Use the value from the request
        )


        # Cleanup tasks
        background_tasks.add_task(os.remove, zip_path)
        for file_path in downloaded_files:
            background_tasks.add_task(os.remove, file_path)
        background_tasks.add_task(cleanup_folder, download_folder)

        return StreamingResponse(
            read_in_chunks(zip_path),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={os.path.basename(zip_path)}"
            },
            background=background_tasks
        )

    except HTTPException as e:
        return JSONResponse({"detail": e.detail}, status_code=e.status_code)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"detail": str(e)}, status_code=500)

    finally:
        if req.request_id and req.request_id in cancellation_registry:
            del cancellation_registry[req.request_id]