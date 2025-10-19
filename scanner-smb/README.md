# Scanner SMB Share Add-on

This Home Assistant add-on provides dual SMB shares for legacy Canon scanners and modern Windows access.

## Features

- **Legacy SMB**: Compatible with older Canon scanners that require legacy SMB1/CIFS protocols
- **Modern SMB**: Secure SMB3 share with authentication for Windows 11 access
- **Dual Network Setup**: Legacy SMB runs on a separate IP address to avoid conflicts

## Configuration

```yaml
workgroup: WORKGROUP
scanner_username: scanner
scanner_password: CHANGEME!
legacy_ip: 192.168.0.254
```

### Options

- `workgroup`: Windows workgroup name (default: WORKGROUP)
- `scanner_username`: Username for modern SMB authentication
- `scanner_password`: Password for modern SMB authentication  
- `legacy_ip`: IP address for legacy SMB service (must be available on your network)

## Usage

1. Configure your Canon scanner to scan to SMB share at `\\192.168.0.254\Scan` (no authentication required)
2. Access scanned files from Windows 11 using `\\your-homeassistant-ip\Scan` with the configured username/password
3. Files are stored in `/share/scan` directory on your Home Assistant system

## Network Requirements

- The `legacy_ip` must be an available IP address on your local network
- Ports 137-139, 445 need to be accessible
- Add-on uses `host_network` mode for proper SMB discovery

## Troubleshooting

- Ensure the legacy IP doesn't conflict with other devices
- Check that your router allows the IP range specified
- For Windows 11, you may need to enable SMB1 client in Windows Features if the legacy scanner doesn't work initially