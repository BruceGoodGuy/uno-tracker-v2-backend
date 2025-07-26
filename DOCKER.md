# Docker Usage Guide

## Quick Start with Docker

### Development Environment

1. **Clone and setup**:
```bash
git clone https://github.com/BruceGoodGuy/uno-tracker-v2.git
cd uno-tracker-backend
```

2. **Create environment file**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start all services**:
```bash
docker-compose up -d
```

4. **View logs**:
```bash
docker-compose logs -f backend
```

5. **Stop services**:
```bash
docker-compose down
```

### Production Deployment

1. **Use production compose**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

2. **View production logs**:
```bash
docker-compose -f docker-compose.prod.yml logs -f backend
```

## Docker Commands

### Build and Run

```bash
# Build the image
docker build -t uno-tracker-backend .

# Run development container
docker run -p 8000:8000 --env-file .env uno-tracker-backend

# Run production container
docker build -f Dockerfile.prod -t uno-tracker-backend-prod .
docker run -p 8000:8000 --env-file .env.prod uno-tracker-backend-prod
```

### Database Operations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Access database
docker-compose exec db psql -U uno_user -d uno_tracker
```

### Debugging

```bash
# Access container shell
docker-compose exec backend bash

# View application logs
docker-compose logs backend

# Restart a service
docker-compose restart backend
```

## Environment Variables

Required environment variables for Docker deployment:

```env
# Database
POSTGRES_USER=uno_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=uno_tracker

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-secret

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

## Services

The docker-compose setup includes:

- **backend**: FastAPI application (port 8000)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)
- **migrations**: One-time migration runner

## Volumes

- `postgres_data`: Database persistence
- `redis_data`: Redis data persistence

## Networks

All services communicate through the `uno-network` bridge network.

## Health Checks

All services include health checks:
- **Database**: PostgreSQL connection test
- **Redis**: Redis ping test  
- **Backend**: HTTP health endpoint

## Production Notes

- Use `docker-compose.prod.yml` for production
- Set `COOKIE_SECURE=true` in production
- Use strong passwords and secrets
- Consider using Docker secrets for sensitive data
- Set up proper logging and monitoring
