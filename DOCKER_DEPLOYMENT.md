# Docker Deployment Options

This document outlines the different Docker deployment options available for the Linkyoh application.

## Deployment Scenarios

### 1. Development Environment

Use `docker-compose.dev.yml` for local development. This setup doesn't include SSL certificates and only exposes HTTP.

```bash
docker-compose -f docker-compose.dev.yml up
```

### 2. Standalone Deployment with Nginx and SSL

Use `docker-compose.standalone.yml` for a complete standalone deployment that includes:
- The web application
- Nginx for serving static files and as a reverse proxy
- Automatic SSL certificate management with Let's Encrypt

This is suitable when you need to run the application with its own Nginx server and SSL certificates.

```bash
# Set your domain name (defaults to linkyoh.com if not specified)
export DOMAIN_NAME=yourdomain.com

# Initialize SSL certificates
bash init-letsencrypt-template.sh

# Start the application
docker-compose -f docker-compose.standalone.yml up -d
```

### 3. Application-Only Deployment (Behind a Load Balancer)

Use `docker-compose.app.yml` when deploying behind a load balancer or reverse proxy (like Apache). This setup only includes the web application and exposes it on port 8000.

```bash
docker-compose -f docker-compose.app.yml up -d
```

The application automatically detects and adds the server's IP address to Django's `ALLOWED_HOSTS` setting. This allows direct access to the application via the server's IP address and port (e.g., `192.168.1.156:8000`) without getting an "Invalid HTTP_HOST header" error.

## SSL Certificate Management

### For Standalone Deployment

The standalone deployment includes automatic SSL certificate management with Let's Encrypt. Certificates are automatically renewed by the certbot service.

To initialize certificates for a new domain:

```bash
export DOMAIN_NAME=yourdomain.com
export EMAIL=your-email@example.com  # Optional, defaults to dev@silvatech.org
export STAGING=0  # Set to 1 for testing to avoid rate limits

bash init-letsencrypt-template.sh
```

### For Application-Only Deployment

When using the application-only deployment, SSL termination should be handled by your external load balancer or reverse proxy (e.g., Apache). Make sure to configure your proxy to forward requests to the application on port 8000.

For detailed instructions on configuring Apache as a reverse proxy for the Linkyoh application, see [APACHE_CONFIGURATION.md](APACHE_CONFIGURATION.md).

## Environment Variables

All deployment options use the same environment variables for application configuration. These can be set in a `.env` file or passed directly to the docker-compose command.

### Deployment Mode

The application now uses a `LYDEPLOYMENT_MODE` environment variable to automatically configure settings based on the deployment scenario:

- `dev`: Development mode with Nginx serving static files
- `standalone`: Production mode with Nginx and SSL
- `app`: Application-only mode where Django serves static files directly

This environment variable is automatically set in each docker-compose file, but you can override it if needed:

```bash
# Example: Force app mode in development
LYDEPLOYMENT_MODE=app docker-compose -f docker-compose.dev.yml up
```

### Static and Media Files

The application handles static and media files differently based on the deployment mode:

- In `dev` and `standalone` modes, Nginx serves static and media files
- In `app` mode, Django serves static files using WhiteNoise middleware

#### Host Paths for Static and Media Files

In `app` mode, the application uses host paths for static and media files:

```yaml
volumes:
  - /srv/static/linkyoh:/linkyoh/static:rw      # ← host path
  - /srv/static/linkyoh/media:/linkyoh/media:rw # ← host path
```

Make sure these directories exist on your host machine and have the correct permissions:

```bash
# Create directories if they don't exist
mkdir -p /srv/static/linkyoh/media

# Set correct permissions
chmod -R 755 /srv/static/linkyoh
chown -R $(whoami):$(whoami) /srv/static/linkyoh
```

When using `app` mode, the application automatically runs `collectstatic` during startup to ensure all static files are collected into the static directory.

## Troubleshooting

### SSL Certificate Issues

If you encounter SSL certificate issues:

1. Check the certificate expiration date:
   ```bash
   docker-compose -f docker-compose.standalone.yml exec nginx openssl x509 -in /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem -text -noout | grep "Not After"
   ```

2. Force certificate renewal:
   ```bash
   docker-compose -f docker-compose.standalone.yml exec certbot certbot renew --force-renewal
   docker-compose -f docker-compose.standalone.yml exec nginx nginx -s reload
   ```

3. Check certbot logs:
   ```bash
   docker-compose -f docker-compose.standalone.yml logs certbot
   ```

### Nginx Configuration

If you need to modify the Nginx configuration:

1. Edit the template file: `nginx/nginx/default.conf.template`
2. Restart the Nginx service:
   ```bash
   docker-compose -f docker-compose.standalone.yml restart nginx
   ```
