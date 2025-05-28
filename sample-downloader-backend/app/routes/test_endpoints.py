from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from fastapi import Depends
from app.utils.firebase_auth import verify_token

router = APIRouter(
    prefix="/api/test",
    tags=["Test Endpoints"],
    dependencies=[Depends(verify_token)],  # ✅ Protect all routes in this router
)

@router.get("/trades")
async def test_trades():
    return JSONResponse({
        "example_input": {
            "product": "Trades",
            "exchange_code": "binc,okex",
            "instrument_class": "spot",
            "instrument_code": "btcusdt,ethusdt",
            "start_date": "2025-01-01",
            "end_date": "2025-01-03",
            "storage": "wasabi"
        }
    })

@router.get("/order_book_snapshots")
async def test_order_book_snapshots():
    return JSONResponse({
        "example_input": {
            "product": "Order Book Snapshots",
            "exchange_code": "binc",
            "instrument_class": "spot",
            "instrument_code": "btcusdt",
            "start_date": "2025-01-01",
            "end_date": "2025-01-03",
            "storage": "s3"
        }
    })

@router.get("/full_order_book")
async def test_full_order_book():
    return JSONResponse({
        "example_input": {
            "product": "Full Order Book",
            "exchange_code": "binc",
            "instrument_class": "spot",
            "instrument_code": "btcusdt",
            "start_date": "2025-01-01",
            "end_date": "2025-01-03",
            "storage": "s3"
        }
    })

@router.get("/ohlcv")
async def test_ohlcv():
    return JSONResponse({
        "example_input": {
            "product": "OHLCV",
            "exchange_code": "binc",
            "instrument_class": "spot",
            "instrument_code": "btcusdt",
            "granularity": "1d_per_year",
            "start_date": "2024-12-01",
            "end_date": "2024-12-10",
            "storage": "wasabi"
        }
    })

@router.get("/indices")
async def test_indices():
    return JSONResponse({
        "example_input": {
            "product": "Index",
            "index_code": "cboe-kaiko_btcusd_rt,d2x-kaiko_etheur_ldn",
            "start_date": "2024-12-01",
            "end_date": "2024-12-05",
            "storage": "wasabi"
        }
    })

@router.get("/derivatives")
async def test_derivatives():
    return JSONResponse({
        "example_input": {
            "product": "Derivatives",
            "exchange_code": "binc",
            "instrument_class": "perpetual-future",
            "instrument_code": "btcusdt",
            "start_date": "2025-01-01",
            "end_date": "2025-01-05",
            "storage": "wasabi"
        }
    })

@router.get("/top_of_book")
async def test_top_of_book():
    return JSONResponse({
        "example_input": {
            "product": "Top Of Book",
            "exchange_code": "binc",
            "instrument_class": "spot",
            "instrument_code": "btcusdt",
            "start_date": "2025-01-01",
            "end_date": "2025-01-03",
            "storage": "s3"
        }
    })

@router.get("/s3")
async def s3_test():
    return {"message": "S3 test successful!"}

@router.get("/wasabi")
async def wasabi_test():
    return {"message": "Wasabi test successful!"}
