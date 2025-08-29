# MCP Tools - Claude Desktop Fix

## 🎯 **Issue Fixed!**

The problem was that the MCP servers were configured to run in **HTTP mode** instead of **stdio mode**. Claude Desktop expects MCP servers to communicate via standard input/output (stdio), not HTTP endpoints.

## ✅ **What Was Fixed:**

1. **Server Mode Detection**: Servers now automatically detect how they're being run
   - **stdio mode** (default) - for Claude Desktop integration  
   - **HTTP mode** (with `--http` flag) - for manual testing

2. **Port Conflicts Resolved**: No more "address already in use" errors
3. **Proper Transport**: Uses stdio transport instead of HTTP for Claude Desktop

## 🔧 **How to Use Now:**

### For Claude Desktop (Recommended):
```bash
# 1. Kill any existing processes
python troubleshoot.py kill

# 2. Regenerate configuration  
python generate_claude_config.py --yes

# 3. Restart Claude Desktop

# 4. Test in Claude Desktop:
#    - "Read the README.md file"
#    - "List files in current directory" 
#    - "Ping google.com"
```

### For Manual Testing (HTTP Mode):
```bash
# Start individual servers with --http flag
python servers/file_server.py --http      # Port 8001
python servers/nmap_server.py --http      # Port 8002

# Or start all servers for testing
python main.py                            # Uses HTTP mode automatically
```

## 🛠️ **Troubleshooting Commands:**

```bash
# Check all aspects of setup
python troubleshoot.py

# Kill conflicting processes
python troubleshoot.py kill

# Test stdio mode (what Claude Desktop uses)
python troubleshoot.py stdio

# Test HTTP mode (for manual testing)
python troubleshoot.py http

# Check Claude Desktop configuration
python troubleshoot.py config

# Check for running processes
python troubleshoot.py processes
```

## 📋 **Server Modes Explained:**

### Stdio Mode (Claude Desktop):
- Default when run without flags
- Uses standard input/output for communication
- No network ports required
- What Claude Desktop expects

### HTTP Mode (Manual Testing):
- Enabled with `--http` flag  
- Runs web server on specific ports
- Useful for testing with curl/API calls
- Not used by Claude Desktop

## 🎉 **The Fix:**

The servers now automatically run in the correct mode:

```python
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # HTTP mode for testing
        await mcp.run_http_async(host="127.0.0.1", port=8001)
    else:
        # Stdio mode for Claude Desktop  
        mcp.run()
```

Your MCP Tools should now work perfectly with Claude Desktop! 🚀
