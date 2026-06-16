"""
Convenience runner: executes Bronze -> Silver -> Gold in sequence.
Run:  python run_pipeline.py  (from cloud-bi/)

Set PYTHONUTF8=1 environment variable on Windows to avoid encoding errors:
  Windows CMD:  set PYTHONUTF8=1 && python run_pipeline.py
  PowerShell:   $env:PYTHONUTF8=1; python run_pipeline.py
"""
import sys
import os

# Force UTF-8 on Windows
os.environ.setdefault("PYTHONUTF8", "1")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

print("=== SKYLearn IQ — Medallion Pipeline ===\n")

print("--- Step 1: Bronze (raw extract from SQLite) ---")
from export.bronze_export import export_bronze
export_bronze()

print("\n--- Step 2: Silver (cleaned + enriched joins) ---")
from transform.silver import build_silver
build_silver()

print("\n--- Step 3: Gold (analytical aggregates) ---")
from transform.gold import build_gold
build_gold()

print("\n=== Pipeline complete. Run 'streamlit run main.py' to open the dashboard. ===")
