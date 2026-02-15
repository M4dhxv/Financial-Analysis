"""
PHASE E: COST-OPTIMIZED REPORT GENERATOR
Markdown reports with optional AI narration.

TWO MODES:
1. FREE MODE: Template-based reports ($0 cost)
2. AI MODE: LLM-enhanced narratives (minimal API calls)
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

print("="*80)
print("MONTHLY PERFORMANCE REPORT GENERATOR")
print("="*80)

# ============================================================================
# LOAD VARIANCE DATA
# ============================================================================

print("\n" + "-"*80)
print("STEP 1: LOAD DATA")
print("-"*80)

# Load latest variance summary
with open(Path(__file__).parent / 'variance_summary_latest.json') as f:
    variance_summary = json.load(f)

# Load driver attributions
with open(Path(__file__).parent / 'variance_drivers_latest.json') as f:
    drivers = json.load(f)

current_month = variance_summary['current_month']
prior_month = variance_summary['prior_month']

print(f"✓ Loaded variance data for {prior_month} → {current_month}")
print(f"  Top categories: {len(variance_summary['top_categories'])}")
print(f"  Driver analyses: {len(drivers)}")

# ============================================================================
# GENERATE REPORT (FREE MODE - NO API CALLS)
# ============================================================================

print("\n" + "-"*80)
print("STEP 2: GENERATE REPORT (FREE MODE)")
print("-"*80)

# Build markdown report
report_lines = []

# Header
report_lines.append(f"# Monthly Performance Report")
report_lines.append(f"## Period: {prior_month} → {current_month}")
report_lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Executive Summary (Template-based)
report_lines.append("## Executive Summary")
report_lines.append("")

overall = variance_summary['overall']
rev = overall.get('total_revenue_proxy', {})
price = overall.get('avg_price', {})
rating = overall.get('avg_rating_weighted', {})

if rev:
    direction = "↑" if rev['delta_pct'] > 0 else "↓"
    report_lines.append(f"**Revenue Proxy:** {direction} {abs(rev['delta_pct']):.1f}% (₹{rev['current']/1e6:.1f}M from ₹{rev['prior']/1e6:.1f}M)")
if price:
    direction = "↑" if price['delta_pct'] > 0 else "↓"
    report_lines.append(f"**Average Price:** {direction} {abs(price['delta_pct']):.1f}% (₹{price['current']:.0f} from ₹{price['prior']:.0f})")
if rating:
    direction = "↑" if rating['delta_abs'] > 0 else "↓"
    report_lines.append(f"**Average Rating:** {direction} {abs(rating['delta_abs']):.2f} stars ({rating['current']:.2f}★)")

report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Key Performance Indicators Table
report_lines.append("## Key Performance Indicators")
report_lines.append("")
report_lines.append("| Metric | Current | Prior | Change | Change % |")
report_lines.append("|--------|---------|-------|--------|----------|")

for kpi_name, kpi_data in overall.items():
    if isinstance(kpi_data, dict):
        label = kpi_data.get('label', kpi_name)
        current = f"{kpi_data['current']:,.0f}" if kpi_data['current'] > 1000 else f"{kpi_data['current']:.2f}"
        prior = f"{kpi_data['prior']:,.0f}" if kpi_data['prior'] > 1000 else f"{kpi_data['prior']:.2f}"
        delta_abs = f"{kpi_data['delta_abs']:+,.0f}" if abs(kpi_data['delta_abs']) > 1000 else f"{kpi_data['delta_abs']:+.2f}"
        delta_pct = f"{kpi_data['delta_pct']:+.1f}%"
        
        report_lines.append(f"| {label} | {current} | {prior} | {delta_abs} | {delta_pct} |")

report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Category Performance
report_lines.append("## Top Category Performance")
report_lines.append("")

for cat_data in variance_summary['top_categories'][:5]:
    cat_name = cat_data['category']
    rev_current = cat_data['revenue_current']
    rev_delta_pct = cat_data['revenue_delta_pct']
    price_effect = cat_data['price_effect']
    volume_effect = cat_data['volume_effect']
    
    # Find driver analysis for this category
    cat_drivers = next((d for d in drivers if d['category'] == cat_name), None)
    
    report_lines.append(f"### {cat_name}")
    report_lines.append("")
    report_lines.append(f"**Revenue Proxy:** ₹{rev_current:,.0f} ({rev_delta_pct:+.1f}%)")
    report_lines.append("")
    
    # Mathematical Decomposition
    report_lines.append(f"**Variance Decomposition:**")
    report_lines.append(f"- Price Effect: ₹{price_effect:+,.0f}")
    report_lines.append(f"- Volume Effect: ₹{volume_effect:+,.0f}")
    report_lines.append("")
    
    # Driver Attribution
    if cat_drivers and cat_drivers['drivers']:
        report_lines.append(f"**Key Drivers:**")
        for driver in cat_drivers['drivers']:
            report_lines.append(f"{driver['rank']}. {driver['narrative']}")
        report_lines.append("")
    
    report_lines.append("---")
    report_lines.append("")

# Appendix
report_lines.append("## Appendix")
report_lines.append("")
report_lines.append("### Charts")
report_lines.append("- Revenue Trend: `visualizations/01_revenue_trend.png`")
report_lines.append("- Price Trend: `visualizations/02_price_trend.png`")
report_lines.append("- Variance Bar Chart: `visualizations/03_variance_bar_chart.png`")
report_lines.append("- Variance Heatmap: `visualizations/04_variance_heatmap.png`")
report_lines.append("")
report_lines.append("### Data Sources")
report_lines.append(f"- Time-series data: `product_performance_timeseries.csv`")
report_lines.append(f"- Category metrics: `monthly_metrics_category.csv`")
report_lines.append(f"- Overall metrics: `monthly_metrics_overall.csv`")
report_lines.append(f"- Variance analysis: `monthly_variance_category.csv`")
report_lines.append(f"- Driver attribution: `variance_drivers.json`")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("*This report was generated using 100% deterministic logic with zero API costs.*")

# Save report
output_file = Path(__file__).parent / f'monthly_report_{current_month}.md'
with open(output_file, 'w') as f:
    f.write('\n'.join(report_lines))

print(f"✓ Report generated: {output_file.name}")
print(f"  Lines: {len(report_lines)}")
print(f"  Size: {output_file.stat().st_size} bytes")

# ============================================================================
# COST SUMMARY
# ============================================================================

print("\n" + "="*80)
print("✓ REPORT GENERATION COMPLETE")
print("="*80)
print("\n📊 COST ANALYSIS:")
print("  Mode: FREE (Template-based)")
print("  API Calls: 0")
print("  Cost: $0.00")
print("")
print("💡 AI-ENHANCED OPTION:")
print("  To add AI narratives, run: report_generator_ai.py")
print("  Estimated cost: ~$0.01-0.03 (using GPT-4 mini or Gemini Flash)")
print("  Benefit: Richer executive summaries and insights")
print("")
print("✨ EFFECTIVENESS:")
print("  ✓ All numbers are deterministic and verifiable")
print("  ✓ Mathematical decomposition (price × volume)")
print("  ✓ Driver attribution with impact scores")
print("  ✓ Visual charts for management review")
print("  ✓ Zero hallucination risk (template-based)")
print("  ✓ Instant generation (no API latency)")
