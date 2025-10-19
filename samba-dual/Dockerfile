ARG BUILD_FROM
FROM $BUILD_FROM

# Install Samba and required tools
RUN apk add --no-cache \
    samba \
    samba-common-tools \
    iproute2 \
    procps

# Create scan directory
RUN mkdir -p /share/scan && chmod 777 /share/scan

# Copy startup script
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
