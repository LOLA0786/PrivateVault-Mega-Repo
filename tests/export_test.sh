#!/usr/bin/env bash

ID=$(curl -s http://localhost:8000/latest | jq -r .run_id)

curl -s http://localhost:8000/export?id=$ID \
  -o logs/$ID.json

echo "Evidence saved: logs/$ID.json"
