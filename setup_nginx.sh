#!/bin/bash
set -euo pipefail
error_handler() {
    echo "Error on line ${BASH_LINENO[0]}: ${BASH_COMMAND}"
}
trap 'error_handler' ERR

# Get the domain name
if [[ -n "$1" ]]; then
    FULL_DOMAIN_NAME="$1"
else
    read -p "Enter the full domain name (e.g., api.example.com): " FULL_DOMAIN_NAME
fi
DOMAIN_NAME="$(echo "$FULL_DOMAIN_NAME" | awk -F. '{print $(NF-1)"."$NF}')"

# Install https certificates
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx
sudo certbot --nginx -d $FULL_DOMAIN_NAME --non-interactive --agree-tos -m admin@$DOMAIN_NAME

# Setup nginx.conf
IP_ADDRESS=localhost
sudo tee /etc/nginx/nginx.conf >/dev/null <<EOF
user www-data;
worker_processes auto;
pid /run/nginx.pid;
error_log /var/log/nginx/error.log;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 1000;
}

http {
    client_max_body_size 100M;

    upstream backend {
        server $IP_ADDRESS:8080;
        keepalive 256;
    }

    # Server block
    server {
        server_name $FULL_DOMAIN_NAME;

        location / {
            proxy_pass http://backend;

            proxy_http_version 1.1;
            proxy_set_header Connection "";

            proxy_connect_timeout 30s;
            proxy_send_timeout 600s;
            proxy_read_timeout 600s;

            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-Host \$host;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Original-URI \$request_uri;
        }

        # SSL settings (Certbot)
        listen [::]:443 ssl ipv6only=on default_server; # managed by Certbot
        listen 443 ssl default_server; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/$FULL_DOMAIN_NAME/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/$FULL_DOMAIN_NAME/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    }

    # HTTP -> HTTPS redirect
    server {
        if (\$host = $FULL_DOMAIN_NAME) {
            return 301 https://\$host\$request_uri;
        }
        listen 80 default_server;
        listen [::]:80 default_server;
        server_name $FULL_DOMAIN_NAME;
        return 404;
    }
}
EOF

# Reload nginx
sudo nginx -t
sudo nginx -s reload
