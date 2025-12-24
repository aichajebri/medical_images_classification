# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and other libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* 

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# Copy backend directory
COPY backend/ ./backend/

# Copy src directory (needed for inference service)
COPY src/ ./src/

# Copy outputs directory (contains trained model)
COPY outputs/ ./outputs/

# Create storage directories
RUN mkdir -p backend/storage/images \
    backend/storage/heatmaps \
    backend/storage/reports

# Expose port 8000
EXPOSE 8000

# Set environment variables with defaults
ENV DATABASE_URL=postgresql://postgres:admin@host.docker.internal:5433/brain_tumor_db
ENV MODEL_PATH=/app/outputs/step4_training/model_checkpoint.pth
ENV STORAGE_PATH=/app/backend/storage

# Run the application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

