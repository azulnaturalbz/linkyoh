# Docker Email Integration Guide

This guide explains how to use the `docker-compose.email.yml` file with the existing Docker Compose configurations (`docker-compose.app.yml` or `docker-compose.dev.yml`) to enable email functionality in the Linkyoh application.

## Overview

The Linkyoh application uses the following Docker Compose files:

- `docker-compose.yml`: Base configuration for production
- `docker-compose.app.yml`: Configuration for app-only mode (no Nginx)
- `docker-compose.dev.yml`: Configuration for development
- `docker-compose.email.yml`: Configuration for email services (RabbitMQ and Celery)

The email services are defined in `docker-compose.email.yml` and include:
- RabbitMQ: Message broker for Celery
- Celery Worker: Processes asynchronous tasks (like sending emails)
- Celery Beat: Schedules periodic tasks (if needed)

## Integration Methods

There are two main ways to integrate the email services with the existing application:

### Method 1: Using Docker Compose Override

Docker Compose allows you to use multiple configuration files with the `-f` flag. This is the recommended approach.

#### For Development Environment

```bash
docker-compose -f docker-compose.dev.yml -f docker-compose.email.yml up -d
```

This command will:
1. Start the web and nginx services from `docker-compose.dev.yml`
2. Start the rabbitmq, celery_worker, and celery_beat services from `docker-compose.email.yml`
3. Override the web service configuration to include the necessary environment variables for Celery

#### For App-Only Environment

```bash
docker-compose -f docker-compose.app.yml -f docker-compose.email.yml up -d
```

This command will:
1. Start the web service from `docker-compose.app.yml`
2. Start the rabbitmq, celery_worker, and celery_beat services from `docker-compose.email.yml`
3. Override the web service configuration to include the necessary environment variables for Celery

### Method 2: Creating a Combined Configuration

Alternatively, you can create a new Docker Compose file that combines the services you need.

1. Create a new file, e.g., `docker-compose.combined.yml`:

```yaml
version: '3'

services:
  # Include services from docker-compose.dev.yml or docker-compose.app.yml
  web:
    # Copy configuration from docker-compose.dev.yml or docker-compose.app.yml
    # Add the CELERY_BROKER_URL environment variable
    environment:
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
    depends_on:
      - rabbitmq
    networks:
      - linkyoh_network

  # For development, include nginx if needed
  nginx:
    # Copy configuration from docker-compose.dev.yml
    networks:
      - linkyoh_network

  # Include services from docker-compose.email.yml
  rabbitmq:
    image: rabbitmq:3-management
    container_name: linkyoh_rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=guest
      - RABBITMQ_DEFAULT_PASS=guest
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    restart: unless-stopped
    networks:
      - linkyoh_network

  celery_worker:
    build: .
    container_name: linkyoh_celery_worker
    command: celery -A linkyoh worker -l info
    volumes:
      - .:/app
    depends_on:
      - rabbitmq
      - web
    environment:
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
    restart: unless-stopped
    networks:
      - linkyoh_network

  celery_beat:
    build: .
    container_name: linkyoh_celery_beat
    command: celery -A linkyoh beat -l info
    volumes:
      - .:/app
    depends_on:
      - rabbitmq
      - web
    environment:
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
    restart: unless-stopped
    networks:
      - linkyoh_network

volumes:
  rabbitmq_data:
  # Include other volumes as needed

networks:
  linkyoh_network:
    driver: bridge
```

2. Start the services using the combined configuration:

```bash
docker-compose -f docker-compose.combined.yml up -d
```

## Environment Variables

Make sure the following environment variables are set in your `.env` file:

```
# Celery Configuration
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
```

## Networking

The `docker-compose.email.yml` file defines a network called `linkyoh_network`. When using Method 1 (Docker Compose Override), Docker Compose will automatically create this network and connect all services to it.

## Monitoring

### RabbitMQ Management Interface

The RabbitMQ management interface is available at http://localhost:15672/ (default credentials: guest/guest).

### Celery Flower (Optional)

For more advanced monitoring, you can add a Celery Flower service to your Docker Compose configuration:

```yaml
flower:
  build: .
  container_name: linkyoh_flower
  command: celery -A linkyoh flower
  ports:
    - "5555:5555"
  depends_on:
    - rabbitmq
    - celery_worker
  environment:
    - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
  restart: unless-stopped
  networks:
    - linkyoh_network
```

Flower will be available at http://localhost:5555/

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

### Viewing Logs

To view logs for a specific service:

```bash
docker-compose -f docker-compose.dev.yml -f docker-compose.email.yml logs -f celery_worker
```

## Example: Complete Development Setup

Here's a complete example of setting up the development environment with email services:

1. Ensure your `.env` file includes the necessary variables
2. Start all services:

```bash
docker-compose -f docker-compose.dev.yml -f docker-compose.email.yml up -d
```

3. Check that all services are running:

```bash
docker-compose -f docker-compose.dev.yml -f docker-compose.email.yml ps
```

4. Access the application at http://localhost:80
5. Access the RabbitMQ management interface at http://localhost:15672

## Example: Complete App-Only Setup

Here's a complete example of setting up the app-only environment with email services:

1. Ensure your `.env` file includes the necessary variables
2. Start all services:

```bash
docker-compose -f docker-compose.app.yml -f docker-compose.email.yml up -d
```

3. Check that all services are running:

```bash
docker-compose -f docker-compose.app.yml -f docker-compose.email.yml ps
```

4. Access the application at http://localhost:8000
5. Access the RabbitMQ management interface at http://localhost:15672