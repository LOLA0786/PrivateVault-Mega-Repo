#!/bin/bash

cd /home/ubuntu/PrivateVault-Mega-Repo || exit 1

exec /home/ubuntu/.local/bin/gunicorn services.api.app:app \
  -k uvicorn.workers.UvicornWorker \
  --workers 1 \
  --bind 127.0.0.1:8000 \
  --timeout 120 \
  --log-level debug \
  --access-logfile - \
  --error-logfile -
