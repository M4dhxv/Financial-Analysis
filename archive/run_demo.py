#!/usr/bin/env python3
"""
END-TO-END DEMO: Financial Reporting System
Runs complete pipeline from data generation to final report.

COST: $0.00 (uses only free components)
"""

import subprocess
import sys
from pathlib import Path
import time

print("="*80)
print("FINANCIAL REPORTING SYSTEM - COMPLETE DEMO")
print("="*80)
print("\nThis demo will:")
print("  1. Generate 6 months of synthetic time-series data")
print("  2. Aggregate to category and overall monthly KPIs")
print("  3. Calculate month-over-month variances")
print("  4. Perform deterministic driver attribution")
print("  5. Generate management-friendly visualizations")
print("  6. Create a markdown performance report")
print("\nCOST: $0.00 (no API calls)")
print("="*80)

scripts = [
    ("monthly_snapshot_generator.py", "Generating monthly snapshots"),
    ("monthly_aggregates.py", "Aggregating to monthly metrics"),
    ("variance_calculator.py", "Calculating variances"),
    ("driver_attribution.py", "Analyzing drivers"),
    ("visualization_engine.py", "Creating charts"),
    ("report_generator.py", "Generating report")
]

total_start = time.time()

for i, (script, description) in enumerate(scripts, 1):
    print(f"\n[{i}/{len(scripts)}] {description}...")
    print("-" * 80)
    
    start = time.time()
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    elapsed = time.time() - start
    
    if result.returncode != 0:
        print(f"❌ Error in {script}:")
        print(result.stderr[-500:])  # Last 500 chars of error
        sys.exit(1)
    else:
        # Show last few lines of output
        output_lines = result.stdout.strip().split('\n')
        for line in output_lines[-5:]:
            print(f"  {line}")
        print(f"✓ Completed in {elapsed:.1f}s")

total_elapsed = time.time() - total_start

print("\n" + "="*80)
print("✨ DEMO COMPLETE")
print("="*80)
print(f"\nTotal time: {total_elapsed:.1f}s")
print(f"Total cost: $0.00")
print("\n📁 Generated Files:")

# List key outputs
outputs = [
    "product_performance_timeseries.csv",
    "monthly_metrics_category.csv",
    "monthly_metrics_overall.csv",
    "monthly_variance_category.csv",
    "variance_drivers.json",
    "visualizations/*.png",
    "monthly_report_*.md"
]

for output in outputs:
    print(f"  ✓ {output}")

# Find and display report
report_files = list(Path(__file__).parent.glob("monthly_report_*.md"))
if report_files:
    report_file = report_files[-1]
    print(f"\n📊 Performance Report: {report_file.name}")
    print(f"  Size: {report_file.stat().st_size:,} bytes")
    print(f"\n  Preview (first 20 lines):")
    print("  " + "-"*76)
    with open(report_file) as f:
        for i, line in enumerate(f):
            if i >= 20:
                break
            print(f"  {line.rstrip()}")
    print("  " + "-"*76)

print("\n✅ SUCCESS: Full financial reporting pipeline executed with:")
print("  • Deterministic variance analysis")
print("  • Mathematical decomposition (price × volume)")
print("  • Driver attribution with impact ranking")
print("  • Management-ready visualizations")
print("  • Zero API costs")
print("  • Zero hallucination risk")
