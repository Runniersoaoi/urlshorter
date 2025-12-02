# URL Shortener Platform

A professional, scalable, and modular URL Shortener Platform built with modern technologies.

## Features
- **Secure URL Shortening**: Uses Hashids for non-predictable short IDs.
- **Advanced Analytics**: Tracks clicks, browsers, countries (GeoIP ready), OS, and referrers.
- **ML-Powered Safety**: Integrated Machine Learning microservice to detect and block phishing/suspicious URLs.
- **High Performance**: Redis caching for instant redirections and rate limiting.
- **Modern Frontend**: Vue 3 + Vite + TailwindCSS for a responsive and elegant UI.
- **Dockerized**: Fully containerized for easy deployment anywhere (no cloud lock-in).

## Architecture

The system follows a microservices-inspired architecture:

- **Frontend**: Vue 3 SPA (Port 3000)
- **Backend**: FastAPI (Port 8000)
- **Database**: PostgreSQL (Port 5432)
- **Cache**: Redis (Port 6379)
- **ML Service**: Python/FastAPI (Port 8001)

## Getting Started

### Prerequisites
- Docker & Docker Compose

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd urlshortener
   ```

2. Start the services:
   ```bash
   docker-compose up --build -d
   ```

3. Access the application:
   - **Frontend**: [http://localhost:3000](http://localhost:3000)
   - **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## API Endpoints

### Public
- `POST /shorten`: Create a new short URL.
- `GET /{short_id}`: Redirect to the original URL.
- `GET /stats/{short_id}`: Get analytics for a short URL.

### Internal/Admin
- `GET /health`: System health check.

## Development

### Project Structure
```
urlshortener/
├── backend/            # FastAPI Application
├── frontend/           # Vue 3 Application
├── ml_service/         # ML Microservice
├── docker-compose.yml  # Orchestration
└── README.md           # This file
```

### Running Tests
To run backend tests (requires local environment setup or running inside container):
```bash
cd backend
pytest
```

## Deployment
This project is designed to be deployed on any VPS (DigitalOcean, Linode, Hetzner, etc.) using Docker Compose.
1. Provision a VPS.
2. Install Docker & Docker Compose.
3. Clone repo and run `docker-compose up -d`.
4. Configure Nginx as a reverse proxy for ports 3000 and 8000.

## License
MIT
