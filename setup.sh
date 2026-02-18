#!/bin/bash

echo "=========================================="
echo "🕵️  hrunxtnshn Setup"
echo "Invisible LinkedIn Extraction System"
echo "=========================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip3 found"
echo

# Navigate to orchestrator directory
cd orchestrator || exit 1

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo

# Install Playwright browsers
echo "🌐 Installing Playwright Chromium..."
playwright install chromium

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Playwright browsers"
    exit 1
fi

echo "✅ Playwright Chromium installed"
echo

# Make CLI executable
chmod +x cli_extractor.py

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo
echo "Next steps:"
echo
echo "1. Login to LinkedIn (one-time):"
echo "   cd orchestrator"
echo "   python3 cli_extractor.py login"
echo
echo "2. Extract employees (invisible):"
echo "   python3 cli_extractor.py extract \"Company Name\""
echo
echo "=========================================="
