# MCP Tools - Server Overview

This document provides a comprehensive overview of all MCP servers included in this project.

## 🌟 Available Servers

### 📁 File Server (mcp-file-server)
**Script:** `servers/file_server.py`  
**Port:** 8001 (HTTP mode)  
**Description:** Provides secure file system operations for local machine access.

**Tools:**
- `read_file(file_path, start_line, end_line)` - Read content from files with optional line range
- `list_directory(directory_path, show_hidden, max_items)` - List directory contents with filtering
- `get_file_info(file_path)` - Get detailed file/directory information including size, permissions, timestamps

**Security Features:**
- Path validation and sandboxing
- File size limits (10MB for reading)
- Hidden file filtering
- Permission checks

---

### 🌐 NMAP Server (mcp-nmap-server)
**Script:** `servers/nmap_server.py`  
**Port:** 8002 (HTTP mode)  
**Description:** Network scanning and connectivity testing using NMAP.

**Tools:**
- `nmap_scan(target, scan_type, ports, options)` - Comprehensive NMAP scanning
- `ping_host(host, count, timeout)` - ICMP ping testing
- `port_scan(host, ports, timeout)` - Quick TCP port scanning
- `network_discovery(network, scan_type)` - Network host discovery

**Scan Types:**
- TCP SYN scan (-sS)
- TCP connect scan (-sT) 
- UDP scan (-sU)
- Version detection (-sV)
- OS detection (-O)

---

### 🔐 SSH Server (mcp-ssh-server)
**Script:** `servers/ssh_server.py`  
**Port:** 8003 (HTTP mode)  
**Description:** SSH remote command execution and file transfer operations.

**Tools:**
- `ssh_execute(host, command, username, password, port, timeout)` - Execute commands on remote hosts
- `ssh_copy_file(source_file, dest_file, host, username, password, direction, port)` - SCP file transfer
- `ssh_tunnel(local_port, remote_host, remote_port, ssh_host, username, password)` - SSH port forwarding info
- `ssh_key_info(key_path, key_type)` - SSH key analysis and information

**Security Features:**
- Command validation and dangerous command blocking
- Secure credential handling
- Timeout controls
- Connection status monitoring

---

### 📂 FTP Server (mcp-ftp-server)
**Script:** `servers/ftp_server.py`  
**Port:** 8004 (HTTP mode)  
**Description:** FTP file transfer and server operations.

**Tools:**
- `ftp_list_files(host, directory, username, password, port, timeout)` - List FTP directory contents
- `ftp_download_file(host, remote_file, local_file, username, password, port, timeout)` - Download files
- `ftp_upload_file(host, local_file, remote_file, username, password, port, timeout)` - Upload files
- `ftp_server_info(host, port, timeout)` - Get FTP server information and capabilities

**Features:**
- Active and passive mode support
- Binary and ASCII transfer modes
- Progress monitoring
- Error handling and recovery

---

### 📡 Telnet Server (mcp-telnet-server)
**Script:** `servers/telnet_server.py`  
**Port:** 8005 (HTTP mode)  
**Description:** Telnet connectivity testing and basic operations (socket-based implementation for Python 3.13+ compatibility).

**Tools:**
- `telnet_connect(host, port, timeout, read_timeout)` - Test Telnet connections
- `telnet_execute(host, command, port, timeout)` - Manual execution guidance (security-focused)
- `telnet_port_check(host, port, timeout)` - Port accessibility testing
- `telnet_banner_grab(host, port, timeout, wait_time)` - Service banner retrieval
- `telnet_interactive_session(host, port, timeout)` - Interactive session setup instructions

**Security Notes:**
- Telnet is inherently insecure (plain text)
- Use only on trusted networks
- Prefer SSH when possible
- Command execution is guided rather than automated

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
brew install nmap  # macOS
```

### 2. Run All Servers
```bash
# Interactive mode with menu
python main.py

# Start all servers and keep running
python main.py start
```

### 3. Configure Claude Desktop
```bash
# Generate Claude Desktop configuration
python generate_claude_config.py --yes
```

### 4. Test Individual Servers
```bash
# Test in HTTP mode (for debugging)
python servers/file_server.py --http
python servers/nmap_server.py --http
python servers/ssh_server.py --http
python servers/ftp_server.py --http
python servers/telnet_server.py --http
```

## 🔧 Configuration

### Claude Desktop Integration
The servers are designed to work with Claude Desktop using the MCP protocol. The configuration file will be automatically placed at:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

### Server Modes
All servers support two modes:

1. **stdio mode** (default): For Claude Desktop integration
2. **HTTP mode** (`--http` flag): For testing and development

## 🛡️ Security Considerations

### General Security
- All servers include input validation and sanitization
- Dangerous operations are blocked or require confirmation
- File path traversal protection is implemented
- Connection timeouts prevent hanging operations

### Network Security
- SSH server uses secure authentication methods
- FTP operations include connection encryption where supported
- Telnet server provides security warnings and guidance
- All network operations respect timeout limits

### File System Security
- File server operations are sandboxed to prevent unauthorized access
- Path validation prevents directory traversal attacks
- File size limits prevent resource exhaustion
- Permission checks ensure appropriate access levels

## 🐛 Troubleshooting

### Common Issues
1. **Import Errors:** Ensure virtual environment is activated and dependencies installed
2. **Permission Errors:** Check file/directory permissions for file operations
3. **Network Timeouts:** Adjust timeout parameters for slow networks
4. **Claude Desktop Integration:** Restart Claude Desktop after configuration changes

### Debug Mode
Run servers with `--http` flag to test functionality independently:
```bash
python servers/file_server.py --http
# Then test at http://localhost:8001
```

### Logs and Monitoring
- Check server console output for error messages
- Use troubleshoot.py for comprehensive system checking
- Monitor resource usage during large operations

## 📝 Usage Examples

### File Operations
- "Read the content of README.md"
- "List all files in the current directory"
- "Show information about the data folder"

### Network Scanning
- "Ping google.com to test connectivity"
- "Scan ports 80,443,22 on example.com"
- "Discover hosts on the 192.168.1.0/24 network"

### SSH Operations
- "Execute 'ls -la' on server 192.168.1.100 using SSH"
- "Copy file.txt to remote server via SSH"
- "Show information about my SSH key"

### FTP Operations
- "List files in the /public directory on FTP server"
- "Download backup.zip from the FTP server"
- "Upload document.pdf to the FTP server"

### Telnet Testing
- "Test if port 23 is open on the server"
- "Grab the banner from port 80 on example.com"
- "Check Telnet connectivity to the router"

## 🤝 Contributing

When adding new servers:
1. Follow the existing server pattern and structure
2. Include proper error handling and validation
3. Add security considerations and input sanitization
4. Update configuration files and documentation
5. Test both stdio and HTTP modes

---

*This project provides a comprehensive set of MCP tools for file operations, network scanning, and remote connectivity testing through Claude Desktop integration.*
