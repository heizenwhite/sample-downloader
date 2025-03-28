# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import download, validate
from app.routes.test_endpoints import router as test_router
from app.routes.cancel import router as cancel_router

app = FastAPI(
    title="Super OPS Sampler",
    description="Backend API for dynamically downloading and processing CSVs from S3 or Wasabi for samples.",
    version="0.1.2"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.50.97:3000"],  # <-- Your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Preflight OPTIONS handler
@app.options("/{rest_of_path:path}")
async def preflight_handler():
    return JSONResponse(content={"status": "OK"})

# ✅ Include all routers
app.include_router(download.router, prefix="/api/download", tags=["Download"])
app.include_router(validate.router, prefix="/api/validate", tags=["Validate"])
app.include_router(test_router, prefix="/api/test", tags=["Test Endpoints"])
app.include_router(cancel_router, prefix="/api/cancel", tags=["Cancel"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Super OPS Sampler API!"}
