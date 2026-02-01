#!/usr/bin/env bash

CLIENT_NAME=$1
YEAR=$(date +%Y)

if [ -z "$CLIENT_NAME" ]; then
    echo "Usage: ./generate-license.sh [CLIENT_NAME]"
    exit 1
fi

# Convert name to uppercase and generate a clean key
CLEAN_NAME=$(echo $CLIENT_NAME | tr '[:lower:]' '[:upper:]' | tr -d ' ')
LICENSE_KEY="PV-$CLEAN_NAME-$YEAR-PRO"

echo "------------------------------------------------"
echo "PRIVATEVAULT LICENSE GENERATOR"
echo "------------------------------------------------"
echo "CLIENT: $CLIENT_NAME"
echo "KEY:    $LICENSE_KEY"
echo "------------------------------------------------"
echo "Instruction: Add this to the sidecar 'x-privatevault-license' header."
