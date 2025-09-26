#!/usr/bin/env bash
set -euo pipefail

# Change to script directory
cd "$(dirname "$0")"

echo "[$(date)] >> Starting SSL certificate renewal..."

# Run certbot renewal with proper profile
echo "[$(date)] >> Running certbot renew..."
if docker compose --profile renew run --rm certbot-renew; then
    echo "[$(date)] >> Certbot renewal completed successfully"
else
    echo "[$(date)] >> Certbot renewal failed or no renewal needed"
    # Don't exit here - certbot returns non-zero if no renewal is needed
fi

# Test nginx configuration before reloading
echo "[$(date)] >> Testing nginx configuration..."
if docker compose exec nginx nginx -t; then
    echo "[$(date)] >> Nginx configuration is valid"
    
    # Reload nginx
    echo "[$(date)] >> Reloading nginx..."
    if docker compose exec nginx nginx -s reload; then
        echo "[$(date)] >> Nginx reloaded successfully"
    else
        echo "[$(date)] >> ERROR: Failed to reload nginx"
        exit 1
    fi
else
    echo "[$(date)] >> ERROR: Nginx configuration test failed"
    exit 1
fi

echo "[$(date)] >> SSL renewal cycle complete."
