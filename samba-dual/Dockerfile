FROM debian:bullseye-slim

# Install Samba and required tools
RUN apt-get update && \
    apt-get install -y \
    samba \
    samba-common-bin \
    iproute2 \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create scan directory
RUN mkdir -p /share/scan && chmod 777 /share/scan

# Copy startup script
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
