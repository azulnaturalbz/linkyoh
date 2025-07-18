# Apache Configuration for Linkyoh Docker Deployment

This document provides instructions for configuring Apache as a reverse proxy for the Linkyoh application deployed using Docker.

## Overview

When using the `docker-compose.app.yml` deployment option, the Linkyoh application is exposed on port 8000 without SSL termination. Apache can be configured as a reverse proxy to:

1. Handle SSL termination
2. Redirect HTTP to HTTPS
3. Forward requests to the Linkyoh application

The Linkyoh application automatically:
- Detects and adds the server's IP address to Django's `ALLOWED_HOSTS` setting, allowing direct access via IP:PORT
- Sets the deployment mode to 'app', which configures Django to serve static files directly using WhiteNoise
- Runs `collectstatic` during startup to gather all static files
- Uses host paths for static and media files: `/srv/static/linkyoh` and `/srv/static/linkyoh/media`

This configuration ensures that the application works correctly when accessed through Apache or directly via its IP address and port (e.g., `192.168.1.156:8000`).

## Updating Apache Configuration

### Current Configuration

Your current Apache configuration files are:

```apache
# HTTP Configuration (port 80)
<VirtualHost *:80>
    ServerAdmin dev@silvatech.bz
    ServerName linkyoh.com
    ServerAlias www.linkyoh.com

    ProxyPreserveHost On
    ProxyAddHeaders On
    ProxyPass / http://192.168.1.156/
    ProxyPassReverse / http://192.168.1.156/

    ErrorLog /var/log/httpd/linkyoh-error.log
    CustomLog /var/log/httpd/linkyoh-access.log combined

    RewriteEngine on
    RewriteCond %{SERVER_NAME} =www.linkyoh.com [OR]
    RewriteCond %{SERVER_NAME} =linkyoh.com
    RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>

# HTTPS Configuration (port 443)
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerAdmin dev@silvatech.bz
    ServerName linkyoh.com
    ServerAlias www.linkyoh.com

    ProxyPreserveHost On
    ProxyAddHeaders On
    SSLProxyEngine on
    SSLProxyVerify none
    SSLProxyCheckPeerCN off
    SSLProxyCheckPeerName off
    SSLProxyProtocol all -SSLv3
    SSLProxyCipherSuite HIGH:MEDIUM:!aNULL:!MD5

    ProxyPass / https://192.168.1.156/
    ProxyPassReverse / https://192.168.1.156/

    ErrorLog /var/log/httpd/linkyoh-error.log
    CustomLog /var/log/httpd/linkyoh-access.log combined

    Include /etc/letsencrypt/options-ssl-apache.conf
    SSLCertificateFile /etc/letsencrypt/live/marketday.store/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/marketday.store/privkey.pem
</VirtualHost>
</IfModule>
```

### Updated Configuration

To work with the `docker-compose.app.yml` deployment, you need to update your Apache configuration files as follows:

```apache
# HTTP Configuration (port 80)
<VirtualHost *:80>
    ServerAdmin dev@silvatech.bz
    ServerName linkyoh.com
    ServerAlias www.linkyoh.com

    ProxyPreserveHost On
    ProxyAddHeaders On

    # Updated to point to port 8000 where the Docker container is listening
    ProxyPass / http://192.168.1.156:8000/
    ProxyPassReverse / http://192.168.1.156:8000/

    ErrorLog /var/log/httpd/linkyoh-error.log
    CustomLog /var/log/httpd/linkyoh-access.log combined

    RewriteEngine on
    RewriteCond %{SERVER_NAME} =www.linkyoh.com [OR]
    RewriteCond %{SERVER_NAME} =linkyoh.com
    RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>

# HTTPS Configuration (port 443)
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerAdmin dev@silvatech.bz
    ServerName linkyoh.com
    ServerAlias www.linkyoh.com

    ProxyPreserveHost On
    ProxyAddHeaders On

    # No need for SSL proxy settings since we're connecting to HTTP backend
    # SSLProxyEngine on
    # SSLProxyVerify none
    # SSLProxyCheckPeerCN off
    # SSLProxyCheckPeerName off
    # SSLProxyProtocol all -SSLv3
    # SSLProxyCipherSuite HIGH:MEDIUM:!aNULL:!MD5

    # Updated to point to port 8000 and use HTTP (not HTTPS)
    ProxyPass / http://192.168.1.156:8000/
    ProxyPassReverse / http://192.168.1.156:8000/

    ErrorLog /var/log/httpd/linkyoh-error.log
    CustomLog /var/log/httpd/linkyoh-access.log combined

    Include /etc/letsencrypt/options-ssl-apache.conf
    SSLCertificateFile /etc/letsencrypt/live/marketday.store/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/marketday.store/privkey.pem
</VirtualHost>
</IfModule>
```

## Key Changes

1. **Port Change**: Updated ProxyPass and ProxyPassReverse to point to port 8000 where the Docker container is listening.
2. **Protocol Change**: For the HTTPS virtual host, changed the backend protocol from HTTPS to HTTP since SSL termination is now handled by Apache.
3. **SSL Proxy Settings**: Removed or commented out SSL proxy settings in the HTTPS virtual host since they're not needed when connecting to an HTTP backend.

## Handling Static and Media Files

When the Django application is running on a different server than Apache, there are several approaches to handle static and media files:

### Summary of Approaches

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| Proxy to Django | Simple setup, no additional configuration | Puts load on Django app, less efficient | Development, small sites |
| NFS Mount | Real-time access to files, no sync delay | Requires NFS setup, potential network issues | Medium-sized sites, shared infrastructure |
| rsync | Simple to set up, works across networks | Periodic sync means potential delay in new files appearing | Medium to large sites |
| CDN | Best performance, scalable | More complex setup, potential cost | Production, high-traffic sites |

### Option 1: Proxy All Requests to Django (Current Configuration)

The current configuration proxies all requests to the Django application, including requests for static and media files. This works but is not optimal for performance as it puts additional load on the Django application.

### Option 2: Configure Apache to Serve Static and Media Files Directly

For better performance, you can configure Apache to serve static and media files directly. This requires:

1. Making the static and media directories accessible to Apache
2. Configuring Apache to serve these files directly

#### Step 1: Share Static and Media Files


#### Step 2: Update Apache Configuration

Update your Apache configuration to serve static and media files directly:

```apache
# HTTP Configuration (port 80)
<VirtualHost *:80>
    ServerAdmin dev@silvatech.bz
    ServerName linkyoh.com
    ServerAlias www.linkyoh.com

    ProxyPreserveHost On
    ProxyAddHeaders On

    # Serve static and media files directly
    Alias /static/ /mnt/linkyoh/
    Alias /media/ /mnt/linkyoh/media/

    <Directory /mnt/linkyoh>
        Require all granted
    </Directory>

    <Directory /mnt/linkyoh/media>
        Require all granted
    </Directory>

    # Proxy everything else to Django
    ProxyPass /static/ !
    ProxyPass /media/ !
    ProxyPass / http://192.168.1.156:8000/
    ProxyPassReverse / http://192.168.1.156:8000/

    ErrorLog /var/log/httpd/linkyoh-error.log
    CustomLog /var/log/httpd/linkyoh-access.log combined

    RewriteEngine on
    RewriteCond %{SERVER_NAME} =www.linkyoh.com [OR]
    RewriteCond %{SERVER_NAME} =linkyoh.com
    RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>

# HTTPS Configuration (port 443)
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerAdmin dev@silvatech.bz
    ServerName linkyoh.com
    ServerAlias www.linkyoh.com

    ProxyPreserveHost On
    ProxyAddHeaders On

    # Serve static and media files directly
    Alias /static/ /mnt/linkyoh/
    Alias /media/ /mnt/linkyoh/media/

    <Directory /mnt/linkyoh>
        Require all granted
    </Directory>

    <Directory /mnt/linkyoh/media>
        Require all granted
    </Directory>

    # Proxy everything else to Django
    ProxyPass /static/ !
    ProxyPass /media/ !
    ProxyPass / http://192.168.1.156:8000/
    ProxyPassReverse / http://192.168.1.156:8000/

    ErrorLog /var/log/httpd/linkyoh-error.log
    CustomLog /var/log/httpd/linkyoh-access.log combined

    Include /etc/letsencrypt/options-ssl-apache.conf
    SSLCertificateFile /etc/letsencrypt/live/marketday.store/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/marketday.store/privkey.pem
</VirtualHost>
</IfModule>
```

### Option 3: Use a CDN for Static Files

For production environments, consider using a CDN (Content Delivery Network) for static files:

1. Configure Django to use a CDN for static files by setting `STATIC_URL` to the CDN URL
2. Upload static files to the CDN during deployment
3. Configure the CDN to serve files from your domain

## SSL Certificate Management

With this configuration:

1. SSL certificates are managed by Let's Encrypt on the Apache server
2. Certificate renewal is handled by certbot on the Apache server
3. The Linkyoh application doesn't need to handle SSL

## File Upload Configuration

### Configuring Apache for Large File Uploads

By default, Apache has limits on file upload sizes that may prevent users from uploading large images or multiple files. To configure Apache to handle large file uploads:

1. Add the following directives to your Apache configuration file (either in the main configuration or in the virtual host):

```apache
# Increase timeout values to handle large uploads
Timeout 600
ProxyTimeout 600

# Increase the maximum request body size (value in bytes, 50MB = 52428800)
LimitRequestBody 52428800

# If using mod_proxy, increase the maximum request size
<IfModule mod_proxy.c>
    ProxyPass / http://192.168.1.156:8000/ timeout=600
    ProxyPassReverse / http://192.168.1.156:8000/
</IfModule>
```

2. If you're using PHP (for any part of your application), also update the PHP configuration:

```apache
<IfModule mod_php7.c>
    php_value upload_max_filesize 50M
    php_value post_max_size 50M
    php_value max_input_time 300
    php_value max_execution_time 300
</IfModule>
```

3. Restart Apache to apply the changes:

```bash
systemctl restart httpd
```

### Configuring Django for Large File Uploads

In your Django settings, ensure you have the following settings:

```python
# Maximum size of request body (in bytes)
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB

# Maximum size of a request's POST parameters (in bytes)
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Maximum size of a file upload (in bytes)
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
```

## Troubleshooting

### Connection Issues

If you encounter connection issues:

1. Verify the Docker container is running:
   ```bash
   docker-compose -f docker-compose.app.yml ps
   ```

2. Check if port 8000 is accessible from the Apache server:
   ```bash
   curl http://192.168.1.156:8000/
   ```

3. Check Apache error logs:
   ```bash
   tail -f /var/log/httpd/linkyoh-error.log
   ```

### SSL Certificate Issues

If you encounter SSL certificate issues:

1. Check the certificate expiration date:
   ```bash
   certbot certificates
   ```

2. Renew certificates if needed:
   ```bash
   certbot renew
   ```

3. Restart Apache after certificate renewal:
   ```bash
   systemctl restart httpd
   ```

### File Upload Issues

If users encounter issues with file uploads:

1. Check Apache error logs for timeout or size limit errors:
   ```bash
   tail -f /var/log/httpd/linkyoh-error.log | grep -E "timeout|size|limit"
   ```

2. Verify the Apache configuration has been applied:
   ```bash
   apachectl -t -D DUMP_INCLUDES | grep -E "Timeout|LimitRequestBody|ProxyTimeout"
   ```

3. Check if the Django application is receiving the uploaded files:
   ```bash
   docker-compose -f docker-compose.app.yml logs web | grep -E "upload|file|size"
   ```

### Testing Static and Media File Serving

To test if your static and media files are being served correctly:

1. Check if static files are accessible:
   ```bash
   curl -I https://linkyoh.com/static/css/main.css
   ```
   You should see a `200 OK` response.

2. Check if media files are accessible:
   ```bash
   curl -I https://linkyoh.com/media/category_img/Auto/auto.jpg
   ```
   You should see a `200 OK` response.

3. Check the Apache access logs to see if requests for static and media files are being handled by Apache:
   ```bash
   tail -f /var/log/httpd/linkyoh-access.log | grep -E "static|media"
   ```

4. If you're using the NFS or rsync approach, verify that the files are correctly synchronized:
   ```bash
   # For NFS
   ls -la /mnt/linkyoh/static/
   ls -la /mnt/linkyoh/media/

   # For rsync
   ls -la /var/www/linkyoh/static/
   ls -la /var/www/linkyoh/media/
   ```
