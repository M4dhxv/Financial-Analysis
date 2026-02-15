#!/usr/bin/env python3
"""
UNIVERSAL REPORT GENERATOR
Creates comprehensive financial reports from variance analysis results.

Works with ANY dataset - completely schema-agnostic.
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

print("="*80)
print("UNIVERSAL REPORT GENERATOR")
print("="*80)

def load_analysis_data(analysis_dir: Path) -> Dict:
    """Load all analysis outputs."""
    
    data = {}
    
    # Load schema
    schema_file = analysis_dir / "detected_schema.json"
    if schema_file.exists():
        with open(schema_file, 'r') as f:
            data['schema'] = json.load(f)
    
    # Load metric registry
    registry_file = analysis_dir / "metric_registry.json"
    if registry_file.exists():
        with open(registry_file, 'r') as f:
            data['registry'] = json.load(f)
    
    # Load variance analysis
    variance_file = analysis_dir / "variance_analysis.csv"
    if variance_file.exists():
        data['variance'] = pd.read_csv(variance_file)
    
    # Load variance summary
    summary_file = analysis_dir / "variance_summary.json"
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            data['summary'] = json.load(f)
    
    # Load canonical data for trends
    canonical_file = analysis_dir / "canonical_data.csv"
    if canonical_file.exists():
        # Sample for performance
        data['canonical'] = pd.read_csv(canonical_file, nrows=50000)
    
    return data


def generate_executive_summary(data: Dict) -> str:
    """Generate executive summary section."""
    
    summary = data.get('summary', {})
    variance_df = data.get('variance')
    
    report = "# Financial Analysis Report\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
    report += f"**Analysis Period:** {summary.get('latest_period', 'N/A')}  \n\n"
    report += "---\n\n"
    
    report += "## Executive Summary\n\n"
    
    if variance_df is not None and len(variance_df) > 0:
        latest_period = variance_df['current_period'].max()
        latest_data = variance_df[variance_df['current_period'] == latest_period]
        
        # Overall statistics
        total_records = len(latest_data)
        entities_count = latest_data['entity'].nunique()
        metrics_count = latest_data['metric_name'].nunique()
        
        report += f"**Records Analyzed:** {total_records:,}  \n"
        report += f"**Entities:** {entities_count:,}  \n"
        report += f"**Metrics:** {metrics_count}  \n\n"
        
        # Top movers
        report += "### Top Changes\n\n"
        
        top_increases = latest_data.nlargest(5, 'delta_absolute')
        top_decreases = latest_data.nsmallest(5, 'delta_absolute')
        
        report += "**Largest Increases:**\n\n"
        for _, row in top_increases.iterrows():
            entity_short = str(row['entity'])[:50] + "..." if len(str(row['entity'])) > 50 else str(row['entity'])
            report += f"- **{row['metric_name']}** in {entity_short}: "
            report += f"+{row['delta_absolute']:.2f} ({row['delta_percentage']:.1f}%)  \n"
        
        report += "\n**Largest Decreases:**\n\n"
        for _, row in top_decreases.iterrows():
            entity_short = str(row['entity'])[:50] + "..." if len(str(row['entity'])) > 50 else str(row['entity'])
            report += f"- **{row['metric_name']}** in {entity_short}: "
            report += f"{row['delta_absolute']:.2f} ({row['delta_percentage']:.1f}%)  \n"
    
    report += "\n---\n\n"
    
    return report


def generate_metric_analysis(data: Dict) -> str:
    """Generate per-metric analysis section."""
    
    variance_df = data.get('variance')
    registry = data.get('registry', {})
    
    if variance_df is None:
        return ""
    
    report = "## Metric Analysis\n\n"
    
    # Get latest period
    latest_period = variance_df['current_period'].max()
    latest_data = variance_df[variance_df['current_period'] == latest_period]
    
    # Analyze each metric
    for metric_name in latest_data['metric_name'].unique():
        metric_data = latest_data[latest_data['metric_name'] == metric_name]
        metric_info = registry.get(metric_name, {})
        
        report += f"### {metric_name}\n\n"
        report += f"**Type:** {metric_info.get('type', 'unknown')}  \n"
        report += f"**Category:** {metric_info.get('driver_category', 'other')}  \n\n"
        
        # Statistics
        avg_change = metric_data['delta_percentage'].mean()
        median_change = metric_data['delta_percentage'].median()
        
        report += f"**Average Change:** {avg_change:.1f}%  \n"
        report += f"**Median Change:** {median_change:.1f}%  \n"
        report += f"**Entities with Data:** {len(metric_data):,}  \n\n"
        
        # Top 3 movers for this metric
        report += "**Top Movers:**\n\n"
        top3 = metric_data.nlargest(3, 'delta_absolute')
        
        for _, row in top3.iterrows():
            entity_short = str(row['entity'])[:40]
            report += f"- {entity_short}: {row['delta_absolute']:.2f} ({row['delta_percentage']:.1f}%)  \n"
        
        report += "\n"
    
    report += "---\n\n"
    
    return report


def generate_data_quality_section(data: Dict) -> str:
    """Generate data quality and methodology section."""
    
    schema = data.get('schema', {})
    
    report = "## Data Quality & Methodology\n\n"
    
    report += "### Detected Schema\n\n"
    report += f"**Time Column:** `{schema.get('time_column', 'N/A')}`  \n"
    report += f"**Entity Columns:** {len(schema.get('entity_columns', []))}  \n"
    report += f"**Measure Columns:** {len(schema.get('measure_columns', []))}  \n\n"
    
    report += "### Analysis Method\n\n"
    report += "- **Variance Calculation:** Period-over-period delta (absolute & percentage)  \n"
    report += "- **Decomposition:** Price × Volume where applicable  \n"
    report += "- **Detection:** Automatic schema detection (zero configuration)  \n"
    report += "- **Cost:** $0.00 (deterministic logic, no API calls)  \n\n"
    
    report += "---\n\n"
    
    return report


def generate_appendix(data: Dict) -> str:
    """Generate appendix with technical details."""
    
    summary = data.get('summary', {})
    
    report = "## Appendix\n\n"
    
    report += "### Files Generated\n\n"
    report += "- `detected_schema.json` - Column type mappings  \n"
    report += "- `canonical_data.csv` - Normalized data format  \n"
    report += "- `metric_registry.json` - Metric classifications  \n"
    report += "- `variance_analysis.csv` - Complete variance calculations  \n"
    report += "- `variance_summary.json` - Summary statistics  \n"
    report += "- `financial_report.md` - This report  \n\n"
    
    report += "### System Information\n\n"
    report += f"- **Analysis Engine:** Schema-Agnostic Financial Reporting v2.0  \n"
    
    # Format numbers with comma only if they're actually numbers
    total_recs = summary.get('total_variance_records', 'N/A')
    entities = summary.get('entities_analyzed', 'N/A')
    metrics = summary.get('metrics_analyzed', 'N/A')
    
    if isinstance(total_recs, int):
        report += f"- **Total Variance Records:** {total_recs:,}  \n"
    else:
        report += f"- **Total Variance Records:** {total_recs}  \n"
    
    if isinstance(entities, int):
        report += f"- **Entities Analyzed:** {entities:,}  \n"
    else:
        report += f"- **Entities Analyzed:** {entities}  \n"
        
    if isinstance(metrics, int):
        report += f"- **Metrics Analyzed:** {metrics}  \n"
    else:
        report += f"- **Metrics Analyzed:** {metrics}  \n"
    
    report += "\n"
    
    report += "*Report generated with 100% deterministic logic. All numbers are auditable and traceable to source data.*\n"
    
    return report


def generate_report(analysis_dir: str, output_file: str = None):
    """Generate complete financial report."""
    
    analysis_path = Path(analysis_dir)
    
    if output_file is None:
        output_file = analysis_path / "financial_report.md"
    else:
        output_file = Path(output_file)
    
    print(f"\n📊 Loading analysis data from: {analysis_path}")
    
    # Load all analysis data
    data = load_analysis_data(analysis_path)
    
    print(f"  ✓ Loaded {len(data)} data sources")
    
    # Generate report sections
    print("\n📝 Generating report sections...")
    
    report = ""
    report += generate_executive_summary(data)
    print("  ✓ Executive summary")
    
    report += generate_metric_analysis(data)
    print("  ✓ Metric analysis")
    
    report += generate_data_quality_section(data)
    print("  ✓ Data quality section")
    
    report += generate_appendix(data)
    print("  ✓ Appendix")
    
    # Save report
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\n💾 Report saved: {output_file}")
    print(f"   Size: {len(report):,} characters")
    
    print("\n" + "="*80)
    print("✅ REPORT GENERATION COMPLETE")
    print("="*80)
    print(f"\n📄 View your report: {output_file}")
    print(f"💰 Cost: $0.00 (no API calls)")
    
    return output_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate financial report from analysis results')
    parser.add_argument('--analysis-dir', required=True, help='Directory containing analysis outputs')
    parser.add_argument('--output', help='Output report file (default: <analysis-dir>/financial_report.md)')
    
    args = parser.parse_args()
    
    try:
        generate_report(args.analysis_dir, args.output)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
