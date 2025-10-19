ARG BUILD_FROM
FROM $BUILD_FROM

# Install Samba and required packages
RUN apk add --no-cache \
    samba \
    samba-common-tools \
    supervisor \
    tzdata

# Create directories
RUN mkdir -p /var/log/supervisor \
    && mkdir -p /scan

# Copy configuration files
COPY rootfs /

# Make scripts executable
RUN chmod +x /etc/services.d/*/run \
    && chmod +x /usr/bin/start.sh

# Expose SMB ports
EXPOSE 137/udp 138/udp 139/tcp 445/tcp

CMD ["/usr/bin/start.sh"]