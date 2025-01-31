#!/usr/bin/env bash
#
# init-letsencrypt.sh
#
# 1) Creates a temporary (dummy) certificate so Nginx can start
# 2) Launches Nginx
# 3) Removes the dummy certificate
# 4) Requests a real certificate from Let's Encrypt
# 5) Reloads Nginx
#
# Run this script only once for new domains or when you need to recreate
# certificates from scratch.

set -e  # Exit immediately if a command exits with a non-zero status

#####################
#  CONFIG VARIABLES
#####################
DOMAINS=("linkyoh.com" "www.linkyoh.com")
RSA_KEY_SIZE=4096
DATA_PATH="./nginx/certbot"
EMAIL="dev@silvatech.bz"     # Your email address (recommended)
STAGING=0                     # Set to 1 if you're testing certs to avoid rate limits

#####################
#   MAIN SCRIPT
#####################
# Check if there's an existing cert for the primary domain
PRIMARY_DOMAIN="${DOMAINS[0]}"
LIVE_PATH="${DATA_PATH}/conf/live/${PRIMARY_DOMAIN}"

if [ -d "${LIVE_PATH}" ]; then
  echo "Certificates for ${PRIMARY_DOMAIN} already exist at '${LIVE_PATH}'."
  echo "Delete that folder or rename it if you want to recreate certificates."
  exit 0
fi

echo "### Ensuring necessary folders exist..."
mkdir -p "${DATA_PATH}/conf"
mkdir -p "${DATA_PATH}/www"

echo "### Downloading recommended TLS parameters (if not present)..."
if [ ! -e "${DATA_PATH}/conf/options-ssl-nginx.conf" ] || [ ! -e "${DATA_PATH}/conf/ssl-dhparams.pem" ]; then
  echo "Downloading options-ssl-nginx.conf and ssl-dhparams.pem..."
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/options-ssl-nginx.conf \
    -o "${DATA_PATH}/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/ssl-dhparams.pem \
    -o "${DATA_PATH}/conf/ssl-dhparams.pem"
fi

echo "### Creating dummy certificate for ${DOMAINS[*]} ..."
DUMMY_PATH="/etc/letsencrypt/live/${PRIMARY_DOMAIN}"
mkdir -p "${DATA_PATH}/conf/live/${PRIMARY_DOMAIN}"
docker-compose run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout '${DUMMY_PATH}/privkey.pem' \
    -out '${DUMMY_PATH}/fullchain.pem' \
    -subj '/CN=localhost'" certbot

echo "### Starting nginx ..."
docker-compose up --force-recreate -d nginx

echo "### Deleting dummy certificate for ${DOMAINS[*]} ..."
docker-compose run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/${PRIMARY_DOMAIN} && \
  rm -Rf /etc/letsencrypt/archive/${PRIMARY_DOMAIN} && \
  rm -Rf /etc/letsencrypt/renewal/${PRIMARY_DOMAIN}.conf" certbot

echo "### Requesting Let's Encrypt certificate for ${DOMAINS[*]} ..."
DOMAIN_ARGS=""
for DOMAIN in "${DOMAINS[@]}"; do
  DOMAIN_ARGS="${DOMAIN_ARGS} -d ${DOMAIN}"
done

# Email arg
case "${EMAIL}" in
  "") EMAIL_ARG="--register-unsafely-without-email" ;;
  *) EMAIL_ARG="--email ${EMAIL}" ;;
esac

# Staging arg
if [ $STAGING -ne 0 ]; then
  echo "### Using the staging environment (for testing)..."
  STAGING_ARG="--staging"
else
  STAGING_ARG=""
fi

docker-compose run --rm --entrypoint "\
  certbot certonly --webroot \
    -w /var/www/certbot \
    ${STAGING_ARG} \
    ${EMAIL_ARG} \
    ${DOMAIN_ARGS} \
    --rsa-key-size ${RSA_KEY_SIZE} \
    --agree-tos \
    --force-renewal" certbot

echo "### Reloading nginx ..."
docker-compose exec nginx nginx -s reload

echo
echo "######################################################################"
echo "Creation of certificate(s) for ${DOMAINS[*]} is complete!"
echo "######################################################################"
