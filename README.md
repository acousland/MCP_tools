# MCP Tools

A collection of FastMCP servers for various system operations, with Claude Desktop integration.

## Overview

This project provides two MCP (Model Context Protocol) servers:

1. **File Server**: Allows reading files from the local machine
2. **NMAP Server**: Executes NMAP commands and returns results

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install nmap (if not already installed):
```bash
# macOS
brew install nmap

# Ubuntu/Debian
sudo apt-get install nmap
```

## Usage

### Claude Desktop Integration (Recommended)

The easiest way to use these MCP servers is through Claude Desktop:

1. **Generate Claude Desktop configuration:**
```bash
python generate_claude_config.py
```

2. **Restart Claude Desktop**

3. **Start using the tools in Claude Desktop:**
   - "Read the contents of README.md"
   - "List files in the current directory" 
   - "Ping google.com"
   - "Scan ports 80 and 443 on localhost"

### Manual Server Management

#### Running Individual Servers

1. **File Server**:
```bash
python servers/file_server.py
```

2. **NMAP Server**:
```bash
python servers/nmap_server.py
```

#### Running All Servers

Use the main application to start all servers:
```bash
python main.py
```

## Servers

### File Server
- **Port**: 8001
- **Tools**: 
  - `read_file`: Read contents of a file
  - `list_directory`: List contents of a directory

### NMAP Server
- **Port**: 8002
- **Tools**:
  - `nmap_scan`: Execute NMAP scans with various options
  - `ping_host`: Simple ping functionality

## Security Notes

- The file server allows reading any file accessible to the user running the server
- The NMAP server executes system commands - use with caution
- Consider implementing authentication for production use

## Claude Desktop Configuration

The `generate_claude_config.py` script automatically configures Claude Desktop to use these MCP servers. The configuration is written to:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json` 
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Configuration Commands

```bash
# Preview what the configuration will look like
python preview_claude_config.py

# Generate configuration with confirmation prompt
python generate_claude_config.py

# Generate configuration automatically (no prompt)
python generate_claude_config.py --yes
```

The script will:
- ✅ Backup any existing configuration
- ✅ Merge with existing MCP servers 
- ✅ Use the project's virtual environment
- ✅ Set proper paths and environment variables

### Troubleshooting

If you encounter issues with Claude Desktop integration:

```bash
# Kill any conflicting processes
python troubleshoot.py kill

# Regenerate configuration
python generate_claude_config.py --yes

# Test servers in stdio mode (Claude Desktop mode)
python troubleshoot.py stdio

# Check configuration
python troubleshoot.py config

# Full troubleshooting check
python troubleshoot.py
```

**Common Issues:**
- **"Address already in use"**: Run `python troubleshoot.py kill` to stop conflicting processes
- **Servers not responding**: Ensure you've restarted Claude Desktop after configuration
- **Tools not available**: Check that configuration was written correctly with `python troubleshoot.py config`

## License

MIT License - see LICENSE file for details.
