#!/usr/bin/env bash

# This script idempotently sets up a cron job for SSL certificate renewal.
# It must be run with sudo.

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root. Please use 'sudo ./setup-cron.sh'" >&2
  exit 1
fi

PROJECT_PATH="/opt/app"
SCRIPT_PATH="$PROJECT_PATH/ssl-renew.sh"
LOG_PATH="$PROJECT_PATH/logs/ssl-renew.log"

echo "Setting up SSL renewal cron job..."

# Ensure the logs directory exists
mkdir -p "$PROJECT_PATH/logs"
touch "$LOG_PATH"

# Define the cron job entry
CRON_CMD="$SCRIPT_PATH"
CRON_ENTRY="0 2,14 * * * cd $PROJECT_PATH && $CRON_CMD >> $LOG_PATH 2>&1"

# Check if the cron job already exists to prevent duplicates
if (crontab -l 2>/dev/null | grep -Fq "$CRON_CMD"); then
  echo "Cron job already exists:"
else
  echo "Installing cron job:"
  # Add the new cron job
  (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
fi

# Display the current cron jobs for verification
crontab -l

echo ""
echo "To remove this cron job later, run:"
echo "  sudo crontab -l | grep -v '$CRON_CMD' | sudo crontab -"