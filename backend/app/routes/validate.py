from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.kaiko_api import validate_instruments

router = APIRouter()

class ValidateRequest(BaseModel):
    exchange_code: str
    instrument_class: str
    instrument_code: list[str]

@router.get("/")
async def validate(request: ValidateRequest):
    try:
        result = await validate_instruments(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))