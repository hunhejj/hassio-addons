#!/usr/bin/with-contenv bashio

# ==============================================================================
# Home Assistant Community Add-on: Scanner SMB Share
# ==============================================================================

# Get configuration options
WORKGROUP=$(bashio::config 'workgroup')
SCANNER_USERNAME=$(bashio::config 'scanner_username')
SCANNER_PASSWORD=$(bashio::config 'scanner_password')
LEGACY_IP=$(bashio::config 'legacy_ip')

bashio::log.info "Starting Scanner SMB Share..."
bashio::log.info "Workgroup: ${WORKGROUP}"
bashio::log.info "Scanner username: ${SCANNER_USERNAME}"
bashio::log.info "Legacy IP: ${LEGACY_IP}"

# Create scan directory if it doesn't exist
mkdir -p /scan
chmod 777 /scan

# Replace placeholders in Samba configuration files
sed -i "s/%%WORKGROUP%%/${WORKGROUP}/g" /etc/samba/smb-legacy.conf
sed -i "s/%%LEGACY_IP%%/${LEGACY_IP}/g" /etc/samba/smb-legacy.conf

sed -i "s/%%WORKGROUP%%/${WORKGROUP}/g" /etc/samba/smb-modern.conf
sed -i "s/%%SCANNER_USERNAME%%/${SCANNER_USERNAME}/g" /etc/samba/smb-modern.conf

# Create Samba user for modern SMB
echo -e "${SCANNER_PASSWORD}\n${SCANNER_PASSWORD}" | smbpasswd -a -s ${SCANNER_USERNAME}
smbpasswd -e ${SCANNER_USERNAME}

# Create log directories
mkdir -p /var/log/samba
mkdir -p /var/log/supervisor

# Initialize Samba databases
mkdir -p /var/lib/samba/private
mkdir -p /var/cache/samba
mkdir -p /var/run/samba

# Set up network interface for legacy SMB
if ! ip addr show | grep -q "${LEGACY_IP}"; then
    bashio::log.info "Adding legacy IP ${LEGACY_IP} to interface"
    ip addr add ${LEGACY_IP}/24 dev eth0 2>/dev/null || bashio::log.warning "Could not add IP ${LEGACY_IP}"
fi

bashio::log.info "Starting Samba services..."

# Start supervisor to manage multiple Samba instances
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf