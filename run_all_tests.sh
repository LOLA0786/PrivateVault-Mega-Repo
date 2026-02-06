#!/usr/bin/env bash
set +e

echo "======================================"
echo " PrivateVault Full Test Diagnostic Run "
echo "======================================"

TS=$(date +"%Y%m%d_%H%M%S")
OUTDIR="test_diagnostics_$TS"

mkdir -p "$OUTDIR"

echo "[1/4] Environment Info..."
python --version > "$OUTDIR/env.txt"
pip freeze >> "$OUTDIR/env.txt"

echo "[2/4] Cleaning cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
rm -rf .pytest_cache 2>/dev/null || true

echo "[3/4] Running Pytest..."
pytest -vv \
  --tb=long \
  --maxfail=50 \
  --durations=20 \
  --junitxml="$OUTDIR/pytest.xml" \
  > "$OUTDIR/pytest.log" 2>&1 || true

echo "[4/4] Running Shell/Integration Tests..."

for f in test-*.sh run_*test*.sh *_test.sh; do
  if [ -f "$f" ]; then
    echo "Running $f" | tee -a "$OUTDIR/shell.log"
    bash "$f" >> "$OUTDIR/shell.log" 2>&1 || true
  fi
done

echo "======================================"
echo " Diagnostics saved in: $OUTDIR"
echo "======================================"

echo "Files:"
ls -lh "$OUTDIR"
