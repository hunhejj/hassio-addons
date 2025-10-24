ARG BUILD_FROM
FROM $BUILD_FROM

WORKDIR /app

COPY start.sh smtp-relay.py /app/

RUN chmod 755 /app/start.sh
RUN chmod 755 /app/smtp-relay.py

RUN apk add --no-cache python3 py3-pip 

ENTRYPOINT ["/app/start.sh"]

LABEL \
  io.hass.version="VERSION" \
  io.hass.type="addon" \
  io.hass.arch="armhf|armv7|aarch64|i386|amd64"
