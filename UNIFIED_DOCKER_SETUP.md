# Unified Docker Setup for Linkyoh

This document explains how to use the new unified Docker Compose file (`docker-compose.unified.yml`) for the Linkyoh application. This file combines all services from the separate Docker Compose files and allows for different environments and configurations.

## Overview

The unified Docker Compose file includes the following services:

- **web**: The Django application running with Gunicorn
- **nginx**: Web server with SSL termination (optional)
- **certbot**: For SSL certificate management (optional)
- **rabbitmq**: Message broker for Celery (optional)
- **celery_worker**: Processes asynchronous tasks like sending emails (optional)
- **celery_beat**: Schedules periodic tasks (optional)

All services are configured to use the same network (`linkyoh_network`) to ensure proper communication.

## Environment Variables

The unified Docker Compose file uses environment variables to control which services are started and how they're configured. Here are the key variables:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `ENVIRONMENT` | The deployment environment (dev, prod, app, standalone) | standalone |
| `ENABLE_EMAIL` | (Deprecated) Use profiles instead | true |
| `VOLUME_STATIC` | Volume name for static files | static_volume |
| `VOLUME_MEDIA` | Volume name for media files | media_volume |
| `STATIC_PATH` | Path to static files in the container | /linkyoh/static |
| `MEDIA_PATH` | Path to media files in the container | /linkyoh/media |
| `COLLECT_STATIC` | Command to collect static files | (empty) |
| `EXPOSE_WEB_PORT` | Port mapping for the web service | 127.0.0.1:8000:8000 |
| `NGINX_IMAGE` | Nginx image to use | nginx:latest |
| `NGINX_CONF_PATH` | Path to Nginx configuration | ./nginx/nginx |
| `CERTBOT_CONF_PATH` | Path to Certbot configuration | ./nginx/certbot/conf |
| `CERTBOT_WWW_PATH` | Path to Certbot webroot | ./nginx/certbot/www |
| `NGINX_HTTP_PORT` | HTTP port for Nginx | 80 |
| `NGINX_HTTPS_PORT` | HTTPS port for Nginx | 443 |
| `NGINX_COMMAND` | Command to run Nginx | nginx -g 'daemon off;' |
| `DOMAIN_NAME` | Domain name for SSL certificates | linkyoh.com |
| `CERTBOT_COMMAND` | Command to run Certbot | (see file) |
| `RABBITMQ_PORT` | RabbitMQ port | 5672 |
| `RABBITMQ_MANAGEMENT_PORT` | RabbitMQ management port | 15672 |
| `RABBITMQ_USER` | RabbitMQ username | guest |
| `RABBITMQ_PASS` | RabbitMQ password | guest |
| `CELERY_BROKER_URL` | URL for Celery broker | amqp://guest:guest@rabbitmq:5672// |

## Usage Examples

### Development Environment

For development, you typically want the web service, nginx, and optionally email services:

```bash
# Set environment variables
export ENVIRONMENT=dev
export NGINX_IMAGE=nginx:1.15-alpine
export NGINX_CONF_PATH=./nginx
export COLLECT_STATIC="python manage.py collectstatic --noinput &&"
export EXPOSE_WEB_PORT=8000:8000

# Start with email services
docker-compose -f docker-compose.unified.yml --profile with-email up -d

# Or without email services
docker-compose -f docker-compose.unified.yml --profile web-only up -d
```

### Production Environment

For production, you want all services including SSL:

```bash
# Set environment variables
export ENVIRONMENT=prod
export VOLUME_STATIC=/srv/static/linkyoh
export VOLUME_MEDIA=/srv/static/linkyoh/media
export STATIC_PATH=/linkyoh/static
export MEDIA_PATH=/linkyoh/media
export COLLECT_STATIC="python manage.py collectstatic --noinput &&"
export DOMAIN_NAME=yourdomain.com

# Start all services including SSL and email
docker-compose -f docker-compose.unified.yml --profile full up -d

# Or without email services
docker-compose -f docker-compose.unified.yml --profile web-only up -d
```

### App-Only Environment

For app-only mode (no nginx or certbot):

```bash
# Set environment variables
export ENVIRONMENT=app
export VOLUME_STATIC=/srv/static/linkyoh
export VOLUME_MEDIA=/srv/static/linkyoh/media
export STATIC_PATH=/linkyoh/static
export MEDIA_PATH=/linkyoh/media
export COLLECT_STATIC="python manage.py collectstatic --noinput &&"
export EXPOSE_WEB_PORT=8000:8000

# Start the web service only
docker-compose -f docker-compose.unified.yml --profile web-only up -d

# Or with email services
docker-compose -f docker-compose.unified.yml --profile with-email up -d
```

### Without Email Services

To run without email services, use the web-only profile:

```bash
# Set environment variables
export ENVIRONMENT=dev

# Start only web and nginx services (no email functionality)
docker-compose -f docker-compose.unified.yml --profile web-only up -d
```

## Using Docker Compose Profiles

The unified Docker Compose file supports Docker Compose profiles, which provide a more direct way to control which services are started:

```bash
# Start only web and nginx services (no email functionality)
docker-compose -f docker-compose.unified.yml --profile web-only up -d

# Start web, nginx, and email services (rabbitmq, celery_worker, celery_beat)
docker-compose -f docker-compose.unified.yml --profile with-email up -d

# Start all services including certbot for SSL
docker-compose -f docker-compose.unified.yml --profile full up -d
```

### Combining Environment Variables and Profiles

You can combine environment variables and profiles to achieve the exact configuration you need:

```bash
# Development environment with email services
export ENVIRONMENT=dev
export NGINX_IMAGE=nginx:1.15-alpine
export NGINX_CONF_PATH=./nginx
docker-compose -f docker-compose.unified.yml --profile with-email up -d

# Production environment without email services
export ENVIRONMENT=prod
export VOLUME_STATIC=/srv/static/linkyoh
export VOLUME_MEDIA=/srv/static/linkyoh/media
docker-compose -f docker-compose.unified.yml --profile web-only up -d
```

## Environment File

You can also create a `.env.unified` file with your environment variables:

```
ENVIRONMENT=dev
NGINX_IMAGE=nginx:1.15-alpine
NGINX_CONF_PATH=./nginx
COLLECT_STATIC=python manage.py collectstatic --noinput &&
EXPOSE_WEB_PORT=8000:8000
```

Then use it with Docker Compose:

```bash
docker-compose -f docker-compose.unified.yml --env-file .env.unified up -d
```

## Monitoring

### RabbitMQ Management Interface

The RabbitMQ management interface is available at http://localhost:15672/ (default credentials: guest/guest).

### Viewing Logs

To view logs for a specific service:

```bash
docker-compose -f docker-compose.unified.yml logs -f web
```

## Troubleshooting

### Common Issues

1. **Services can't communicate with each other**:
   - Ensure all services are on the same network (`linkyoh_network`)
   - Check that service names are correctly referenced in connection strings

2. **RabbitMQ connection errors**:
   - Ensure RabbitMQ is running and accessible
   - Check the CELERY_BROKER_URL environment variable

3. **Celery workers not processing tasks**:
   - Check Celery worker logs for errors
   - Ensure the Celery app is correctly configured in the Django application

4. **Nginx can't find static files**:
   - Check that the volume mounts are correct
   - Ensure collectstatic has been run

## Migration from Separate Docker Compose Files

If you're currently using the separate Docker Compose files, here's how to migrate to the unified file:

### From docker-compose.dev.yml

```bash
export ENVIRONMENT=dev
export NGINX_IMAGE=nginx:1.15-alpine
export NGINX_CONF_PATH=./nginx
# For development with web and nginx only
docker-compose -f docker-compose.unified.yml --profile web-only up -d
# Or with email services
docker-compose -f docker-compose.unified.yml --profile with-email up -d
```

### From docker-compose.app.yml

```bash
export ENVIRONMENT=app
export VOLUME_STATIC=/srv/static/linkyoh
export VOLUME_MEDIA=/srv/static/linkyoh/media
export STATIC_PATH=/linkyoh/static
export MEDIA_PATH=/linkyoh/media
export COLLECT_STATIC="python manage.py collectstatic --noinput &&"
export EXPOSE_WEB_PORT=8000:8000
# For app-only mode without email
docker-compose -f docker-compose.unified.yml --profile web-only up -d
# Or with email services
docker-compose -f docker-compose.unified.yml --profile with-email up -d
```

### From docker-compose.yml (Production)

```bash
export ENVIRONMENT=prod
# For a complete setup with all services including SSL and email
docker-compose -f docker-compose.unified.yml --profile full up -d
```

### From docker-compose.email.yml

Email services are included in the unified file and can be enabled using profiles:

```bash
# Add email services to any environment
docker-compose -f docker-compose.unified.yml --profile with-email up -d

# Or for a complete setup with all services
docker-compose -f docker-compose.unified.yml --profile full up -d
```
