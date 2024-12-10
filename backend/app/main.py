from fastapi import FastAPI
from app.routes import download, validate

# Initialize the FastAPI app
app = FastAPI(
    title="Super OPS Sampler",
    description="Backend API for dynamically downloading and processing CSVs from S3 or Wasabi for samples.",
    version="0.1.2"
)

# Include Routers
app.include_router(download.router, prefix="/api/download", tags=["Download"])
app.include_router(validate.router, prefix="/api/validate", tags=["Validate"])

# Optional Root Path
@app.get("/")
async def root():
    return {"message": "Welcome to the Super OPS Sampler API!"}