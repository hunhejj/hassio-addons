#!/usr/bin/env python3
import os
import logging
import smtplib
import smtpd
import asyncore
from email.parser import Parser

# Configuration defaults
defaults = {
    'SMTP_AUTH_REQUIRED': 'true',
    'SMTP_RELAY_HOST': 'smtp.gmail.com',
    'SMTP_RELAY_PORT': '587',
    'SMTP_RELAY_USER': '',
    'SMTP_RELAY_PASS': '',
    'SMTP_RELAY_STARTTLS': 'true',
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


class RelayServer(smtpd.SMTPServer):
    """SMTP Relay Server using smtpd"""
    
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        """Process and relay incoming messages"""
        try:
            logger.info(f"Received mail from {mailfrom} to {rcpttos} (peer: {peer})")
            
            # Check relay domains if configured
            if RELAY_DOMAINS:
                should_relay = False
                for recipient in rcpttos:
                    domain = recipient.split('@')[-1] if '@' in recipient else ''
                    if domain in RELAY_DOMAINS or not domain:
                        should_relay = True
                        break
                
                if not should_relay:
                    logger.warning(f"Rejecting mail - no recipients in allowed relay domains")
                    return '550 Relaying denied'
            
            # Relay the message
            if USE_TLS:
                smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=TIMEOUT)
                smtp.starttls()
            else:
                smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=TIMEOUT)
            
            try:
                if SMTP_AUTH_REQUIRED:
                    smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                
                # Send the message with original data
                smtp.sendmail(mailfrom, rcpttos, data)
                
                logger.info(f"Successfully relayed mail to {rcpttos}")
                
            finally:
                smtp.quit()
            
            return None  # Success
            
        except Exception as e:
            logger.error(f"Error relaying message: {e}", exc_info=True)
            return '451 Temporary failure, please try again later'


def main():
    logger.info(f"Starting SMTP Relay on port 25, forwarding to {SMTP_HOST}:{SMTP_PORT}")
    
    # Create the relay server
    server = RelayServer(('0.0.0.0', 25), None)
    
    logger.info("SMTP Relay server is running...")
    
    try:
        # Start the asyncore loop
        asyncore.loop()
    except KeyboardInterrupt:
        logger.info("SMTP Relay stopped")


if __name__ == '__main__':
    main()
