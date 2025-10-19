# Dual Samba Server Add-on

This add-on runs two Samba servers simultaneously:
1. **Legacy SMB1** server for old Canon printers that can only scan to legacy SMB
2. **Modern SMB2/3** server for Windows 11 laptops to access the scans

## Installation

1. Copy the entire `samba_dual` folder to `/addons/` on your Home Assistant OS
2. Reload add-ons in the Supervisor
3. Install "Dual Samba Server"
4. Create a folder `/share/scan` in Home Assistant (or map an existing folder)
5. Start the add-on

## Configuration

The add-on comes with sensible defaults:

```yaml
workgroup: "WORKGROUP"
legacy_ip: "192.168.0.254"
username: "scanner"
password: "CHANGEME!"
```

**Important:** Change the `legacy_ip` to an unused IP in your network if needed.

## Usage

### Canon Printer Setup
Configure your Canon printer to scan to:
- **Server:** `\\192.168.0.254\Scan` (or your configured legacy_ip)
- **Authentication:** Guest/Anonymous (no password needed)
- **Protocol:** SMB1/CIFS

### Windows 11 Access
Access scans from Windows:
- **Path:** `\\homeassistant\Scan` or `\\<your-ha-ip>\Scan`
- **Username:** `scanner` (or your configured username)
- **Password:** `CHANGEME!` (or your configured password)

## How It Works

The add-on creates a virtual IP address for the legacy SMB1 server that your Canon printer connects to. The modern SMB2/3 server runs on the main Home Assistant IP for your Windows laptops. Both servers share the same `/share/scan` directory.

## Storage

The add-on maps to `/share/scan` by default. You can access this folder:
- Via the modern Samba share from Windows
- Via File Editor add-on (if installed)
- Via SSH/Terminal

## Troubleshooting

Check the add-on logs if something isn't working. Common issues:
- **IP conflict:** Change `legacy_ip` to an unused IP in your network
- **Canon can't connect:** Ensure your Canon is on the same network and SMB1 is enabled on the printer
- **Windows can't connect:** Check firewall settings and ensure SMB2/3 is enabled on Windows 11
