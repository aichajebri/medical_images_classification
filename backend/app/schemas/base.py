from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import datetime, date
from typing import Optional, List, Union, Annotated

# --- Patient Schemas ---
class PatientBase(BaseModel):
    patient_id: str
    age: Optional[int] = None
    gender: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "protected_namespaces": ()
    }

# --- Study Schemas ---
class StudyBase(BaseModel):
    patient_id: int
    study_date: date
    modality: str = "MRI"
    
    model_config = ConfigDict(from_attributes=True)

class StudyCreate(StudyBase):
    @model_validator(mode='before')
    @classmethod
    def parse_study_date(cls, data):
        if isinstance(data, dict) and 'study_date' in data:
            study_date = data['study_date']
            if isinstance(study_date, str):
                try:
                    data['study_date'] = date.fromisoformat(study_date)
                except ValueError:
                    raise ValueError("study_date must be in YYYY-MM-DD format")
        return data

class Study(StudyBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

# --- Prediction Schemas ---
class PredictionBase(BaseModel):
    model_version: str = "resnet50_v1"
    model_config = {"protected_namespaces": ()}

class PredictionResponse(BaseModel):
    id: int
    image_id: int
    class_label: str
    confidence: float
    heatmap_path: str
    pdf_report_path: str
    processing_time: float
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

# --- Image Upload Result ---
class ImageUploadResponse(BaseModel):
    image_id: int
    filename: str
    file_path: str
