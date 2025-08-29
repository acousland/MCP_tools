#!/usr/bin/env python3
"""
Telnet Server - MCP server for Telnet connections and remote command execution.
Provides tools to connect to remote systems via Telnet (insecure protocol).
Note: Uses socket-based implementation since telnetlib was deprecated in Python 3.11+
"""

import socket
import time
import re
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Telnet Server")

def _connect_telnet(host: str, port: int = 23, timeout: int = 30) -> Dict[str, Any]:
    """
    Create Telnet connection using socket and return connection object or error.
    
    Args:
        host: Telnet server hostname or IP
        port: Telnet port (default: 23)
        timeout: Connection timeout
    
    Returns:
        Dictionary with connection result
    """
    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        
        return {
            "success": True,
            "socket": sock,
            "host": host,
            "port": port
        }
        
    except socket.timeout:
        return {
            "success": False,
            "error": f"Connection to {host}:{port} timed out after {timeout} seconds"
        }
    except socket.gaierror as e:
        return {
            "success": False,
            "error": f"DNS resolution failed for {host}: {e}"
        }
    except ConnectionRefusedError:
        return {
            "success": False,
            "error": f"Connection refused by {host}:{port}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Telnet connection failed: {e}"
        }

@mcp.tool()
def telnet_connect(host: str, port: int = 23, timeout: int = 30, 
                   read_timeout: int = 10) -> str:
    """
    Connect to a Telnet server and read initial response.
    
    Args:
        host: Telnet server hostname or IP address
        port: Telnet port (default: 23)
        timeout: Connection timeout in seconds
        read_timeout: Time to wait for initial response
    
    Returns:
        Connection result and initial server response
    """
    # Basic validation
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    if not (1 <= port <= 65535):
        return "Error: Invalid port number"
    
    # Connect to Telnet server
    conn_result = _connect_telnet(host, port, timeout)
    
    if not conn_result["success"]:
        return f"Error: {conn_result['error']}"
    
    sock = conn_result["socket"]
    
    try:
        # Set socket timeout for reading
        sock.settimeout(read_timeout)
        
        # Read initial response from server
        try:
            initial_response = sock.recv(4096).decode('utf-8', errors='ignore')
        except socket.timeout:
            initial_response = "No response within timeout period"
        
        # Close connection
        sock.close()
        
        # Format output
        output = f"Telnet Connection Test\n"
        output += f"{'='*35}\n"
        output += f"Server: {host}:{port}\n"
        output += f"Status: ✅ Connection successful\n"
        output += f"{'='*35}\n"
        
        if initial_response.strip():
            output += f"Initial Response:\n{initial_response}\n"
        else:
            output += f"No initial response received\n"
        
        return output
        
    except Exception as e:
        try:
            sock.close()
        except:
            pass
        return f"Error reading from server: {e}"

@mcp.tool()
def telnet_execute(host: str, command: str, port: int = 23, timeout: int = 30) -> str:
    """
    Test Telnet connection and provide manual execution instructions.
    Note: Interactive command execution via Telnet requires manual intervention.
    
    Args:
        host: Telnet server hostname or IP address
        command: Command to note for manual execution
        port: Telnet port (default: 23)
        timeout: Connection timeout in seconds
    
    Returns:
        Connection test and manual execution instructions
    """
    # Basic validation
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    if not command or len(command) > 500:
        return "Error: Invalid or too long command specified"
    
    # Security warning for dangerous commands
    dangerous_patterns = ['rm -rf', 'mkfs', 'dd if=', '> /dev/', 'format ', 'fdisk']
    if any(pattern in command.lower() for pattern in dangerous_patterns):
        return "Error: Potentially dangerous command blocked for safety"
    
    # Test connection first
    conn_result = _connect_telnet(host, port, timeout)
    
    output = f"Telnet Connection Test & Command Info\n"
    output += f"{'='*45}\n"
    output += f"Server: {host}:{port}\n"
    output += f"Command: {command}\n"
    output += f"{'='*45}\n"
    
    if conn_result["success"]:
        sock = conn_result["socket"]
        
        # Try to read banner
        try:
            sock.settimeout(5)
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            output += f"✅ Connection successful\n"
            if banner.strip():
                output += f"Banner: {banner[:100]}...\n" if len(banner) > 100 else f"Banner: {banner}\n"
        except:
            output += f"✅ Connection successful (no banner)\n"
        
        try:
            sock.close()
        except:
            pass
        
        output += f"\n🔧 Manual Execution Instructions:\n"
        output += f"1. Connect: telnet {host} {port}\n"
        output += f"2. Login (if required)\n"
        output += f"3. Execute: {command}\n"
        output += f"\n⚠️  Security Warning:\n"
        output += f"- Telnet is insecure (plain text)\n"
        output += f"- Use SSH when possible\n"
        output += f"- Only use on trusted networks\n"
    else:
        output += f"❌ Connection failed\n"
        output += f"Error: {conn_result['error']}\n"
    
    return output

@mcp.tool()
def telnet_port_check(host: str, port: int, timeout: int = 10) -> str:
    """
    Check if a specific port is open via Telnet connection.
    
    Args:
        host: Target hostname or IP address
        port: Port to check
        timeout: Connection timeout in seconds
    
    Returns:
        Port check result
    """
    # Basic validation
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    if not (1 <= port <= 65535):
        return "Error: Invalid port number"
    
    # Test connection
    conn_result = _connect_telnet(host, port, timeout)
    
    output = f"Telnet Port Check\n"
    output += f"{'='*25}\n"
    output += f"Target: {host}:{port}\n"
    output += f"Timeout: {timeout}s\n"
    output += f"{'='*25}\n"
    
    if conn_result["success"]:
        sock = conn_result["socket"]
        
        # Try to read some data to confirm the service is responding
        try:
            sock.settimeout(5)
            data = sock.recv(1024)
            if data:
                preview = data.decode('utf-8', errors='ignore')[:100]
                output += f"✅ Port is open and responding\n"
                output += f"Service banner: {preview}...\n" if len(preview) == 100 else f"Service banner: {preview}\n"
            else:
                output += f"✅ Port is open (no banner)\n"
        except:
            output += f"✅ Port is open (unable to read banner)\n"
        
        try:
            sock.close()
        except:
            pass
    else:
        output += f"❌ Port is closed or filtered\n"
        output += f"Details: {conn_result['error']}\n"
    
    return output
    
    return output

@mcp.tool()
def telnet_banner_grab(host: str, port: int = 23, timeout: int = 10, 
                       wait_time: int = 3) -> str:
    """
    Connect to a service and grab its banner via Telnet.
    
    Args:
        host: Target hostname or IP address
        port: Target port
        timeout: Connection timeout in seconds
        wait_time: Time to wait for banner data
    
    Returns:
        Service banner information
    """
    # Basic validation
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    if not (1 <= port <= 65535):
        return "Error: Invalid port number"
    
    # Connect to service
    conn_result = _connect_telnet(host, port, timeout)
    
    if not conn_result["success"]:
        return f"Error: {conn_result['error']}"
    
    sock = conn_result["socket"]
    
    try:
        # Set socket timeout for reading
        sock.settimeout(wait_time)
        
        # Read available data
        try:
            banner_data = sock.recv(4096)
            banner_text = banner_data.decode('utf-8', errors='ignore') if banner_data else ""
        except socket.timeout:
            banner_text = ""
        
        # Close connection
        sock.close()
        
        # Format output
        output = f"Service Banner Grab\n"
        output += f"{'='*30}\n"
        output += f"Target: {host}:{port}\n"
        output += f"Wait time: {wait_time}s\n"
        output += f"{'='*30}\n"
        
        if banner_text.strip():
            output += f"Banner:\n{banner_text}\n"
        else:
            output += f"No banner received (service may not send one)\n"
        
        return output
        
    except Exception as e:
        try:
            sock.close()
        except:
            pass
        return f"Error grabbing banner: {e}"

@mcp.tool()
def telnet_interactive_session(host: str, port: int = 23, timeout: int = 30) -> str:
    """
    Get information about starting an interactive Telnet session.
    
    Args:
        host: Telnet server hostname or IP address
        port: Telnet port (default: 23)
        timeout: Connection timeout in seconds
    
    Returns:
        Instructions for interactive session
    """
    # Basic validation
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    if not (1 <= port <= 65535):
        return "Error: Invalid port number"
    
    # Test connection first
    conn_result = _connect_telnet(host, port, timeout)
    
    output = f"Telnet Interactive Session Info\n"
    output += f"{'='*40}\n"
    output += f"Target: {host}:{port}\n"
    output += f"{'='*40}\n"
    
    if conn_result["success"]:
        sock = conn_result["socket"]
        
        # Get initial response
        try:
            sock.settimeout(5)
            initial = sock.recv(1024).decode('utf-8', errors='ignore')
            output += f"✅ Connection successful\n"
            if initial.strip():
                output += f"Initial response:\n{initial[:200]}...\n" if len(initial) > 200 else f"Initial response:\n{initial}\n"
        except:
            output += f"✅ Connection successful (no initial response)\n"
        
        try:
            sock.close()
        except:
            pass
        
        output += f"\n📋 Interactive Session Instructions:\n"
        output += f"1. Open terminal and run: telnet {host} {port}\n"
        output += f"2. If login required, enter credentials\n"
        output += f"3. Type 'exit' or Ctrl+] then 'quit' to disconnect\n"
        output += f"\n⚠️  Security Reminders:\n"
        output += f"- Telnet transmits data in plain text\n"
        output += f"- Only use on trusted networks\n"
        output += f"- Consider using SSH instead\n"
        
    else:
        output += f"❌ Connection failed\n"
        output += f"Error: {conn_result['error']}\n"
        output += f"\n🔧 Troubleshooting:\n"
        output += f"- Check if host is reachable: ping {host}\n"
        output += f"- Verify port is open: nmap -p {port} {host}\n"
        output += f"- Check firewall settings\n"
    
    return output

# Run the server
if __name__ == "__main__":
    mcp.run()

if __name__ == "__main__":
    import sys
    
    # Check if we should run in HTTP mode (for testing) or stdio mode (for Claude Desktop)
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # HTTP mode for testing
        import asyncio
        
        async def run_server():
            await mcp.run_http_async(host="127.0.0.1", port=8005)
        
        print("🚀 Starting Telnet Server in HTTP mode on http://127.0.0.1:8005")
        print("Use --http flag to run in HTTP mode, otherwise runs in stdio mode for Claude Desktop")
        asyncio.run(run_server())
    else:
        # Stdio mode for Claude Desktop
        mcp.run()
