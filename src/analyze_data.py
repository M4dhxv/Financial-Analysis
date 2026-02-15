#!/usr/bin/env python3
"""
SCHEMA-AGNOSTIC ANALYZER - Command Line Interface
Process any CSV/Excel file through schema detection and analysis.

Usage:
    python3 analyze_data.py --input your_file.csv
    python3 analyze_data.py --input your_file.xlsx --output analysis_results/
"""

import argparse
import sys
from pathlib import Path
import json

# Import our new modules
from input_adapter import load_and_detect, save_schema_map
from canonical_format import CanonicalConverter, save_canonical
from metric_registry import MetricClassifier, save_registry

print("="*80)
print("SCHEMA-AGNOSTIC DATA ANALYZER")
print("="*80)

def analyze_file(input_path: str, output_dir: str = None):
    """
    Analyze any CSV/Excel file end-to-end.
    
    Steps:
    1. Detect schema (column types)
    2. Convert to canonical format
    3. Classify metrics
    4. Generate summary report
    """
    
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"\n❌ Error: File not found: {input_path}")
        sys.exit(1)
    
    # Setup output directory
    if output_dir:
        out_dir = Path(output_dir)
    else:
        out_dir = input_file.parent / f"{input_file.stem}_analysis"
    
    out_dir.mkdir(exist_ok=True, parents=True)
    print(f"\n📁 Output directory: {out_dir}")
    
    # ========================================================================
    # STEP 1: SCHEMA DETECTION
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 1: SCHEMA DETECTION")
    print("="*80)
    
    df, schema_map = load_and_detect(str(input_file))
    
    # Save schema
    schema_file = out_dir / "detected_schema.json"
    save_schema_map(schema_map, str(schema_file))
    
    # ========================================================================
    # STEP 2: CANONICAL CONVERSION
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 2: CANONICAL CONVERSION")
    print("="*80)
    
    converter = CanonicalConverter(df, schema_map)
    df_canonical = converter.to_canonical()
    
    # Save canonical data
    canonical_file = out_dir / "canonical_data.csv"
    save_canonical(df_canonical, str(canonical_file))
    
    # ========================================================================
    # STEP 3: METRIC CLASSIFICATION
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 3: METRIC CLASSIFICATION")
    print("="*80)
    
    metric_names = df_canonical['metric_name'].unique().tolist()
    classifier = MetricClassifier(metric_names)
    registry = classifier.build_registry()
    
    # Save registry
    registry_file = out_dir / "metric_registry.json"
    save_registry(registry, str(registry_file))
    
    # ========================================================================
    # STEP 4: GENERATE SUMMARY REPORT
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 4: SUMMARY REPORT")
    print("="*80)
    
    summary = {
        'input_file': str(input_file.name),
        'rows_analyzed': len(df),
        'columns_analyzed': len(df.columns),
        'schema': {
            'time_column': schema_map['time_column'],
            'entity_columns': schema_map['entity_columns'],
            'measure_columns': schema_map['measure_columns']
        },
        'canonical_format': {
            'total_rows': len(df_canonical),
            'unique_periods': df_canonical['period'].nunique(),
            'unique_entities': df_canonical['entity'].nunique(),
            'unique_metrics': df_canonical['metric_name'].nunique()
        },
        'metrics': {
            'total': len(registry),
            'by_type': {},
            'decomposable': [m['name'] for m in registry.values() if m['is_decomposable']],
            'priority_metrics': sorted(
                [m for m in registry.values() if m['analysis_priority'] <= 2],
                key=lambda x: x['analysis_priority']
            )
        }
    }
    
    # Count by type
    for metric in registry.values():
        mtype = metric['type']
        summary['metrics']['by_type'][mtype] = summary['metrics']['by_type'].get(mtype, 0) + 1
    
    # Save summary
    summary_file = out_dir / "analysis_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Analysis Summary:")
    print(f"  Input: {summary['input_file']}")
    print(f"  Rows: {summary['rows_analyzed']:,}")
    print(f"  Columns: {summary['columns_analyzed']}")
    print(f"\n  Schema Detected:")
    print(f"    Time column: {summary['schema']['time_column']}")
    print(f"    Entity columns: {len(summary['schema']['entity_columns'])}")
    print(f"    Measure columns: {len(summary['schema']['measure_columns'])}")
    print(f"\n  Canonical Format:")
    print(f"    Total rows: {summary['canonical_format']['total_rows']:,}")
    print(f"    Periods: {summary['canonical_format']['unique_periods']}")
    print(f"    Entities: {summary['canonical_format']['unique_entities']:,}")
    print(f"    Metrics: {summary['canonical_format']['unique_metrics']}")
    print(f"\n  Metric Classification:")
    for mtype, count in summary['metrics']['by_type'].items():
        print(f"    {mtype}: {count}")
    
    if summary['metrics']['decomposable']:
        print(f"\n  Decomposable Metrics (price × volume):")
        for m in summary['metrics']['decomposable']:
            print(f"    - {m}")
    
    if summary['metrics']['priority_metrics']:
        print(f"\n  High-Priority Metrics (for variance analysis):")
        for m in summary['metrics']['priority_metrics'][:5]:
            print(f"    - {m['name']} ({m['type']})")
    
    # ========================================================================
    # FINAL OUTPUT
    # ========================================================================
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)
    print(f"\n📂 Output Files:")
    print(f"  ├── detected_schema.json     - Column type mappings")
    print(f"  ├── canonical_data.csv       - Normalized long-format data")
    print(f"  ├── metric_registry.json     - Metric classifications")
    print(f"  └── analysis_summary.json    - Overall summary")
    print(f"\n📁 All files saved to: {out_dir}/")
    
    print(f"\n🎯 Next Steps:")
    print(f"  1. Review detected_schema.json to verify column detection")
    print(f"  2. Check metric_registry.json to see metric types")
    print(f"  3. Use canonical_data.csv for variance analysis")
    print(f"  4. Run variance analysis (coming in Phase 2)")
    
    print(f"\n💰 Cost: $0.00 (no API calls)")
    
    return out_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Analyze any CSV/Excel file with automatic schema detection'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to input CSV or Excel file'
    )
    parser.add_argument(
        '--output',
        help='Output directory (default: <filename>_analysis/)'
    )
    
    args = parser.parse_args()
    
    try:
        output_dir = analyze_file(args.input, args.output)
        print(f"\n✨ SUCCESS! Analysis complete.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
