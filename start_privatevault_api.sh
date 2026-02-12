#!/bin/bash

cd /home/galanichandan/PrivateVault-Mega-Repo

source venv/bin/activate || true

exec gunicorn services.api.app:app \
  -k uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 127.0.0.1:8000 \
  --timeout 120
