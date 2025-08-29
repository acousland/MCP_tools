# Project Structure

/Users/acousland/Documents/Code/MCP_tools/
├── LICENSE                    # MIT License
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── config.json               # Server configuration
├── main.py                   # Main application to run all servers
├── setup.sh                  # Setup script for installation
├── test_servers.py           # Test script for server functionality
├── examples.py               # Usage examples
├── .venv/                    # Python virtual environment
└── servers/                  # MCP servers directory
    ├── __init__.py           # Package init file
    ├── file_server.py        # File operations server (port 8001)
    └── nmap_server.py        # Network scanning server (port 8002)

## Servers

### File Server (port 8001)
- `read_file(file_path, encoding="utf-8")` - Read file contents
- `list_directory(dir_path, show_hidden=False)` - List directory contents  
- `get_file_info(file_path)` - Get file/directory information

### NMAP Server (port 8002)
- `nmap_scan(target, scan_type="basic", ports="", options="")` - NMAP scanning
- `ping_host(host, count=4, timeout=5)` - Ping connectivity test
- `port_scan(host, ports="1-1000", scan_type="tcp")` - Port scanning
- `network_discovery(network="192.168.1.0/24")` - Network host discovery

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Install nmap: `brew install nmap` (macOS)  
3. Run all servers: `python main.py`
4. Test functionality: `python test_servers.py`
5. See examples: `python examples.py`

## API Usage

Servers provide REST APIs:
- GET `/health` - Health check
- GET `/tools` - List available tools
- POST `/call` - Call a tool with JSON payload:
  ```json
  {
    "tool": "tool_name",
    "arguments": {
      "param1": "value1"
    }
  }
  ```
