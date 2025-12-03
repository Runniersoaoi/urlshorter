# Deployment Guide

This project is configured to be deployed using Docker and Docker Compose.

## Prerequisites
- Docker
- Docker Compose

## Configuration
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and set your secure passwords and secret keys.

## Running the Application
To start the application in production mode:

```bash
docker-compose up --build -d
```

## Accessing the Application
- **Frontend**: http://localhost (Port 80)
- **Backend API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

## Services
- **Frontend**: Nginx serving Vue 3 app.
- **Backend**: FastAPI (Python 3.13) running with Uvicorn.
- **Database**: PostgreSQL 15.
- **Redis**: Redis 7 (Caching & Rate Limiting).
- **ML Service**: Python service for URL safety checks.
