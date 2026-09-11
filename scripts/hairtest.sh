#!/bin/sh
# Rebuild the hair-fit contact sheet. Usage: sh scripts/hairtest.sh <out.png> [angle]
set -e
OUT=${1:-preview/hairfit.png}
ANG=${2:-1.0}
rm -rf preview/hairtest && mkdir -p preview/hairtest
python3 - <<'EOF'
import sys; sys.path.insert(0, 'scripts')
from compose import base_rig_mesh, export
from accessories import fit_hair, fit_glasses
from catalog import HAIR
for i, (k, o) in enumerate(HAIR.items()):
    export([base_rig_mesh(), fit_hair(k, color="#3B2418", **o)] + fit_glasses(),
           f"preview/hairtest/{i:02d}_{k}.glb")
print(len(HAIR), "built")
EOF
timeout 600 python3 scripts/contact_sheet.py 'preview/hairtest/*.glb' "$OUT" "$ANG" --head 2>&1 | grep -v 'GET\|404' | tail -1
