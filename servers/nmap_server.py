#!/usr/bin/env python3
"""
NMAP Server - MCP server for running NMAP commands and network scanning.
Provides tools to execute NMAP scans and basic network operations.
"""

import asyncio
import subprocess
import json
import re
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("NMAP Server")

def _run_command(command: List[str], timeout: int = 30) -> Dict[str, Any]:
    """
    Run a shell command safely and return the result.
    
    Args:
        command: List of command parts
        timeout: Timeout in seconds
    
    Returns:
        Dictionary with command result
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Command execution failed: {e}"
        }

@mcp.tool()
def nmap_scan(target: str, scan_type: str = "basic", ports: str = "", options: str = "") -> str:
    """
    Perform an NMAP scan on the specified target.
    
    Args:
        target: Target host or network (e.g., "192.168.1.1" or "192.168.1.0/24")
        scan_type: Type of scan - "basic", "syn", "udp", "tcp", "ping", "os", "service"
        ports: Specific ports to scan (e.g., "22,80,443" or "1-1000")
        options: Additional NMAP options
    
    Returns:
        NMAP scan results
    """
    # Validate target (basic validation)
    if not target or len(target) > 100:
        return "Error: Invalid target specified"
    
    # Build NMAP command
    nmap_cmd = ["nmap"]
    
    # Add scan type options
    if scan_type == "basic":
        pass  # Default scan
    elif scan_type == "syn":
        nmap_cmd.append("-sS")
    elif scan_type == "udp":
        nmap_cmd.append("-sU")
    elif scan_type == "tcp":
        nmap_cmd.append("-sT")
    elif scan_type == "ping":
        nmap_cmd.extend(["-sn"])
    elif scan_type == "os":
        nmap_cmd.extend(["-O"])
    elif scan_type == "service":
        nmap_cmd.extend(["-sV"])
    else:
        return f"Error: Unknown scan type '{scan_type}'"
    
    # Add port specification
    if ports:
        nmap_cmd.extend(["-p", ports])
    
    # Add additional options (be careful with this in production)
    if options:
        # Basic sanitization - remove dangerous characters
        safe_options = re.sub(r'[;&|`$]', '', options)
        if safe_options != options:
            return "Error: Invalid characters in options"
        nmap_cmd.extend(safe_options.split())
    
    # Add target
    nmap_cmd.append(target)
    
    # Execute command
    result = _run_command(nmap_cmd, timeout=120)  # 2 minute timeout
    
    if not result["success"]:
        return f"Error: {result.get('error', 'Unknown error')}"
    
    if result["returncode"] != 0:
        return f"NMAP Error: {result['stderr']}"
    
    # Format output
    output = f"NMAP Scan Results for {target}\n"
    output += f"{'='*50}\n"
    output += f"Command: {' '.join(nmap_cmd)}\n"
    output += f"{'='*50}\n"
    output += result["stdout"]
    
    return output

@mcp.tool()
def ping_host(host: str, count: int = 4, timeout: int = 5) -> str:
    """
    Ping a host to check connectivity.
    
    Args:
        host: Hostname or IP address to ping
        count: Number of ping packets to send
        timeout: Timeout for each ping in seconds
    
    Returns:
        Ping results
    """
    # Validate inputs
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    if count < 1 or count > 10:
        return "Error: Count must be between 1 and 10"
    
    if timeout < 1 or timeout > 30:
        return "Error: Timeout must be between 1 and 30 seconds"
    
    # Build ping command (macOS/Linux compatible)
    ping_cmd = ["ping", "-c", str(count), "-W", str(timeout * 1000), host]
    
    # Execute command
    result = _run_command(ping_cmd, timeout=(timeout * count + 10))
    
    if not result["success"]:
        return f"Error: {result.get('error', 'Unknown error')}"
    
    # Format output
    output = f"Ping Results for {host}\n"
    output += f"{'='*30}\n"
    output += result["stdout"]
    
    if result["stderr"]:
        output += f"\nErrors/Warnings:\n{result['stderr']}"
    
    return output

@mcp.tool()
def port_scan(host: str, ports: str = "1-1000", scan_type: str = "tcp") -> str:
    """
    Scan specific ports on a host.
    
    Args:
        host: Target host
        ports: Port range (e.g., "1-1000", "22,80,443")
        scan_type: Type of scan ("tcp", "udp", "syn")
    
    Returns:
        Port scan results
    """
    # Validate host
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    # Build NMAP command for port scanning
    nmap_cmd = ["nmap", "-Pn"]  # Skip ping, just scan ports
    
    if scan_type == "tcp":
        nmap_cmd.append("-sT")
    elif scan_type == "udp":
        nmap_cmd.append("-sU")
    elif scan_type == "syn":
        nmap_cmd.append("-sS")
    else:
        return f"Error: Invalid scan type '{scan_type}'"
    
    nmap_cmd.extend(["-p", ports, host])
    
    # Execute command
    result = _run_command(nmap_cmd, timeout=300)  # 5 minute timeout for port scans
    
    if not result["success"]:
        return f"Error: {result.get('error', 'Unknown error')}"
    
    # Format output
    output = f"Port Scan Results for {host}\n"
    output += f"Ports: {ports} | Type: {scan_type}\n"
    output += f"{'='*50}\n"
    output += result["stdout"]
    
    if result["stderr"]:
        output += f"\nWarnings:\n{result['stderr']}"
    
    return output

@mcp.tool()
def network_discovery(network: str = "192.168.1.0/24") -> str:
    """
    Discover active hosts on a network.
    
    Args:
        network: Network to scan (CIDR notation, e.g., "192.168.1.0/24")
    
    Returns:
        List of discovered hosts
    """
    # Validate network format (basic)
    if not network or "/" not in network:
        return "Error: Invalid network format. Use CIDR notation (e.g., 192.168.1.0/24)"
    
    # Build NMAP ping scan command
    nmap_cmd = ["nmap", "-sn", network]
    
    # Execute command
    result = _run_command(nmap_cmd, timeout=60)
    
    if not result["success"]:
        return f"Error: {result.get('error', 'Unknown error')}"
    
    # Format output
    output = f"Network Discovery for {network}\n"
    output += f"{'='*40}\n"
    output += result["stdout"]
    
    return output

if __name__ == "__main__":
    import sys
    
    # Check if we should run in HTTP mode (for testing) or stdio mode (for Claude Desktop)
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # HTTP mode for testing
        import asyncio
        
        async def run_server():
            await mcp.run_http_async(host="127.0.0.1", port=8002)
        
        print("🚀 Starting NMAP Server in HTTP mode on http://127.0.0.1:8002")
        print("Use --http flag to run in HTTP mode, otherwise runs in stdio mode for Claude Desktop")
        asyncio.run(run_server())
    else:
        # Stdio mode for Claude Desktop
        mcp.run()
