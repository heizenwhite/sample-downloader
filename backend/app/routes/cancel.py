# routes/cancel.py
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from fastapi import Depends
from app.utils.firebase_auth import verify_token
from app.utils.cancellation_registry import cancellation_registry

router = APIRouter()

@router.post("/")
async def cancel_download(request_id: str = Query(...), user=Depends(verify_token)):
    if not request_id:
        return JSONResponse({"error": "request_id is required"}, status_code=400)
    
    cancellation_registry[request_id] = True
    return JSONResponse({"message": f"Cancellation for request {request_id} has been registered."})
