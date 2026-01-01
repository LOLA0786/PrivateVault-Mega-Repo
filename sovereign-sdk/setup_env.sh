#!/bin/bash
echo "🛡️ Setting up Sovereign SDK Environment..."
pip install fastapi uvicorn httpx pydantic
echo "✅ Dependencies installed."
echo "🚀 To start the Conscience: python3 src/uaal/api.py"
echo "🚀 To start the Muscle: python3 src/oaas/api.py"
