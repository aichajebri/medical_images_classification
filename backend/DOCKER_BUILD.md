# Docker Build Instructions

## Build the Docker Image

From the project root directory (`Medical/`), run:

```bash
docker build -f backend/Dockerfile -t brain-tumor-api:latest .
```

## Run the Container

### Basic Run (with default environment variables)

**Detached mode (recommended for production):**
```bash
docker run -d -p 8000:8000 --name brain-tumor-api brain-tumor-api:latest
```

**Foreground mode (for testing/debugging):**
```bash
docker run -p 8000:8000 brain-tumor-api:latest
```

### Run with Custom Environment Variables

**Linux/Mac:**
```bash
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql://postgres:admin@host.docker.internal:5433/brain_tumor_db" \
  -e MODEL_PATH="/app/outputs/step4_training/model_checkpoint.pth" \
  -e STORAGE_PATH="/app/backend/storage" \
  --name brain-tumor-api \
  brain-tumor-api:latest
```

**Windows PowerShell:**
```powershell
docker run -d -p 8000:8000 `
  -e DATABASE_URL="postgresql://postgres:admin@host.docker.internal:5433/brain_tumor_db" `
  -e MODEL_PATH="/app/outputs/step4_training/model_checkpoint.pth" `
  -e STORAGE_PATH="/app/backend/storage" `
  --name brain-tumor-api `
  brain-tumor-api:latest
```

### Run with Volume Mounts (for persistent storage)

**Linux/Mac:**
```bash
docker run -d -p 8000:8000 \
  -v $(pwd)/backend/storage:/app/backend/storage \
  -e DATABASE_URL="postgresql://postgres:admin@host.docker.internal:5433/brain_tumor_db" \
  --name brain-tumor-api \
  brain-tumor-api:latest
```

**Windows PowerShell:**
```powershell
docker run -d -p 8000:8000 `
  -v ${PWD}/backend/storage:/app/backend/storage `
  -e DATABASE_URL="postgresql://postgres:admin@host.docker.internal:5433/brain_tumor_db" `
  --name brain-tumor-api `
  brain-tumor-api:latest
```

## Verify the Container

Once the container is running, test the health endpoint:

**Linux/Mac:**
```bash
curl http://localhost:8000/health
```

**Windows PowerShell:**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing | Select-Object -ExpandProperty Content
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Brain Tumor Analysis API"
}
```

### View Container Logs

```bash
docker logs brain-tumor-api
```

### Stop and Remove Container

```bash
docker stop brain-tumor-api
docker rm brain-tumor-api
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://postgres:admin@host.docker.internal:5433/brain_tumor_db`)
- `MODEL_PATH`: Path to the trained model checkpoint (default: `/app/outputs/step4_training/model_checkpoint.pth`)
- `STORAGE_PATH`: Path for storing images, heatmaps, and reports (default: `/app/backend/storage`)

## Notes

- The container uses `host.docker.internal` to connect to the host's PostgreSQL database
- For Linux, you may need to use `--network host` or the actual host IP instead of `host.docker.internal`
- Ensure PostgreSQL is accessible from the container on port 5433

