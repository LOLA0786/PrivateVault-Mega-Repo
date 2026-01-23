#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# PrivateVault Production Test Runner
# - Creates venv
# - Installs deps
# - Runs critical/high pytest suite
# - Generates JUnit + HTML reports
# ==============================================================================

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

REPORT_DIR="${ROOT_DIR}/test_reports"
VENV_DIR="${ROOT_DIR}/.venv-tests"

PYTHON_BIN="${PYTHON_BIN:-python3}"
TEST_FILE="${TEST_FILE:-privatevault_comprehensive_test_suite.py}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 PrivateVault Production Test Runner"
echo "📁 Root: $ROOT_DIR"
echo "📄 Test file: $TEST_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Safety checks
if [[ ! -f "$TEST_FILE" ]]; then
  echo "❌ ERROR: Test file not found: $TEST_FILE" >&2
  exit 1
fi

mkdir -p "$REPORT_DIR"

# Create venv if missing
if [[ ! -d "$VENV_DIR" ]]; then
  echo "🔧 Creating virtual environment at: $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# Activate venv
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "🐍 Python: $(python --version)"
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip wheel setuptools >/dev/null

echo "📦 Installing test dependencies..."
python -m pip install -q \
  pytest \
  pytest-asyncio \
  pytest-html \
  psutil

# Timestamp for reports
TS="$(date +%Y%m%d_%H%M%S)"
JUNIT_XML="${REPORT_DIR}/junit_${TS}.xml"
HTML_REPORT="${REPORT_DIR}/report_${TS}.html"

echo
echo "🚀 Running production-grade tests (critical/high)..."
echo "   - JUnit: $JUNIT_XML"
echo "   - HTML : $HTML_REPORT"
echo

set +e
pytest \
  "$TEST_FILE" \
  -v \
  --tb=short \
  --color=yes \
  --junit-xml="$JUNIT_XML" \
  --html="$HTML_REPORT" \
  --self-contained-html \
  -m "critical or high"
EXIT_CODE=$?
set -e

echo
if [[ "$EXIT_CODE" -eq 0 ]]; then
  echo "✅ ALL TESTS PASSED"
  echo "📄 Reports saved in: $REPORT_DIR"
else
  echo "⚠️  SOME TESTS FAILED (exit code: $EXIT_CODE)"
  echo "📄 Reports saved in: $REPORT_DIR"
fi

exit "$EXIT_CODE"
