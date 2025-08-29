# MCP Tools - FastMCP Server Collection

🎉 **Setup Complete!** Your FastMCP server collection is ready to use.

## ✅ What's Been Created

### 1. **File Server** (`servers/file_server.py`)
- **Port:** 8001  
- **Endpoint:** `http://127.0.0.1:8001/mcp`
- **Tools:**
  - `read_file(file_path, encoding="utf-8")` - Read file contents
  - `list_directory(dir_path, show_hidden=False)` - List directory contents
  - `get_file_info(file_path)` - Get file/directory information

### 2. **NMAP Server** (`servers/nmap_server.py`) 
- **Port:** 8002
- **Endpoint:** `http://127.0.0.1:8002/mcp`  
- **Tools:**
  - `nmap_scan(target, scan_type, ports, options)` - NMAP scanning
  - `ping_host(host, count, timeout)` - Ping connectivity test
  - `port_scan(host, ports, scan_type)` - Port scanning
  - `network_discovery(network)` - Network host discovery

### 3. **Management App** (`main.py`)
- Start all servers with interactive management
- Health checks and monitoring
- Graceful shutdown handling

## 🚀 Quick Start

### Start Individual Servers
```bash
# File server
python servers/file_server.py

# NMAP server  
python servers/nmap_server.py
```

### Start All Servers
```bash
# Interactive mode
python main.py

# Background mode
python main.py start
```

### Test Servers
```bash
# Simple functionality test
python simple_test.py

# Run test examples
python demo.py
```

## 📋 Dependencies Installed

- ✅ `fastmcp` - FastMCP framework
- ✅ `uvicorn` - ASGI server
- ✅ `requests` - HTTP client library  
- ✅ `python-nmap` - Python NMAP wrapper
- ✅ `nmap` - Network mapping tool

## 🔧 Usage Examples

### File Operations
```bash
curl -X POST http://127.0.0.1:8001/mcp/call \\
  -H "Content-Type: application/json" \\
  -d '{"tool": "read_file", "arguments": {"file_path": "README.md"}}'

curl -X POST http://127.0.0.1:8001/mcp/call \\
  -H "Content-Type: application/json" \\
  -d '{"tool": "list_directory", "arguments": {"dir_path": "."}}'
```

### Network Operations
```bash
curl -X POST http://127.0.0.1:8002/mcp/call \\
  -H "Content-Type: application/json" \\
  -d '{"tool": "ping_host", "arguments": {"host": "127.0.0.1", "count": 3}}'

curl -X POST http://127.0.0.1:8002/mcp/call \\
  -H "Content-Type: application/json" \\
  -d '{"tool": "nmap_scan", "arguments": {"target": "127.0.0.1", "ports": "80,443,8001,8002"}}'
```

## 🛡️ Security Notes

- File server can access any file readable by the user
- NMAP server executes system commands
- Consider implementing authentication for production
- Use firewall rules to restrict network access if needed

## 📁 Project Structure

```
MCP_tools/
├── servers/
│   ├── file_server.py      # File operations server
│   └── nmap_server.py      # Network scanning server  
├── main.py                 # Server manager application
├── simple_test.py          # Simple functionality test
├── demo.py                 # Usage demonstration
├── requirements.txt        # Python dependencies
├── setup.sh                # Installation script
└── README.md              # Documentation
```

## 🎯 Next Steps

### For Claude Desktop Integration (Recommended):
1. **Generate Claude config:** `python generate_claude_config.py`
2. **Restart Claude Desktop**
3. **Start using tools in Claude Desktop:**
   - "Read the README.md file"
   - "List files in current directory"
   - "Ping google.com"
   - "Scan port 80 on localhost"

### For Manual Server Management:
1. **Start the servers:** `python main.py`
2. **Test functionality:** `python simple_test.py` 
3. **Try examples:** `python demo.py`
4. **Integrate with your applications** using the REST API endpoints

Your FastMCP server collection is ready! 🚀

## 📋 Additional Files Created

- `generate_claude_config.py` - Generates Claude Desktop configuration
- `preview_claude_config.py` - Preview configuration without writing
- `CLAUDE_DESKTOP_GUIDE.md` - Comprehensive Claude Desktop usage guide
