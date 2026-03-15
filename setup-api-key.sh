#!/bin/bash

echo "🔑 Setting up Gemini API Key for Demo"
echo "====================================="

echo "Please enter your Gemini API key:"
read -s GEMINI_API_KEY

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ No API key provided. Exiting."
    exit 1
fi

echo "✅ API key received. Setting up environment..."

# Set for current session
export GEMINI_API_KEY="$GEMINI_API_KEY"

echo "🚀 Running demo with your API key..."
python simple-free-demo.py

