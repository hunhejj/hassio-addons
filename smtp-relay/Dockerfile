ARG BUILD_FROM
FROM $BUILD_FROM

WORKDIR /app

COPY start.sh /app/

RUN chmod 755 /app/start.sh

RUN apk add --no-cache ssmtp socat

ENTRYPOINT ["/app/start.sh"]

LABEL \
  io.hass.version="VERSION" \
  io.hass.type="addon" \
  io.hass.arch="armhf|armv7|aarch64|i386|amd64"
