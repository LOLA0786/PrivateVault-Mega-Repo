#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Usage: ./verify-evidence.sh <receipt.json>"
  exit 1
fi

echo "Verifying receipt: $1"

docker run --rm \
  -v $(pwd):/data \
  privatevault:pilot-v1 \
  verify /data/$1

echo "Verification completed."
