#!/bin/bash

mkdir -p compliance_reports

pytest tests \
  --junitxml=compliance_reports/tests.xml \
  --html=compliance_reports/report.html \
  --self-contained-html

date > compliance_reports/run_date.txt
git rev-parse HEAD > compliance_reports/commit.txt
