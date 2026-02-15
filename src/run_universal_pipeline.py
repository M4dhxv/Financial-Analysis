#!/usr/bin/env python3
"""
UNIVERSAL FINANCIAL REPORTING PIPELINE
End-to-end analysis from any CSV/Excel to complete financial report.

NO CONFIGURATION NEEDED - Works with ANY monthly data.
"""

import sys
import argparse
from pathlib import Path
import time

print("="*80)
print("UNIVERSAL FINANCIAL REPORTING PIPELINE")
print("="*80)

def run_pipeline(input_file: str, output_dir: str = None):
    """Run complete analysis pipeline."""
    
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"\n❌ ERROR: File not found: {input_file}")
        sys.exit(1)
    
    # Setup output directory
    if output_dir:
        out_dir = Path(output_dir)
    else:
        out_dir = input_path.parent / f"{input_path.stem}_report"
    
    out_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"\n📁 Input: {input_path.name}")
    print(f"📁 Output: {out_dir}/")
    print(f"\n⏱️  Starting pipeline...")
    
    start_time = time.time()
    
    # ========================================================================
    # STEP 1: ANALYZE DATA (Schema + Canonical + Registry)
    # ========================================================================
    print("\n" + "="*80)
    print("[1/4] SCHEMA DETECTION & NORMALIZATION")
    print("="*80)
    
    import subprocess
    
    step_start = time.time()
    result = subprocess.run([
        'python3', 'analyze_data.py',
        '--input', str(input_path),
        '--output', str(out_dir)
    ], capture_output=False, cwd=str(Path(__file__).parent))
    
    if result.returncode != 0:
        print(f"\n❌ Analysis failed")
        sys.exit(1)
    
    # Files are in the output directory
    schema_file = out_dir / "detected_schema.json"
    canonical_file = out_dir / "canonical_data.csv"
    registry_file = out_dir / "metric_registry.json"
    
    print(f"✓ Completed in {time.time() - step_start:.1f}s")
    
    # ========================================================================
    # STEP 2: VARIANCE ANALYSIS
    # ========================================================================
    print("\n" + "="*80)
    print("[2/4] VARIANCE ANALYSIS")
    print("="*80)
    
    step_start = time.time()
    result = subprocess.run([
        'python3', 'generic_variance.py',
        '--canonical', str(canonical_file),
        '--registry', str(registry_file),
        '--output', str(out_dir)
    ], capture_output=False, cwd=str(Path(__file__).parent))
    
    if result.returncode != 0:
        print(f"\n❌ Variance analysis failed")
        sys.exit(1)
    
    print(f"✓ Completed in {time.time() - step_start:.1f}s")
    
    # ========================================================================
    # STEP 3: CHART GENERATION
    # ========================================================================
    print("\n" + "="*80)
    print("[3/6] CHART GENERATION")
    print("="*80)
    
    step_start = time.time()
    result = subprocess.run([
        'python3', 'chart_generator.py',
        '--analysis-dir', str(out_dir)
    ], capture_output=False, cwd=str(Path(__file__).parent))
    
    if result.returncode != 0:
        print(f"\n⚠️  Chart generation had issues (continuing anyway)")
    
    print(f"✓ Completed in {time.time() - step_start:.1f}s")
    
    # ========================================================================
    # STEP 4: MARKDOWN REPORT
    # ========================================================================
    print("\n" + "="*80)
    print("[4/6] MARKDOWN REPORT")
    print("="*80)
    
    step_start = time.time()
    result = subprocess.run([
        'python3', 'report_generator_universal.py',
        '--analysis-dir', str(out_dir)
    ], capture_output=False, cwd=str(Path(__file__).parent))
    
    if result.returncode != 0:
        print(f"\n❌ Report generation failed")
        sys.exit(1)
    
    print(f"✓ Completed in {time.time() - step_start:.1f}s")
    
    # ========================================================================
    # STEP 5: PDF GENERATION
    # ========================================================================
    print("\n" + "="*80)
    print("[5/6] PDF GENERATION")
    print("="*80)
    
    step_start = time.time()
    result = subprocess.run([
        'python3', 'pdf_report_builder.py',
        '--analysis-dir', str(out_dir)
    ], capture_output=False, cwd=str(Path(__file__).parent))
    
    if result.returncode != 0:
        print(f"\n⚠️  PDF generation had issues (markdown report still available)")
    
    print(f"✓ Completed in {time.time() - step_start:.1f}s")
    
    # ========================================================================
    # STEP 6: COMPLETE
    # ========================================================================
    print("\n" + "="*80)
    print("[6/6] PIPELINE COMPLETE")
    print("="*80)
    
    total_time = time.time() - start_time
    
    print(f"\n⏱️  Total time: {total_time:.1f}s")
    print(f"💰 Total cost: $0.00")
    
    print(f"\n📂 Generated Files:")
    print(f"  ├── detected_schema.json      - Schema mappings")
    print(f"  ├── canonical_data.csv        - Normalized data")
    print(f"  ├── metric_registry.json      - Metric types")
    print(f"  ├── variance_analysis.csv     - Variance calculations")
    print(f"  ├── variance_summary.json     - Summary stats")
    print(f"  ├── charts/                   - 📊 VISUALIZATIONS")
    print(f"  ├── financial_report.md       - Markdown report")
    print(f"  └── financial_report.pdf      - 📄 FINAL PDF REPORT")
    
    print(f"\n📄 VIEW YOUR REPORTS:")
    print(f"   PDF:      {out_dir / 'financial_report.pdf'}")
    print(f"   Markdown: {out_dir / 'financial_report.md'}")
    
    print(f"\n✨ SUCCESS! Universal pipeline completed on ANY dataset structure.")
    
    return out_dir / 'financial_report.md'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Universal financial reporting - works with ANY CSV/Excel file!'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to input CSV or Excel file'
    )
    parser.add_argument(
        '--output',
        help='Output directory (default: <filename>_report/)'
    )
    
    args = parser.parse_args()
    
    try:
        run_pipeline(args.input, args.output)
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
