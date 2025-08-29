#!/usr/bin/env python3
"""
Example usage of MCP Tools servers.
This script demonstrates how to interact with the FastMCP servers.
"""

import requests
import json
import time
import sys

def call_tool(server_port: int, tool_name: str, arguments: dict) -> dict:
    """Call a tool on an MCP server."""
    url = f"http://127.0.0.1:{server_port}/call"
    payload = {
        "tool": tool_name,
        "arguments": arguments
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def example_file_operations():
    """Demonstrate file server operations."""
    print("\n📁 File Server Examples")
    print("=" * 40)
    
    # Read the README file
    print("📖 Reading README.md...")
    result = call_tool(8001, "read_file", {"file_path": "README.md"})
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        content = result.get("result", "")
        lines = content.split('\n')
        print(f"✅ File read successfully ({len(lines)} lines)")
        print(f"First few lines:")
        for line in lines[:5]:
            print(f"   {line}")
        if len(lines) > 5:
            print("   ...")
    
    # List current directory
    print("\n📂 Listing current directory...")
    result = call_tool(8001, "list_directory", {"dir_path": "."})
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ Directory listing:")
        print(result.get("result", ""))
    
    # Get file info for main.py
    print("ℹ️  Getting file info for main.py...")
    result = call_tool(8001, "get_file_info", {"file_path": "main.py"})
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ File info:")
        info = result.get("result", "")
        # Show first few lines of info
        for line in info.split('\n')[:10]:
            print(f"   {line}")

def example_network_operations():
    """Demonstrate NMAP server operations."""
    print("\n🌐 NMAP Server Examples")
    print("=" * 40)
    
    # Ping localhost
    print("🏓 Pinging localhost...")
    result = call_tool(8002, "ping_host", {
        "host": "127.0.0.1", 
        "count": 3,
        "timeout": 2
    })
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ Ping result:")
        ping_output = result.get("result", "")
        # Show relevant lines
        for line in ping_output.split('\n'):
            if line.strip() and ('ping' in line.lower() or 'packet' in line.lower() or 'time=' in line):
                print(f"   {line}")
    
    # Simple port scan on localhost
    print("\n🔍 Scanning common ports on localhost...")
    result = call_tool(8002, "port_scan", {
        "host": "127.0.0.1",
        "ports": "22,80,443,8001,8002",
        "scan_type": "tcp"
    })
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ Port scan result:")
        scan_output = result.get("result", "")
        # Show relevant lines
        for line in scan_output.split('\n'):
            if line.strip() and ('open' in line.lower() or 'closed' in line.lower() or 'filtered' in line.lower()):
                print(f"   {line}")
    
    # Basic NMAP scan
    print("\n🎯 Basic NMAP scan of localhost...")
    result = call_tool(8002, "nmap_scan", {
        "target": "127.0.0.1",
        "scan_type": "basic",
        "ports": "8001-8002"
    })
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ NMAP scan result:")
        scan_output = result.get("result", "")
        # Show summary lines
        lines = scan_output.split('\n')
        in_results = False
        for line in lines:
            if '=' in line and 'NMAP' in line:
                in_results = True
                continue
            if in_results and line.strip():
                if len(line) < 100:  # Skip very long lines
                    print(f"   {line}")

def check_servers():
    """Check if servers are running."""
    print("🔍 Checking server status...")
    
    servers = [
        ("File Server", 8001),
        ("NMAP Server", 8002)
    ]
    
    all_running = True
    
    for name, port in servers:
        try:
            response = requests.get(f"http://127.0.0.1:{port}/health", timeout=3)
            if response.status_code == 200:
                print(f"✅ {name} is running on port {port}")
            else:
                print(f"❌ {name} returned status {response.status_code}")
                all_running = False
        except requests.exceptions.ConnectionError:
            print(f"❌ {name} is not responding on port {port}")
            all_running = False
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            all_running = False
    
    return all_running

def main():
    """Main example function."""
    print("🚀 MCP Tools - Usage Examples")
    print("=" * 50)
    
    # Check if servers are running
    if not check_servers():
        print("\n⚠️  Some servers are not running. Please start them first:")
        print("   python3 main.py")
        sys.exit(1)
    
    print("\n🎯 Running examples...")
    
    # File server examples
    example_file_operations()
    
    # Network server examples  
    example_network_operations()
    
    print("\n🎉 Examples completed!")
    print("\n💡 Tips:")
    print("   - All servers provide REST APIs at http://127.0.0.1:<port>")
    print("   - Use POST /call to invoke tools")
    print("   - Use GET /tools to list available tools")
    print("   - Use GET /health to check server status")
    print("   - Check the server logs for debugging")

if __name__ == "__main__":
    main()
