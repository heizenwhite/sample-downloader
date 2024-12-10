from fastapi import FastAPI
from app.routes import download, validate

app = FastAPI(
    title="CSV Downloader API",
    description="Backend API for dynamically downloading and processing CSVs from S3 or Wasabi.",
    version="1.0.0"
)

# Include Routes
app.include_router(download.router, prefix="/api/download", tags=["Download"])
app.include_router(validate.router, prefix="/api/validate", tags=["Validate"])