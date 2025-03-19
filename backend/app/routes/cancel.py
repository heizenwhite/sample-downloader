# routes/cancel.py
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.utils.cancellation_registry import cancellation_registry

router = APIRouter()

@router.post("/")
async def cancel_download(request_id: str = Query(...)):
    if not request_id:
        return JSONResponse({"error": "request_id is required"}, status_code=400)
    
    cancellation_registry[request_id] = True
    return JSONResponse({"message": f"Cancellation for request {request_id} has been registered."})
