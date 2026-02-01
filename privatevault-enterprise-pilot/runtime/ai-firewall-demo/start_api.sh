#!/bin/bash
# Start AI Firewall API

echo "🔥 Starting AI Firewall API..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found, copying from .env.example"
    cp .env.example .env
    echo "📝 Please edit .env and set your API_KEY and SECRET_KEY"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Start API
echo "🚀 Starting Flask API on port 5000..."
python api.py
