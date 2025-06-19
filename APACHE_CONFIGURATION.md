# Apache Configuration for Linkyoh Docker Deployment

This document provides instructions for configuring Apache as a reverse proxy for the Linkyoh application deployed using Docker.

## Overview

When using the `docker-compose.app.yml` deployment option, the Linkyoh application is exposed on port 8000 without SSL termination. Apache can be configured as a reverse proxy to:

1. Handle SSL termination
2. Redirect HTTP to HTTPS
3. Forward requests to the Linkyoh application

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