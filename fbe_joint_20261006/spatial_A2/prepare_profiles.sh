#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p profiles checks
tdx -b -tcl create_profiles.tcl > checks/tdx_profiles.log 2>&1
cat checks/tdx_profiles.log
svisual -b verify_profiles.tcl > checks/svisual_profiles.log 2>&1 < /dev/null
echo 'Generation cutlines saved; inspect before any A2 device simulation'
