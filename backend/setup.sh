#!/bin/bash

# FermTrack Backend Quick Setup Script
# This script automates the setup process for the FermTrack backend

set -e  # Exit on any error

echo "🚀 FermTrack Backend Quick Setup"
echo "=================================="
echo

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "✅ Python 3 detected: $(python3 --version)"

# Navigate to backend directory
cd "$(dirname "$0")"

# Run the Python initialization script
echo "🔧 Running initialization script..."
python3 init.py

# Check if initialization was successful
if [ $? -eq 0 ]; then
    echo
    echo "🎉 Setup completed successfully!"
    echo
    echo "To start the server:"
    echo "  1. Activate virtual environment: source venv/bin/activate"
    echo "  2. Run the server: python app.py"
    echo "  3. Test the API: python test_api.py"
    echo
    echo "The API will be available at http://localhost:5000"
else
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi