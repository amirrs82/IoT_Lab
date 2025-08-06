# IoT Lab Complete Setup Guide

This guide will help you set up the complete IoT Lab system using Docker Compos### Database issues:
1. Check if PostgreSQL container is running: `docker compose ps`
2. Check database logs: `docker compose logs db`
3. Restart the database: `docker compose restart db`

### Static files issues:
The system uses WhiteNoise to serve static files automatically. If you experience issues:
1. Static files are automatically collected during container startup
2. Check if backend container is running: `docker compose ps`
3. Restart backend to re-collect static files: `docker compose restart backend`
4. Verify static files are accessible: `curl -I http://localhost:10003/static/admin/css/base.css`hich includes:
- Frontend (Nginx serving static files)
- Backend (Django REST API)
- PostgreSQL Database
- Redis (for Celery)
- Celery Worker

## Prerequisites

- Docker
- Docker Compose

## Services and Ports

After running the system, the following services will be available:

- **Frontend**: http://localhost:10004
- **Backend API**: http://localhost:10003
- **PostgreSQL**: localhost:10001
- **Redis**: localhost:10002

## Quick Start

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd IoT_Lab
   ```

2. **Build and start all services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Open your browser and go to: http://localhost:10004
   - You'll be redirected to the login page

## Initial Setup

### Create a superuser (optional)
To access the Django admin panel:

```bash
docker compose exec backend python manage.py createsuperuser
```

*Note: The system uses WhiteNoise to serve static files automatically, so all Django admin styles and static assets are properly configured.*

### Access Django Admin
- URL: http://localhost:10003/admin/
- Use the superuser credentials you created

## API Endpoints

The backend provides the following authentication endpoints:

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile

## Frontend Features

- **Login Page**: `/pages/login.html`
- **Signup Page**: `/pages/signup.html`
- **Profile Page**: `/pages/profile.html`
- **Contracts Page**: `/pages/contracts.html`

## Development

### Backend Development
The backend code is in the `server/` directory. Changes to Python files will require a container restart:

```bash
docker-compose restart backend
```

### Frontend Development
The frontend code is in the `client/` directory. Changes to HTML/CSS/JS files will be immediately visible as the directory is mounted as a volume.

### Database Migration
To run database migrations:

```bash
docker-compose exec backend python manage.py migrate
```

## Environment Configuration

All environment variables are set in the `docker-compose.yml` file:

- **Database**: PostgreSQL with credentials in docker-compose.yml
- **Secret Key**: Set in environment variables
- **Debug Mode**: Disabled for production-like setup
- **CORS**: Configured to allow frontend access

## Troubleshooting

### If containers fail to start:
1. Check if ports 10001-10004 are available
2. Ensure Docker and Docker Compose are installed and running
3. Check logs: `docker-compose logs [service-name]`

### If frontend can't connect to backend:
1. Verify backend is running: `docker-compose ps`
2. Check backend logs: `docker-compose logs backend`
3. Ensure CORS settings are correct

### Database issues:
1. Check if PostgreSQL container is running: `docker-compose ps`
2. Check database logs: `docker-compose logs db`
3. Restart the database: `docker-compose restart db`

## Stop Services

To stop all services:
```bash
docker-compose down
```

To stop and remove all data (including database):
```bash
docker-compose down -v
```

## Production Notes

For production deployment:
1. Change secret keys and passwords
2. Set `DEBUG=False` in environment variables
3. Configure proper domain names in ALLOWED_HOSTS
4. Set up proper SSL/TLS certificates
5. Use a proper web server like Nginx with SSL termination
