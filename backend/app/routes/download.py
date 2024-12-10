from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.services.s3_handler import download_files

router = APIRouter()

# Input model for the download request
class DownloadRequest(BaseModel):
    storage_type: str  # "s3" or "wasabi"
    credentials: dict  # AWS/Wasabi credentials
    prefix_template: str
    date_range: list[str]  # ["YYYY-MM-DD", "YYYY-MM-DD"]
    exchange_code: str
    instrument_class: str
    instrument_code: list[str]  # Comma-separated values
    granularity: str = None  # Optional, for products like OHLCV

@router.post("/")
async def download(request: DownloadRequest, background_tasks: BackgroundTasks):
    try:
        # Pass task to background
        task_id = await download_files(request, background_tasks)
        return {"status": "success", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))