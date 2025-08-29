#!/usr/bin/env python3
"""
Simple test of FastMCP functionality
"""

from fastmcp import FastMCP
import os

# Create MCP server
mcp = FastMCP("Test Server")

@mcp.tool()
def hello_world() -> str:
    """Simple hello world test."""
    return "Hello from FastMCP!"

@mcp.tool()
def list_files(directory: str = ".") -> str:
    """List files in a directory."""
    try:
        files = os.listdir(directory)
        return f"Files in {directory}: {', '.join(files[:10])}"  # Limit to first 10
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("🧪 Testing FastMCP Server")
    print("Tools available:")
    for tool_name in ["hello_world", "list_files"]:
        print(f"  - {tool_name}")
    
    print("\n🚀 Starting HTTP server on port 8001...")
    print("Server will run until interrupted with Ctrl+C")
    import asyncio
    
    async def run_server():
        await mcp.run_http_async(host="127.0.0.1", port=8001)
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\n✅ Server stopped")
