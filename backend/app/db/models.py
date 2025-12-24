from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True, nullable=False) # Clinical ID
    age = Column(Integer)
    gender = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    studies = relationship("Study", back_populates="patient")

class Study(Base):
    __tablename__ = "studies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    study_date = Column(Date, nullable=False)
    modality = Column(String, default="MRI")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="studies")
    images = relationship("Image", back_populates="study")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(Integer, ForeignKey("studies.id"))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(BigInteger)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    study = relationship("Study", back_populates="images")
    prediction = relationship("Prediction", uselist=False, back_populates="image")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"))
    model_version = Column(String, default="resnet50_v1")
    class_label = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    heatmap_path = Column(String)
    pdf_report_path = Column(String)
    processing_time = Column(Float) # in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    image = relationship("Image", back_populates="prediction")
