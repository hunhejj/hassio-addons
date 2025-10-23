#!/usr/bin/env bashio

bashio::log.info "Configuring SMTP relay..."

# Get configuration from Home Assistant
RELAY_HOST="$(bashio::config 'smtp_relay_host')"
RELAY_PORT="$(bashio::config 'smtp_relay_port')"
RELAY_USER="$(bashio::config 'smtp_relay_user')"  
RELAY_PASS="$(bashio::config 'smtp_relay_pass')"
USE_STARTTLS="$(bashio::config 'smtp_relay_starttls')"

# Create ssmtp configuration
cat > /etc/ssmtp/ssmtp.conf << EOF
root=${RELAY_USER}
mailhub=${RELAY_HOST}:${RELAY_PORT}
hostname=homeassistant
AuthUser=${RELAY_USER}
AuthPass=${RELAY_PASS}
UseSTARTTLS=${USE_STARTTLS}
UseTLS=${USE_STARTTLS}
rewriteDomain=${RELAY_HOST}
FromLineOverride=YES
EOF

# Create revaliases for local delivery
echo "root:${RELAY_USER}:${RELAY_HOST}:${RELAY_PORT}" > /etc/ssmtp/revaliases

bashio::log.info "Starting SMTP relay server..."

# Start ssmtp as SMTP server (simple approach - use socat to listen on port 25)
socat TCP-LISTEN:25,fork EXEC:"/usr/sbin/ssmtp -t"
