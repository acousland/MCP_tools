#!/bin/bash
# Setup script for MCP Tools

echo "🔧 Setting up MCP Tools..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed"
    exit 1
fi

echo "✅ pip found"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt || pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

echo "✅ Python dependencies installed"

# Check if nmap is installed
if ! command -v nmap &> /dev/null; then
    echo "⚠️  nmap not found. Installing..."
    
    # Detect OS and install nmap
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install nmap
        else
            echo "❌ Homebrew not found. Please install nmap manually:"
            echo "   brew install nmap"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y nmap
        elif command -v yum &> /dev/null; then
            sudo yum install -y nmap
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y nmap
        else
            echo "❌ Package manager not found. Please install nmap manually"
            exit 1
        fi
    else
        echo "❌ Unsupported OS. Please install nmap manually"
        exit 1
    fi
else
    echo "✅ nmap found"
fi

# Make scripts executable
chmod +x main.py
chmod +x test_servers.py
chmod +x servers/file_server.py
chmod +x servers/nmap_server.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Usage:"
echo "  python3 main.py          - Start all servers interactively"
echo "  python3 main.py start    - Start all servers and wait"
echo "  python3 main.py check    - Check dependencies"
echo "  python3 test_servers.py  - Test server functionality"
echo ""
echo "Individual servers:"
echo "  python3 servers/file_server.py   - File server (port 8001)"
echo "  python3 servers/nmap_server.py   - NMAP server (port 8002)"
