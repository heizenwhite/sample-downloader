from fastapi import APIRouter, HTTPException, Query
from typing import List
from itertools import product
from app.services.kaiko_api import validate_combinations

router = APIRouter()

@router.get("/")
async def validate(
    exchange_code: str = Query(..., description="exchange_1,exchange_2,exchange_3,..."),
    instrument_class: str = Query(..., description="class_1,class_2,class_3,..."),
    instrument_code: str = Query(..., description="instrument_1,instrument_2,instrument_3,...")
):
    try:
        # Parse comma-separated inputs
        exchanges = exchange_code.split(",")
        classes = instrument_class.split(",")
        instruments = instrument_code.split(",")
        
        # Generate all combinations
        combinations = list(product(exchanges, classes, instruments))
        
        # Validate each combination
        result = await validate_combinations(combinations)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))