from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .api.routes import patients, predictions
from .db.base import engine
from .db import models
import traceback
import os

# In a real environment, you'd use Alembic. 
# For this demo, we can create tables on startup if desired, 
# but we'll use our script as requested.
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Brain Tumor Analysis API", version="1.0.0")

# Get storage path
STORAGE_PATH_ENV = os.getenv("STORAGE_PATH")
if STORAGE_PATH_ENV:
    STORAGE_DIR = Path(STORAGE_PATH_ENV)
else:
    STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage"

# Ensure storage directories exist
(STORAGE_DIR / "images").mkdir(parents=True, exist_ok=True)
(STORAGE_DIR / "heatmaps").mkdir(parents=True, exist_ok=True)
(STORAGE_DIR / "reports").mkdir(parents=True, exist_ok=True)

# Mount static files directory for serving heatmaps and reports
app.mount("/storage", StaticFiles(directory=str(STORAGE_DIR)), name="storage")

# CORS Configuration - Allow all origins for development
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*",  # Allow all origins for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Global exception handler to ensure CORS headers are always present
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = str(exc)
    print(f"Error processing request: {error_detail}")
    print(traceback.format_exc())
    
    # Get origin from request
    origin = request.headers.get("origin", "*")
    
    response = JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {error_detail}"}
    )
    
    # Add CORS headers to error response
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response

# Handle OPTIONS requests for CORS preflight
@app.options("/{rest_of_path:path}")
async def options_handler(request: Request, rest_of_path: str):
    origin = request.headers.get("origin", "*")
    response = JSONResponse(content={})
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response

# Routes
app.include_router(patients.router, prefix="/api", tags=["Patients"])
app.include_router(predictions.router, prefix="/api", tags=["Analysis"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Brain Tumor Analysis API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
