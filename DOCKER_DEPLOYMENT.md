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

## Environment Variables

All deployment options use the same environment variables for application configuration. These can be set in a `.env` file or passed directly to the docker-compose command.

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