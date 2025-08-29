#!/usr/bin/env python3
"""
Network Interfaces Server - MCP server for network interface information.
Provides tools to get network interface details and statistics.
"""

import psutil
import json
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Network Interfaces Server")

@mcp.tool()
def get_network_interfaces() -> str:
    """
    Get information about all network interfaces on the system.
    
    Returns:
        Detailed information about network interfaces including addresses, netmasks, and broadcast addresses
    """
    try:
        interfaces = psutil.net_if_addrs()
        result = {}
        
        for interface_name, addresses in interfaces.items():
            result[interface_name] = []
            for address in addresses:
                addr_info = {
                    "family": str(address.family),
                    "address": address.address,
                    "netmask": address.netmask,
                    "broadcast": address.broadcast
                }
                if hasattr(address, 'ptp'):
                    addr_info["ptp"] = address.ptp
                result[interface_name].append(addr_info)
        
        # Format output nicely
        output = "Network Interfaces\n"
        output += "=" * 50 + "\n"
        
        for interface_name, addresses in result.items():
            output += f"\nInterface: {interface_name}\n"
            output += "-" * 30 + "\n"
            
            for i, addr in enumerate(addresses, 1):
                output += f"  Address {i}:\n"
                output += f"    Family: {addr['family']}\n"
                output += f"    Address: {addr['address']}\n"
                if addr['netmask']:
                    output += f"    Netmask: {addr['netmask']}\n"
                if addr['broadcast']:
                    output += f"    Broadcast: {addr['broadcast']}\n"
                if addr.get('ptp'):
                    output += f"    PTP: {addr['ptp']}\n"
                output += "\n"
        
        return output
        
    except Exception as e:
        return f"Error getting network interfaces: {e}"

@mcp.tool()
def get_network_stats() -> str:
    """
    Get network interface statistics including bytes sent/received and packet counts.
    
    Returns:
        Network statistics for all interfaces
    """
    try:
        stats = psutil.net_io_counters(pernic=True)
        
        output = "Network Interface Statistics\n"
        output += "=" * 50 + "\n"
        
        for interface_name, stat in stats.items():
            output += f"\nInterface: {interface_name}\n"
            output += "-" * 30 + "\n"
            output += f"  Bytes Sent: {stat.bytes_sent:,}\n"
            output += f"  Bytes Received: {stat.bytes_recv:,}\n"
            output += f"  Packets Sent: {stat.packets_sent:,}\n"
            output += f"  Packets Received: {stat.packets_recv:,}\n"
            output += f"  Errors In: {stat.errin:,}\n"
            output += f"  Errors Out: {stat.errout:,}\n"
            output += f"  Drops In: {stat.dropin:,}\n"
            output += f"  Drops Out: {stat.dropout:,}\n"
        
        return output
        
    except Exception as e:
        return f"Error getting network statistics: {e}"

@mcp.tool()
def get_interface_status() -> str:
    """
    Get the status (up/down) of all network interfaces.
    
    Returns:
        Status information for all network interfaces
    """
    try:
        stats = psutil.net_if_stats()
        
        output = "Network Interface Status\n"
        output += "=" * 50 + "\n"
        
        for interface_name, stat in stats.items():
            status = "UP" if stat.isup else "DOWN"
            duplex_map = {1: "HALF", 2: "FULL", 0: "UNKNOWN"}
            duplex = duplex_map.get(stat.duplex, "UNKNOWN")
            
            output += f"\nInterface: {interface_name}\n"
            output += "-" * 30 + "\n"
            output += f"  Status: {status}\n"
            output += f"  Speed: {stat.speed} Mbps\n"
            output += f"  Duplex: {duplex}\n"
            output += f"  MTU: {stat.mtu}\n"
        
        return output
        
    except Exception as e:
        return f"Error getting interface status: {e}"

if __name__ == "__main__":
    import sys
    
    # Check if we should run in HTTP mode (for testing) or stdio mode (for Claude Desktop)
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # HTTP mode for testing
        import asyncio
        
        async def run_server():
            await mcp.run_http_async(host="127.0.0.1", port=8004)
        
        print("🚀 Starting Network Interfaces Server in HTTP mode on http://127.0.0.1:8004")
        print("Use --http flag to run in HTTP mode, otherwise runs in stdio mode for Claude Desktop")
        asyncio.run(run_server())
    else:
        # Stdio mode for Claude Desktop
        mcp.run()
