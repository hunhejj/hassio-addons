#!/usr/bin/with-contenv bashio

# Get configuration
WORKGROUP=$(bashio::config 'workgroup')
LEGACY_IP=$(bashio::config 'legacy_ip')
USERNAME=$(bashio::config 'username')
PASSWORD=$(bashio::config 'password')

bashio::log.info "Starting Dual Samba Server..."
bashio::log.info "Legacy IP for Canon: ${LEGACY_IP}"

# Create user for modern SMB
adduser -D -H -s /bin/false "${USERNAME}" 2>/dev/null || true
echo -e "${PASSWORD}\n${PASSWORD}" | smbpasswd -a -s "${USERNAME}"
smbpasswd -e "${USERNAME}"

# Configure legacy SMB (SMB1 for Canon)
cat > /etc/samba/smb-legacy.conf << EOF
[global]
   workgroup = ${WORKGROUP}
   server string = Canon Scanner Legacy
   security = user
   map to guest = Bad User
   guest account = nobody
   
   # Force SMB1 for old Canon printers
   server min protocol = NT1
   client min protocol = NT1
   server max protocol = NT1
   
   # Network settings for legacy
   interfaces = ${LEGACY_IP}/24
   bind interfaces only = no
   
   log level = 1
   load printers = no
   printing = bsd
   printcap name = /dev/null
   disable spoolss = yes

[Scan]
   path = /share/scan
   browseable = yes
   read only = no
   guest ok = yes
   create mask = 0666
   directory mask = 0777
   force user = root
EOF

# Configure modern SMB (SMB2+ for Windows 11)
cat > /etc/samba/smb.conf << EOF
[global]
   workgroup = ${WORKGROUP}
   server string = Scan Server
   security = user
   
   # Modern SMB2/3 only
   server min protocol = SMB2
   client min protocol = SMB2
   
   log level = 1
   load printers = no
   printing = bsd
   printcap name = /dev/null
   disable spoolss = yes

[Scan]
   path = /share/scan
   browseable = yes
   read only = no
   valid users = ${USERNAME}
   create mask = 0666
   directory mask = 0777
   force user = root
EOF

# Add virtual IP for legacy Samba
bashio::log.info "Adding virtual IP ${LEGACY_IP} for legacy SMB..."
ip addr add ${LEGACY_IP}/24 dev eth0 2>/dev/null || bashio::log.warning "Could not add IP (may already exist)"

# Start legacy Samba (SMB1) on the virtual IP
bashio::log.info "Starting legacy Samba (SMB1) for Canon..."
smbd -D --configfile=/etc/samba/smb-legacy.conf
nmbd -D --configfile=/etc/samba/smb-legacy.conf

# Give legacy instance time to start
sleep 2

# Start modern Samba (SMB2/3) on main interface
bashio::log.info "Starting modern Samba (SMB2/3) for Windows..."
smbd -F --configfile=/etc/samba/smb.conf --no-process-group &
SMBD_PID=$!

nmbd -F --configfile=/etc/samba/smb.conf --no-process-group &
NMBD_PID=$!

bashio::log.info "Both Samba servers started successfully!"
bashio::log.info "Canon scans to: \\\\${LEGACY_IP}\\Scan (SMB1, guest access)"
bashio::log.info "Windows access: \\\\<homeassistant>\\Scan (SMB2/3, user: ${USERNAME})"

# Wait for processes
wait $SMBD_PID $NMBD_PID
