#!/bin/bash

echo "Setting up JobGenie ML Engine..."

# Check if Python is installed
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null
then
    echo "Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Use python3 if available, otherwise use python
PYTHON_CMD="python"
if command -v python3 &> /dev/null
then
    PYTHON_CMD="python3"
fi

echo "Using Python command: $PYTHON_CMD"

# Create virtual environment
echo "Creating virtual environment..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To run the ML engine:"
echo "1. Activate the virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   source venv/Scripts/activate"
else
    echo "   source venv/bin/activate"
fi
echo "2. Run the ML engine:"
echo "   python match_jobs.py"
echo ""
echo "The ML engine will be available at http://localhost:5000"
