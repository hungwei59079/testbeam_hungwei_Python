#!/bin/bash
# Wrapper to run the inspector inside CMSSW environment

echo "[$(date)] Starting on $(hostname)"
echo "Running event inspection: file=$1, start=$2, end=$3"

# 1. Setup CMSSW environment
cd ~/CMSSW_16_0_0_pre1/src       # <-- modify to your CMSSW directory
eval `scramv1 runtime -sh`

# 2. Go back to working directory
cd $PWD/$(dirname "$0")          # Condor job directory (optional sanity check)

# 3. Run the Python script
python3 hit_inspector.py "$1" "$2" "$3"

echo "[$(date)] Done."
