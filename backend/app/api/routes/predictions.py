from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import os

from ...db.base import get_db
from ...db import models
from ...schemas import base as schemas
from ...services.inference_service import inference_service

router = APIRouter()

# Get storage path from environment or use default
STORAGE_PATH_ENV = os.getenv("STORAGE_PATH")
if STORAGE_PATH_ENV:
    STORAGE_DIR = Path(STORAGE_PATH_ENV)
else:
    # Path: predictions.py -> routes -> api -> app -> backend
    # So parent.parent.parent.parent gets us to backend folder
    STORAGE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "storage"

# Ensure storage directories exist
(STORAGE_DIR / "images").mkdir(parents=True, exist_ok=True)
(STORAGE_DIR / "heatmaps").mkdir(parents=True, exist_ok=True)
(STORAGE_DIR / "reports").mkdir(parents=True, exist_ok=True)

@router.post("/predict", response_model=schemas.PredictionResponse)
async def predict(study_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Verify Study
    db_study = db.query(models.Study).filter(models.Study.id == study_id).first()
    if not db_study:
        raise HTTPException(status_code=404, detail="Study not found")

    # 2. Save Uploaded Image
    file_path = STORAGE_DIR / "images" / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 3. Insert Image Record
    db_image = models.Image(
        study_id=study_id,
        filename=file.filename,
        file_path=f"storage/images/{file.filename}",
        file_size=os.path.getsize(file_path)
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    # 4. Run Inference
    try:
        results = inference_service.run_full_inference(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

    # 5. Insert Prediction Record
    db_prediction = models.Prediction(
        image_id=db_image.id,
        class_label=results["class_label"],
        confidence=results["confidence"],
        heatmap_path=results["heatmap_path"],
        pdf_report_path=results["pdf_path"],
        processing_time=results["processing_time"]
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)

    return db_prediction

@router.get("/predictions/{prediction_id}", response_model=schemas.PredictionResponse)
def get_prediction(prediction_id: int, db: Session = Depends(get_db)):
    db_prediction = db.query(models.Prediction).filter(models.Prediction.id == prediction_id).first()
    if not db_prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return db_prediction

@router.get("/reports/{prediction_id}")
def get_report(prediction_id: int, db: Session = Depends(get_db)):
    db_prediction = db.query(models.Prediction).filter(models.Prediction.id == prediction_id).first()
    if not db_prediction or not db_prediction.pdf_report_path:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # The pdf_report_path is stored as "storage/reports/filename.pdf"
    # We need to resolve it relative to STORAGE_DIR
    pdf_filename = db_prediction.pdf_report_path.replace("storage/reports/", "")
    pdf_path = STORAGE_DIR / "reports" / pdf_filename
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"Report file not found at {pdf_path}")
    
    return FileResponse(path=str(pdf_path), filename=f"Report_{prediction_id}.pdf", media_type='application/pdf')
