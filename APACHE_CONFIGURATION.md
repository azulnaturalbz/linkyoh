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

You need to make the static and media files accessible to the Apache server. Options include:

- **NFS Mount**: Mount the static and media directories from the Django server to the Apache server
  ```bash
  # On the Django server
  apt-get install nfs-kernel-server
  echo "/srv/static/linkyoh *(ro,sync,no_subtree_check)" >> /etc/exports
  echo "/srv/static/linkyoh/media *(rw,sync,no_subtree_check)" >> /etc/exports
  exportfs -a

  # On the Apache server
  apt-get install nfs-common
  mkdir -p /mnt/linkyoh/static /mnt/linkyoh/media
  mount 192.168.1.156:/srv/static/linkyoh /mnt/linkyoh/static
  mount 192.168.1.156:/srv/static/linkyoh/media /mnt/linkyoh/media
  ```

- **rsync**: Periodically sync files from the Django server to the Apache server
  ```bash
  # Create a script on the Apache server
  cat > /usr/local/bin/sync-linkyoh-assets.sh << 'EOF'
  #!/bin/bash
  rsync -avz --delete 192.168.1.156:/srv/static/linkyoh/ /var/www/linkyoh/static/
  rsync -avz --delete 192.168.1.156:/srv/static/linkyoh/media/ /var/www/linkyoh/media/
  EOF
  chmod +x /usr/local/bin/sync-linkyoh-assets.sh

  # Add to crontab to run every 5 minutes
  (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/sync-linkyoh-assets.sh") | crontab -
  ```

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
    Alias /static/ /mnt/linkyoh/static/
    Alias /media/ /mnt/linkyoh/media/

    <Directory /mnt/linkyoh/static>
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
    Alias /static/ /mnt/linkyoh/static/
    Alias /media/ /mnt/linkyoh/media/

    <Directory /mnt/linkyoh/static>
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
