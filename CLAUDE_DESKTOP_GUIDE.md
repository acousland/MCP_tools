# Claude Desktop Integration Guide

This guide explains how to set up and use the MCP Tools servers with Claude Desktop.

## 🚀 Quick Setup

1. **Generate the configuration:**
   ```bash
   python generate_claude_config.py
   ```

2. **Restart Claude Desktop**

3. **Start using the tools!**

## 🔧 Available Tools in Claude Desktop

Once configured, you can ask Claude to use these tools naturally:

### 📁 File Operations

**Reading Files:**
- "Read the contents of README.md"
- "Show me what's in the main.py file"
- "Read the first 50 lines of the config file"

**Directory Listing:**
- "List all files in the current directory"
- "Show me the contents of the servers folder"
- "List all Python files in this directory"

**File Information:**
- "Get information about the LICENSE file"
- "Show me the size and permissions of main.py"
- "What type of file is setup.sh?"

### 🌐 Network Operations

**Connectivity Testing:**
- "Ping google.com"
- "Test connectivity to 127.0.0.1"
- "Ping github.com 5 times"

**Port Scanning:**
- "Scan port 80 on localhost"
- "Check if ports 22, 80, and 443 are open on google.com"
- "Scan ports 1-1000 on 127.0.0.1"

**Network Discovery:**
- "Discover active hosts on my local network"
- "Find devices on 192.168.1.0/24"
- "Scan my subnet for active machines"

**Advanced NMAP Scans:**
- "Run a TCP SYN scan on 127.0.0.1"
- "Perform service detection on localhost"
- "Do an OS detection scan on google.com"

## 💡 Usage Tips

### Natural Language
You can use natural language to request operations:
- ✅ "Can you read my README file and summarize it?"
- ✅ "Check if my local web server on port 8080 is running"
- ✅ "List all the configuration files in this project"

### Combining Operations
Claude can chain operations together:
- "List all Python files, then read the main.py file"
- "Ping google.com and then scan its port 80"
- "Check what files are in the servers directory and read one of them"

### File Paths
- Use relative paths from the project directory
- Absolute paths work too: `/Users/username/Documents/file.txt`
- Claude will help resolve path issues

## 🛠️ Configuration Details

### Generated Configuration
The script creates entries in your Claude Desktop config like this:

```json
{
  "mcpServers": {
    "mcp-file-server": {
      "command": "/path/to/MCP_tools/.venv/bin/python",
      "args": ["/path/to/MCP_tools/servers/file_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/MCP_tools"
      }
    },
    "mcp-nmap-server": {
      "command": "/path/to/MCP_tools/.venv/bin/python", 
      "args": ["/path/to/MCP_tools/servers/nmap_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/MCP_tools"
      }
    }
  }
}
```

### Configuration Location
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## 🔍 Troubleshooting

### MCP Servers Not Available
1. **Check Claude Desktop restart**: Make sure you restarted Claude Desktop after configuration
2. **Verify configuration**: Run `python preview_claude_config.py` to check paths
3. **Check permissions**: Ensure the Python executable and scripts are accessible
4. **Regenerate config**: Run `python generate_claude_config.py --yes` again

### Tool Execution Errors
1. **Python environment**: Make sure the virtual environment is properly set up
2. **Dependencies**: Verify all packages are installed with `pip list`
3. **NMAP installation**: Check that `nmap` command works in terminal
4. **File permissions**: Ensure scripts are executable

### Path Issues
- The configuration uses absolute paths, so moving the project folder requires regenerating the config
- Virtual environment must exist in `.venv` directory within the project

## 🔒 Security Considerations

### File Server
- Can read any file accessible to your user account
- Cannot write or modify files (read-only access)
- Respects file system permissions

### NMAP Server  
- Executes system network commands
- Limited to safe scanning operations
- Some advanced NMAP features may require root privileges

### Best Practices
- Only use on trusted networks
- Be cautious with network scanning in corporate environments
- Consider firewall rules for sensitive environments

## 📋 Example Conversations

### File Management
```
You: "Read my README file and tell me what this project does"
Claude: *uses read_file tool* "This project provides MCP servers for file operations and network scanning..."

You: "What Python files are in the servers directory?"
Claude: *uses list_directory tool* "I found two Python files: file_server.py and nmap_server.py..."
```

### Network Analysis
```
You: "Check if my local development server on port 3000 is running"
Claude: *uses port_scan tool* "I'll scan port 3000 on localhost... The port appears to be closed."

You: "Is google.com reachable from here?"
Claude: *uses ping_host tool* "Yes, google.com is reachable. All 4 ping packets were successful..."
```

## 🎯 Getting Started Checklist

- [ ] Run `python generate_claude_config.py`
- [ ] Restart Claude Desktop application
- [ ] Test with simple command: "List files in current directory"
- [ ] Try network test: "Ping 127.0.0.1"
- [ ] Explore more advanced features

Your MCP Tools are now integrated with Claude Desktop! 🎉
