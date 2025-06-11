from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import datetime, timedelta
from pydantic import BaseModel
import os

from app.services.s3_handler import fetch_files, DownloadCancelled
from app.utils.prefix_generator import generate_prefixes
from app.utils.cancellation_registry import cancellation_registry
from app.utils.firebase_auth import verify_token

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
    bucket: str = "indices-backfill"

def read_in_chunks(path: str, chunk_size: int = 1024*1024):
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk

@router.post("/download/")
async def download_data(
    background_tasks: BackgroundTasks,
    req: DownloadRequest,
    request: Request,
):
    # Do not run for preflight
    if request.method == "OPTIONS":
        return JSONResponse(content={"status": "OK"})

    # ✅ Auth only on real requests
    user = await verify_token(request)
    # pre-start cancel
    if req.request_id and cancellation_registry.get(req.request_id):
        raise HTTPException(499, "Cancelled")

    # parse dates
    sd = datetime.fromisoformat(req.start_date) + timedelta(days=1)  # adjust start date to include the full day
    ed = datetime.fromisoformat(req.end_date) + timedelta(days=1)  # adjust end date to include the full day
    if ed < sd:
        return JSONResponse({"error": "End date must be after start date."}, status_code=400)

    # build prefixes
    prefixes = generate_prefixes(
        product=req.product,
        exchange_code=(req.exchange_code or "").split(","),
        instrument_class=(req.instrument_class or "").split(","),
        instrument_code=(req.instrument_code or "").split(","),
        index_code=(req.index_code or "").split(","),
        granularity=req.granularity,
        start_date=sd, end_date=ed
    )

    # fetch + zip
    try:
        zip_path, downloaded, skipped = await fetch_files(
            prefixes=prefixes,
            storage=req.storage,
            download_folder="./downloads",
            request_id=req.request_id,
            bucket_type=req.bucket
        )
    except DownloadCancelled:
        raise HTTPException(499, "Cancelled mid-way")

    # schedule cleanup
    background_tasks.add_task(os.remove, zip_path)
    for p in downloaded:
        background_tasks.add_task(os.remove, p)
    background_tasks.add_task(lambda: os.rmdir("./downloads"))

    # put lists into headers
    headers = {
        "Content-Disposition": f"attachment; filename={req.product.replace(' ','_')}.zip",
        "X-Downloaded-Files": ",".join(downloaded),
        "X-Skipped-Files": ",".join(f"{s['key']}::{s['reason']}" for s in skipped),
    }

    return StreamingResponse(
        read_in_chunks(zip_path),
        media_type="application/zip",
        headers=headers,
        background=background_tasks
    )
