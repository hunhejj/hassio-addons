ARG BUILD_FROM
FROM $BUILD_FROM

# Install Samba and required tools
RUN apk add --no-cache \
    samba \
    samba-common-tools \
    iproute2 \
    procps

# Create scan directory
RUN mkdir -p /share/scan \
    && chmod 777 /share/scan

WORKDIR /app

# Copy startup script
COPY run.sh /app/run.sh
RUN chmod 755 /app/run.sh

ENTRYPOINT ["/app/run.sh"]

LABEL \
  io.hass.version="VERSION" \
  io.hass.type="addon" \
  io.hass.arch="armhf|armv7|aarch64|i386|amd64"
