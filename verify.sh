#!/bin/bash
export $(grep -v '^#' sovereign.env | xargs)
echo "🧪 Running Integration Test..."
python3 sovereign_final_test.py
echo ""
echo "📋 Generating Integrity Report..."
python3 audit_viewer.py
