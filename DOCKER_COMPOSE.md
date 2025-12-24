# Docker Compose Setup

This document describes how to run the Brain Tumor Analysis API stack using Docker Compose.

## Prerequisites

- Docker and Docker Compose installed
- Backend Docker image built: `brain-tumor-api:latest`
  ```bash
  docker build -f backend/Dockerfile -t brain-tumor-api:latest .
  ```

## Initial Database Setup

**Important:** On first run, you need to initialize the database tables:

```bash
docker compose exec backend python -m backend.app.db.init_db
```

This creates all required tables (patients, studies, images, predictions) in PostgreSQL.

## Quick Start

### Start the Stack

```bash
docker compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- MongoDB database (port 27017)
- Backend API (port 8000)

**Note:** The backend takes 2-3 minutes to start as it loads the ML model. Wait for all services to show "healthy" status.

### Initialize Database (First Run Only)

After starting the stack, initialize the database tables:

```bash
docker compose exec backend python -m backend.app.db.init_db
```

This creates all required tables (patients, studies, images, predictions) in PostgreSQL.

### Stop the Stack

```bash
docker compose down
```

### Stop and Remove Volumes (⚠️ This deletes all data)

```bash
docker compose down -v
```

## Services

### Backend API
- **Port**: 8000
- **Health Check**: http://localhost:8000/health
- **Dependencies**: PostgreSQL, MongoDB
- **Storage**: Persistent volumes for images, heatmaps, and reports

### PostgreSQL Database
- **Port**: 5432
- **Database**: brain_tumor_db
- **User**: postgres
- **Password**: admin
- **Volume**: postgres_data (persistent)

### MongoDB Database
- **Port**: 27017
- **Database**: brain_tumor_metadata
- **Volume**: mongo_data (persistent)

## Environment Variables

The stack uses environment variables defined in `docker-compose.yml`. You can override them by:

1. Creating a `.env` file (copy from `.env.example`)
2. Using `-e` flags in docker compose commands
3. Modifying `docker-compose.yml` directly

## Verify the Stack

### Check Service Status

```bash
docker compose ps
```

### View Logs

**All services:**
```bash
docker compose logs
```

**Specific service:**
```bash
docker compose logs backend
docker compose logs postgres
docker compose logs mongo
```

### Follow Logs (Real-time)

```bash
docker compose logs -f backend
```

### Test Health Endpoint

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

### Test API Endpoints

**Create a Patient:**
```bash
curl -X POST http://localhost:8000/patients \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "P001", "age": 45, "gender": "M"}'
```

**Windows PowerShell:**
```powershell
$body = @{patient_id='P001'; age=45; gender='M'} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/patients -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing
```

**List Patients:**
```bash
curl http://localhost:8000/patients
```

**Windows PowerShell:**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/patients -UseBasicParsing | Select-Object -ExpandProperty Content
```

## Database Access

### PostgreSQL

**Connect from host:**
```bash
docker exec -it brain-tumor-postgres psql -U postgres -d brain_tumor_db
```

**Or using docker compose:**
```bash
docker compose exec postgres psql -U postgres -d brain_tumor_db
```

### MongoDB

**Connect from host:**
```bash
docker exec -it brain-tumor-mongo mongosh brain_tumor_metadata
```

**Or using docker compose:**
```bash
docker compose exec mongo mongosh brain_tumor_metadata
```

## Storage Volumes

The backend storage directories are mounted as volumes:
- `./backend/storage/images` → `/app/backend/storage/images`
- `./backend/storage/heatmaps` → `/app/backend/storage/heatmaps`
- `./backend/storage/reports` → `/app/backend/storage/reports`

Data persists on the host filesystem, so uploaded images, heatmaps, and reports are preserved between container restarts.

## Troubleshooting

### Backend fails to start

1. Check if the Docker image exists:
   ```bash
   docker images | grep brain-tumor-api
   ```

2. If missing, build it:
   ```bash
   docker build -f backend/Dockerfile -t brain-tumor-api:latest .
   ```

3. Check backend logs:
   ```bash
   docker compose logs backend
   ```

### Database connection issues

1. Verify databases are healthy:
   ```bash
   docker compose ps
   ```

2. Check database logs:
   ```bash
   docker compose logs postgres
   ```

3. Ensure DATABASE_URL uses service name `postgres` (not `localhost` or `host.docker.internal`)

### Port conflicts

If ports 8000, 5432, or 27017 are already in use, modify the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Use 8001 on host instead of 8000
```

## Network

All services are connected via the `brain-tumor-network` bridge network. Services can communicate using their service names:
- Backend → PostgreSQL: `postgres:5432`
- Backend → MongoDB: `mongo:27017`

## Production Considerations

For production deployments, consider:

1. **Security**: Change default passwords
2. **Secrets Management**: Use Docker secrets or external secret management
3. **Resource Limits**: Add CPU/memory limits to services
4. **Backup Strategy**: Regular backups of database volumes
5. **Monitoring**: Add monitoring and logging solutions
6. **SSL/TLS**: Use reverse proxy with SSL certificates

