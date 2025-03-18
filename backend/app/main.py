from fastapi import FastAPI
from app.routes import download, validate
from app.routes.test_endpoints import router as test_router


app = FastAPI(
    title="Super OPS Sampler",
    description="Backend API for dynamically downloading and processing CSVs from S3 or Wasabi for samples.",
    version="0.1.2"
)

app.include_router(download.router, prefix="/api/download", tags=["Download"])
app.include_router(validate.router, prefix="/api/validate", tags=["Validate"])
app.include_router(test_router, prefix="/api/test", tags=["Test Endpoints"])


@app.get("/")
async def root():
    return {"message": "Welcome to the Super OPS Sampler API!"}
