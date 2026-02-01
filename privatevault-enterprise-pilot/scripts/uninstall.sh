#!/bin/bash
set -e

echo "Removing PrivateVault Pilot..."

kubectl delete namespace pv-pilot --ignore-not-found=true

echo "Cleanup complete."
