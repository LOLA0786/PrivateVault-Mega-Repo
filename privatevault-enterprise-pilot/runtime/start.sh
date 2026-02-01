#!/bin/bash
source sovereign.env
kill -9 $(lsof -ti:8000,8001) 2>/dev/null
python3 -m uvicorn uaal_fastapi:app --port 8000 --log-level error &
python3 -m uvicorn governed_gateway:app --port 8001 --log-level error &
echo "🚀 GALANI PROTOCOL ONLINE"
