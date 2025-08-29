#!/usr/bin/env python3
"""
SSH Server - MCP server for SSH connections and remote command execution.
Provides tools to connect to remote systems via SSH and execute commands.
"""

import subprocess
import os
import tempfile
import json
from typing import Any, Dict, List, Optional
from pathlib import Path

from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("SSH Server")

def _run_ssh_command(host: str, command: str, username: str = None, password: str = None, 
                    key_file: str = None, port: int = 22, timeout: int = 30) -> Dict[str, Any]:
    """
    Run an SSH command safely and return the result.
    
    Args:
        host: Target hostname or IP address
        command: Command to execute on remote host
        username: SSH username
        password: SSH password (not recommended, use key_file instead)
        key_file: Path to SSH private key file
        port: SSH port (default: 22)
        timeout: Timeout in seconds
    
    Returns:
        Dictionary with command result
    """
    try:
        # Build SSH command
        ssh_cmd = ["ssh", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no"]
        
        # Add port if not default
        if port != 22:
            ssh_cmd.extend(["-p", str(port)])
        
        # Add key file if specified
        if key_file and os.path.exists(key_file):
            ssh_cmd.extend(["-i", key_file])
        
        # Add username and host
        if username:
            ssh_cmd.append(f"{username}@{host}")
        else:
            ssh_cmd.append(host)
        
        # Add command
        ssh_cmd.append(command)
        
        # Execute SSH command
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "command": " ".join(ssh_cmd[:-1]) + " [COMMAND]"  # Hide actual command for security
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"SSH command timed out after {timeout} seconds"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"SSH command execution failed: {e}"
        }

@mcp.tool()
def ssh_execute(host: str, command: str, username: str = None, key_file: str = None, 
                port: int = 22, timeout: int = 30) -> str:
    """
    Execute a command on a remote host via SSH.
    
    Args:
        host: Target hostname or IP address
        command: Command to execute on the remote host
        username: SSH username (if not specified, uses current user)
        key_file: Path to SSH private key file (recommended over password)
        port: SSH port (default: 22)
        timeout: Command timeout in seconds (default: 30)
    
    Returns:
        Command output and execution details
    """
    # Basic validation
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    if not command or len(command) > 500:
        return "Error: Invalid or too long command specified"
    
    # Security check - prevent dangerous commands
    dangerous_patterns = ['rm -rf', 'mkfs', 'dd if=', '> /dev/', 'format ', 'fdisk']
    if any(pattern in command.lower() for pattern in dangerous_patterns):
        return "Error: Potentially dangerous command blocked for safety"
    
    # Execute SSH command
    result = _run_ssh_command(host, command, username, None, key_file, port, timeout)
    
    if not result["success"]:
        return f"SSH Error: {result.get('error', 'Unknown error')}"
    
    # Format output
    output = f"SSH Command Execution on {host}\n"
    output += f"{'='*50}\n"
    output += f"User: {username or 'current user'}\n"
    output += f"Port: {port}\n"
    output += f"Command: {command}\n"
    output += f"Exit Code: {result['returncode']}\n"
    output += f"{'='*50}\n"
    
    if result["stdout"]:
        output += f"STDOUT:\n{result['stdout']}\n"
    
    if result["stderr"]:
        output += f"STDERR:\n{result['stderr']}\n"
    
    return output

@mcp.tool()
def ssh_copy_file(host: str, local_path: str, remote_path: str, username: str = None, 
                  key_file: str = None, port: int = 22, direction: str = "upload") -> str:
    """
    Copy files to/from a remote host via SCP.
    
    Args:
        host: Target hostname or IP address
        local_path: Local file path
        remote_path: Remote file path
        username: SSH username
        key_file: Path to SSH private key file
        port: SSH port (default: 22)
        direction: "upload" (local->remote) or "download" (remote->local)
    
    Returns:
        File copy result
    """
    # Validate inputs
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    if direction not in ["upload", "download"]:
        return "Error: Direction must be 'upload' or 'download'"
    
    try:
        # Build SCP command
        scp_cmd = ["scp", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no"]
        
        # Add port if not default
        if port != 22:
            scp_cmd.extend(["-P", str(port)])
        
        # Add key file if specified
        if key_file and os.path.exists(key_file):
            scp_cmd.extend(["-i", key_file])
        
        # Set source and destination based on direction
        if direction == "upload":
            if not os.path.exists(local_path):
                return f"Error: Local file not found: {local_path}"
            
            source = local_path
            if username:
                destination = f"{username}@{host}:{remote_path}"
            else:
                destination = f"{host}:{remote_path}"
        else:  # download
            if username:
                source = f"{username}@{host}:{remote_path}"
            else:
                source = f"{host}:{remote_path}"
            destination = local_path
        
        scp_cmd.extend([source, destination])
        
        # Execute SCP command
        result = subprocess.run(
            scp_cmd,
            capture_output=True,
            text=True,
            timeout=60,  # Longer timeout for file transfers
            check=False
        )
        
        # Format output
        output = f"SCP File Copy ({direction.upper()})\n"
        output += f"{'='*40}\n"
        output += f"Host: {host}:{port}\n"
        output += f"User: {username or 'current user'}\n"
        output += f"Local: {local_path}\n"
        output += f"Remote: {remote_path}\n"
        output += f"Exit Code: {result.returncode}\n"
        output += f"{'='*40}\n"
        
        if result.returncode == 0:
            output += "✅ File copy completed successfully\n"
        else:
            output += f"❌ File copy failed\n"
        
        if result.stdout:
            output += f"Output: {result.stdout}\n"
        
        if result.stderr:
            output += f"Errors: {result.stderr}\n"
        
        return output
        
    except subprocess.TimeoutExpired:
        return "Error: SCP operation timed out"
    except Exception as e:
        return f"Error: SCP operation failed: {e}"

@mcp.tool()
def ssh_tunnel(host: str, local_port: int, remote_host: str = "localhost", 
               remote_port: int = 80, username: str = None, key_file: str = None, 
               ssh_port: int = 22, duration: int = 60) -> str:
    """
    Create an SSH tunnel (port forwarding).
    
    Args:
        host: SSH server hostname or IP address
        local_port: Local port to bind to
        remote_host: Remote host to forward to (default: localhost on SSH server)
        remote_port: Remote port to forward to
        username: SSH username
        key_file: Path to SSH private key file
        ssh_port: SSH server port (default: 22)
        duration: How long to keep tunnel open in seconds (default: 60)
    
    Returns:
        Tunnel creation result
    """
    # Validate inputs
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    if not (1 <= local_port <= 65535) or not (1 <= remote_port <= 65535):
        return "Error: Invalid port numbers"
    
    if duration > 300:  # Max 5 minutes for safety
        return "Error: Maximum tunnel duration is 300 seconds"
    
    try:
        # Build SSH tunnel command
        ssh_cmd = [
            "ssh", "-N", "-L", 
            f"{local_port}:{remote_host}:{remote_port}",
            "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=no"
        ]
        
        # Add SSH port if not default
        if ssh_port != 22:
            ssh_cmd.extend(["-p", str(ssh_port)])
        
        # Add key file if specified
        if key_file and os.path.exists(key_file):
            ssh_cmd.extend(["-i", key_file])
        
        # Add username and host
        if username:
            ssh_cmd.append(f"{username}@{host}")
        else:
            ssh_cmd.append(host)
        
        # Start tunnel in background with timeout
        import signal
        import time
        
        output = f"SSH Tunnel Setup\n"
        output += f"{'='*30}\n"
        output += f"SSH Server: {host}:{ssh_port}\n"
        output += f"Tunnel: localhost:{local_port} -> {remote_host}:{remote_port}\n"
        output += f"Duration: {duration} seconds\n"
        output += f"{'='*30}\n"
        
        # Note: This is a simplified implementation
        # In a real scenario, you'd want to manage the tunnel process more carefully
        output += f"⚠️  Note: SSH tunnel creation requires interactive setup.\n"
        output += f"Command to run manually:\n{' '.join(ssh_cmd)}\n"
        output += f"Then access via localhost:{local_port}\n"
        
        return output
        
    except Exception as e:
        return f"Error creating SSH tunnel: {e}"

@mcp.tool()
def ssh_key_info(key_file: str) -> str:
    """
    Get information about an SSH key file.
    
    Args:
        key_file: Path to SSH key file (public or private)
    
    Returns:
        SSH key information
    """
    if not os.path.exists(key_file):
        return f"Error: Key file not found: {key_file}"
    
    try:
        # Check if it's a public key
        if key_file.endswith('.pub') or 'id_rsa.pub' in key_file or 'id_ed25519.pub' in key_file:
            # Public key
            with open(key_file, 'r') as f:
                content = f.read().strip()
            
            parts = content.split()
            if len(parts) >= 2:
                key_type = parts[0]
                key_data = parts[1]
                comment = parts[2] if len(parts) > 2 else "No comment"
                
                output = f"SSH Public Key Information\n"
                output += f"{'='*35}\n"
                output += f"File: {key_file}\n"
                output += f"Type: {key_type}\n"
                output += f"Comment: {comment}\n"
                output += f"Key Length: {len(key_data)} characters\n"
                output += f"Fingerprint: [Use ssh-keygen -l -f {key_file}]\n"
                
                return output
            else:
                return "Error: Invalid public key format"
        
        else:
            # Try to get info about private key using ssh-keygen
            result = subprocess.run(
                ["ssh-keygen", "-l", "-f", key_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = f"SSH Private Key Information\n"
                output += f"{'='*35}\n"
                output += f"File: {key_file}\n"
                output += f"Fingerprint: {result.stdout.strip()}\n"
                
                # Check permissions
                stat = os.stat(key_file)
                perms = oct(stat.st_mode)[-3:]
                output += f"Permissions: {perms}\n"
                
                if perms != "600":
                    output += "⚠️  Warning: Private key should have 600 permissions\n"
                
                return output
            else:
                return f"Error reading key file: {result.stderr}"
    
    except Exception as e:
        return f"Error analyzing key file: {e}"

if __name__ == "__main__":
    import sys
    
    # Check if we should run in HTTP mode (for testing) or stdio mode (for Claude Desktop)
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # HTTP mode for testing
        import asyncio
        
        async def run_server():
            await mcp.run_http_async(host="127.0.0.1", port=8003)
        
        print("🚀 Starting SSH Server in HTTP mode on http://127.0.0.1:8003")
        print("Use --http flag to run in HTTP mode, otherwise runs in stdio mode for Claude Desktop")
        asyncio.run(run_server())
    else:
        # Stdio mode for Claude Desktop
        mcp.run()
