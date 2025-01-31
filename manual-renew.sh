#!/usr/bin/env bash
#
# manual-renew.sh
#
# Force renew the existing certificate(s) and reload Nginx

docker-compose run --rm certbot renew --force-renewal --webroot -w /var/www/certbot
docker-compose exec nginx nginx -s reload

echo "Certificates have been renewed and Nginx reloaded."
