from fastapi import APIRouter, HTTPException, Query
from fastapi import Depends
from app.utils.firebase_auth import verify_token
from typing import List
from itertools import product as cartesian_product
from app.services.kaiko_api import validate_combinations

router = APIRouter()

@router.get("/")
async def validate_combinations_handler(
    exchange_code: str = Query(..., description="Comma-separated exchange codes (e.g., binc,okex,krkn)"),
    instrument_class: str = Query(..., description="Comma-separated classes (e.g., spot,future,perpetual-future)"),
    instrument_code: str = Query(..., description="Comma-separated instrument codes (e.g., btcusdt,ethusdt)"),
    user=Depends(verify_token)
):
    try:
        # Split input strings into lists
        exchanges = exchange_code.split(",")
        classes = instrument_class.split(",")
        instruments = instrument_code.split(",")

        # Cartesian product of all combinations
        combinations = list(cartesian_product(exchanges, classes, instruments))

        # Validate against Kaiko API
        result = await validate_combinations(combinations)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
