#!/bin/bash

# FermTrack Frontend Quick Start Script
# This script starts the frontend development server

set -e

echo "🚀 Starting FermTrack Frontend..."
echo

# Check if we're in the right directory
if [ ! -f "index.html" ]; then
    echo "❌ index.html not found. Please run this script from the frontend directory."
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✅ Python 3 detected: $(python3 --version)"
echo

# Start the server
echo "🌐 Starting frontend server..."
echo "💡 Make sure the backend is running at http://localhost:5000"
echo

python3 serve.py