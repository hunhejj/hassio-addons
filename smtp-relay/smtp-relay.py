#!/usr/bin/env python3
import os
import logging
from smtpproxy import SMTPProxy

# Configuration defaults
defaults = {
    'SMTP_AUTH_REQUIRED': 'False',
    'SMTP_RELAY_HOST': None,
    'SMTP_RELAY_PORT': None,
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
if config['SMTP_RELAY_PORT']:
    config['SMTP_RELAY_PORT'] = int(config['SMTP_RELAY_PORT'])

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if config['DEBUG'] else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info(f"Starting SMTP Relay on port 25, forwarding to {config['SMTP_RELAY_HOST']}:{config['SMTP_RELAY_PORT']}")
    
    # Create SMTP proxy
    proxy = SMTPProxy(
        listen_host='0.0.0.0',
        listen_port=25,
        remote_host=config['SMTP_RELAY_HOST'],
        remote_port=config['SMTP_RELAY_PORT'],
        username=config['SMTP_RELAY_USER'] if config['SMTP_AUTH_REQUIRED'] else None,
        password=config['SMTP_RELAY_PASS'] if config['SMTP_AUTH_REQUIRED'] else None,
        use_tls=config['SMTP_RELAY_STARTTLS']
    )
    
    logger.info("SMTP Relay server is running...")
    
    try:
        proxy.run()
    except KeyboardInterrupt:
        logger.info("SMTP Relay stopped")
        proxy.stop()

if __name__ == '__main__':
    main()