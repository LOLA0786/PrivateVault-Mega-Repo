#!/bin/bash
export $(grep -v '^#' sovereign.env | xargs)
python3 sovereign_final_test.py
python3 audit_viewer.py
