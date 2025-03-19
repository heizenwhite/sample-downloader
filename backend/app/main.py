from fastapi import FastAPI
from app.routes import download, validate
from app.routes.test_endpoints import router as test_router
from app.routes.cancel import router as cancel_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Super OPS Sampler",
    description="Backend API for dynamically downloading and processing CSVs from S3 or Wasabi for samples.",
    version="0.1.2"
)

app.include_router(download.router, prefix="/api/download", tags=["Download"])
app.include_router(validate.router, prefix="/api/validate", tags=["Validate"])
app.include_router(test_router, prefix="/api/test", tags=["Test Endpoints"])
app.include_router(cancel_router, prefix="/api/cancel", tags=["Cancellation"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for stricter dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Super OPS Sampler API!"}
