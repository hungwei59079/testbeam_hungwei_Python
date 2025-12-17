#!/bin/bash
set -e

echo "[$(date)] Starting on $(hostname)"

# 1. Setup CMSSW environment
cd /afs/cern.ch/user/h/hungwei/CMSSW_16_0_0_pre1/src
eval "$(scramv1 runtime -sh)"

# 2. Go to job working directory
cd /afs/cern.ch/user/h/hungwei/testbeam_hungwei_Python/TB2025Analysis

# 3. Run analyzer
python3 Analyzer.py \
  --infile configs/SpecAlignment.json \
  --modules alignment \
  --outdir ./

echo "[$(date)] Done."

