#!/usr/bin/env python3
"""
Troubleshooting script for MCP Tools and Claude Desktop integration.
"""

import subprocess
import sys
import json
import os
from pathlib import Path
from generate_claude_config import get_claude_config_path, get_python_executable

def test_stdio_mode():
    """Test if servers work in stdio mode."""
    print("🧪 Testing MCP Servers in stdio mode (Claude Desktop mode)")
    print("=" * 60)
    
    servers = [
        ("File Server", "servers/file_server.py"),
        ("NMAP Server", "servers/nmap_server.py")
    ]
    
    python_exe = get_python_executable()
    
    for name, script in servers:
        print(f"\n📡 Testing {name}...")
        script_path = Path(script)
        
        if not script_path.exists():
            print(f"❌ Script not found: {script}")
            continue
        
        try:
            # Test that the server can start in stdio mode
            # We'll send it an initialize message to see if it responds
            process = subprocess.Popen(
                [python_exe, str(script_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send MCP initialize message
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send the message
            message_json = json.dumps(init_message) + "\n"
            
            try:
                stdout, stderr = process.communicate(input=message_json, timeout=5)
                
                if process.returncode == 0 or "initialize" in stdout:
                    print(f"✅ {name} responds to MCP protocol in stdio mode")
                    if stderr:
                        print(f"   stderr: {stderr[:200]}...")
                else:
                    print(f"❌ {name} failed in stdio mode")
                    print(f"   stdout: {stdout[:200]}")
                    print(f"   stderr: {stderr[:200]}")
                    
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️  {name} didn't respond within 5 seconds (may be normal for stdio mode)")
                
        except Exception as e:
            print(f"❌ Error testing {name}: {e}")

def test_http_mode():
    """Test if servers work in HTTP mode."""
    print("\n🌐 Testing MCP Servers in HTTP mode (for manual testing)")
    print("=" * 60)
    
    servers = [
        ("File Server", "servers/file_server.py", 8001),
        ("NMAP Server", "servers/nmap_server.py", 8002)
    ]
    
    python_exe = get_python_executable()
    
    for name, script, port in servers:
        print(f"\n📡 Testing {name} on port {port}...")
        script_path = Path(script)
        
        if not script_path.exists():
            print(f"❌ Script not found: {script}")
            continue
        
        try:
            # Start server in HTTP mode
            process = subprocess.Popen(
                [python_exe, str(script_path), "--http"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it time to start
            import time
            time.sleep(3)
            
            # Check if it's still running
            if process.poll() is None:
                print(f"✅ {name} started successfully in HTTP mode")
                
                # Try to connect
                try:
                    import requests
                    response = requests.get(f"http://127.0.0.1:{port}/health", timeout=2)
                    print(f"✅ HTTP endpoint responding: {response.status_code}")
                except Exception as e:
                    print(f"⚠️  HTTP endpoint test failed: {e}")
                
                # Clean up
                process.terminate()
                process.wait(timeout=5)
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {name} failed to start in HTTP mode")
                print(f"   stdout: {stdout[:200]}")
                print(f"   stderr: {stderr[:200]}")
                
        except Exception as e:
            print(f"❌ Error testing {name}: {e}")

def check_claude_config():
    """Check Claude Desktop configuration."""
    print("\n🔧 Checking Claude Desktop Configuration")
    print("=" * 50)
    
    config_path = get_claude_config_path()
    print(f"📁 Config file: {config_path}")
    
    if not config_path.exists():
        print("❌ Claude Desktop config file not found")
        print("   Run: python generate_claude_config.py")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "mcpServers" not in config:
            print("❌ No mcpServers section in config")
            return False
        
        mcp_servers = config["mcpServers"]
        print(f"✅ Found {len(mcp_servers)} MCP servers in config")
        
        for server_name, server_config in mcp_servers.items():
            if server_name.startswith("mcp-"):
                print(f"📡 {server_name}")
                command = server_config.get("command", "")
                args = server_config.get("args", [])
                
                # Check if command exists
                if os.path.exists(command):
                    print(f"   ✅ Command exists: {command}")
                else:
                    print(f"   ❌ Command not found: {command}")
                
                # Check if script exists
                if args and os.path.exists(args[0]):
                    print(f"   ✅ Script exists: {args[0]}")
                else:
                    print(f"   ❌ Script not found: {args[0] if args else 'No args'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

def check_processes():
    """Check for running MCP server processes."""
    print("\n🔍 Checking for Running MCP Server Processes")
    print("=" * 50)
    
    try:
        # Check for processes containing our script names
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        lines = result.stdout.split('\n')
        mcp_processes = [
            line for line in lines 
            if any(script in line for script in ["file_server.py", "nmap_server.py"])
        ]
        
        if mcp_processes:
            print(f"⚠️  Found {len(mcp_processes)} potentially conflicting processes:")
            for i, line in enumerate(mcp_processes[:5]):  # Show first 5
                print(f"   {i+1}. {line[:100]}...")
            
            if len(mcp_processes) > 5:
                print(f"   ... and {len(mcp_processes) - 5} more")
                
            print("\n💡 You may need to kill these processes:")
            print("   pkill -f file_server.py")
            print("   pkill -f nmap_server.py")
        else:
            print("✅ No conflicting MCP server processes found")
            
    except Exception as e:
        print(f"❌ Error checking processes: {e}")

def kill_mcp_processes():
    """Kill any running MCP server processes."""
    print("\n🛑 Killing MCP Server Processes")
    print("=" * 40)
    
    scripts = ["file_server.py", "nmap_server.py"]
    
    for script in scripts:
        try:
            result = subprocess.run(
                ["pkill", "-f", script],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Killed processes for {script}")
            else:
                print(f"ℹ️  No processes found for {script}")
                
        except Exception as e:
            print(f"❌ Error killing {script} processes: {e}")

def main():
    """Main troubleshooting function."""
    print("🔧 MCP Tools - Claude Desktop Troubleshooting")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "stdio":
            test_stdio_mode()
        elif command == "http":
            test_http_mode()
        elif command == "config":
            check_claude_config()
        elif command == "processes":
            check_processes()
        elif command == "kill":
            kill_mcp_processes()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: stdio, http, config, processes, kill")
    else:
        # Run all checks
        check_processes()
        print()
        check_claude_config()
        print()
        test_stdio_mode()
        
        print("\n📋 Summary and Recommendations:")
        print("=" * 40)
        print("1. Ensure no conflicting processes are running")
        print("2. Verify Claude Desktop configuration is correct")
        print("3. Test servers in stdio mode (Claude Desktop expects this)")
        print("4. Restart Claude Desktop after configuration changes")
        print("\n💡 Common fixes:")
        print("   python troubleshoot.py kill          # Kill conflicting processes")
        print("   python generate_claude_config.py     # Regenerate configuration")
        print("   python troubleshoot.py config        # Check configuration")

if __name__ == "__main__":
    main()
