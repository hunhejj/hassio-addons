#!/usr/bin/env python3
import os
import logging
import smtplib
import socketserver
import threading
from email.parser import Parser

# Configuration defaults
defaults = {
    'SMTP_AUTH_REQUIRED': 'False',
    'SMTP_RELAY_HOST': None,
    'SMTP_RELAY_PORT': '25',
    'SMTP_RELAY_USER': None,
    'SMTP_RELAY_PASS': None,
    'SMTP_RELAY_STARTTLS': None,
    'SMTP_RELAY_TIMEOUT_SECS': '30',
    'DEBUG': 'false'
}

# Load configuration from environment variables
config = {
    setting: os.environ.get(setting, default) for setting, default in defaults.items()
}

# Convert strings to booleans
for key, value in config.items():
    if value and value.lower() == "true":
        config[key] = True
    elif value and value.lower() == "false":
        config[key] = False

# Convert port and timeout to integers
config['SMTP_RELAY_PORT'] = int(config['SMTP_RELAY_PORT'])
config['SMTP_RELAY_TIMEOUT_SECS'] = int(config['SMTP_RELAY_TIMEOUT_SECS'])

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if config['DEBUG'] else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SMTP_HOST = config['SMTP_RELAY_HOST']
SMTP_PORT = config['SMTP_RELAY_PORT']
SMTP_USERNAME = config['SMTP_RELAY_USER']
SMTP_PASSWORD = config['SMTP_RELAY_PASS']
USE_TLS = config['SMTP_RELAY_STARTTLS']
SMTP_AUTH_REQUIRED = config['SMTP_AUTH_REQUIRED']
TIMEOUT = config['SMTP_RELAY_TIMEOUT_SECS']


class SMTPHandler(socketserver.BaseRequestHandler):
    """Handle SMTP connections"""

    def handle(self):
        """Handle incoming SMTP connection"""
        try:
            logger.info(f"Connection from {self.client_address}")

            # Send greeting
            self.send_response("220 SMTP Relay Ready")

            mail_from = None
            rcpt_to = []
            data = ""
            in_data = False

            buffer = ""
            while True:
                try:
                    chunk = self.request.recv(1024).decode('utf-8')
                    if not chunk:
                        break

                    buffer += chunk

                    # Process complete lines
                    while '\r\n' in buffer:
                        line, buffer = buffer.split('\r\n', 1)

                        logger.debug(f"Received: {line}")

                        if not in_data:
                            if line.upper().startswith("EHLO") or line.upper().startswith("HELO"):
                                self.send_response("250 Hello")
                            elif line.upper().startswith("MAIL FROM:"):
                                mail_from = line[10:].strip().strip('<>')
                                self.send_response("250 OK")
                            elif line.upper().startswith("RCPT TO:"):
                                rcpt_to.append(line[8:].strip().strip('<>'))
                                self.send_response("250 OK")
                            elif line.upper() == "DATA":
                                self.send_response("354 Start mail input; end with <CRLF>.<CRLF>")
                                in_data = True
                                data = ""
                            elif line.upper() == "QUIT":
                                self.send_response("221 Bye")
                                return
                            else:
                                self.send_response("250 OK")
                        else:
                            # In DATA mode
                            if line == ".":
                                # End of data, relay the message
                                logger.info("End of message received, relaying...")
                                self.relay_message(mail_from, rcpt_to, data)
                                self.send_response("250 OK Message accepted")
                                in_data = False
                                data = ""
                                mail_from = None
                                rcpt_to = []
                            else:
                                # Handle dot stuffing (RFC 5321)
                                if line.startswith("."):
                                    line = line[1:]
                                data += line + "\r\n"

                except Exception as e:
                    logger.error(f"Error handling command: {e}")
                    self.send_response("451 Temporary failure")

        except Exception as e:
            logger.error(f"Connection error: {e}")

    def send_response(self, response):
        """Send response to client"""
        self.request.send(f"{response}\r\n".encode('utf-8'))

    def relay_message(self, mail_from, rcpt_to, data):
        """Relay the message through external SMTP"""
        try:
            logger.info(f"Relaying message from {mail_from} to {rcpt_to}")

            # Connect to relay server
            if USE_TLS:
                smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=TIMEOUT)
                smtp.starttls()
            else:
                smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=TIMEOUT)

            try:
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)

                # Send the message
                smtp.sendmail(mail_from, rcpt_to, data)
                logger.info(f"Successfully relayed to {rcpt_to}")

            finally:
                smtp.quit()

        except Exception as e:
            logger.error(f"Error relaying message: {e}", exc_info=True)
            raise


def main():
    logger.info(f"Starting SMTP Relay on port 25, forwarding to {SMTP_HOST}:{SMTP_PORT}")

    # Create the server
    server = socketserver.ThreadingTCPServer(('0.0.0.0', 25), SMTPHandler)

    logger.info("SMTP Relay server is running...")

    try:
        # Start the server
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("SMTP Relay stopped")
        server.shutdown()


if __name__ == '__main__':
    main()
