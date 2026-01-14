#!/bin/bash
# Run all tests

set -e

echo "Running all tests..."

# Unit tests
echo ""
echo "1. Running unit tests..."
pytest tests/unit/ -v --cov=. --cov-report=term-missing

# Integration tests
echo ""
echo "2. Running integration tests..."
pytest tests/integration/ -v --timeout=300

# Generate coverage report
echo ""
echo "3. Generating coverage report..."
coverage html
echo "Coverage report: htmlcov/index.html"

echo ""
echo "✅ All tests passed!"
