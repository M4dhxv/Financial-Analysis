#!/usr/bin/env python3
"""
UNIVERSAL CHART GENERATOR
Generates visualizations from canonical data and variance analysis.

Works with ANY dataset - completely schema-agnostic.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

from chart_registry import ChartRegistry

print("="*80)
print("UNIVERSAL CHART GENERATOR")
print("="*80)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

def load_analysis_data(analysis_dir: Path) -> Dict:
    """Load all analysis data."""
    
    data = {}
    
    # Load canonical data (sample for performance)
    canonical_file = analysis_dir / "canonical_data.csv"
    if canonical_file.exists():
        data['canonical'] = pd.read_csv(canonical_file, nrows=100000)
    
    # Load variance
    variance_file = analysis_dir / "variance_analysis.csv"
    if variance_file.exists():
        data['variance'] = pd.read_csv(variance_file)
    
    # Load metric registry
    registry_file = analysis_dir / "metric_registry.json"
    if registry_file.exists():
        with open(registry_file, 'r') as f:
            data['registry'] = json.load(f)
    
    return data


def generate_metric_trends(data: Dict, registry: ChartRegistry, output_dir: Path):
    """Generate trend charts for top metrics."""
    
    print("\n📈 Generating metric trend charts...")
    
    df_canonical = data.get('canonical')
    metric_registry = data.get('registry', {})
    
    if df_canonical is None:
        print("  ⚠️  No canonical data available")
        return
    
    # Get top priority metrics
    priority_metrics = sorted(
        [(m, info) for m, info in metric_registry.items()],
        key=lambda x: x[1].get('analysis_priority', 99)
    )[:5]  # Top 5 metrics
    
    for metric_name, info in priority_metrics:
        # Filter to this metric
        df_metric = df_canonical[df_canonical['metric_name'] == metric_name]
        
        if len(df_metric) == 0:
            continue
        
        # Aggregate by period
        trends = df_metric.groupby('period')['metric_value'].agg(['mean', 'sum', 'count']).reset_index()
        trends = trends.sort_values('period')
        
        # Limit to recent periods for readability
        if len(trends) > 12:
            trends = trends.tail(12)
        
        # Create chart
        fig, ax = plt.subplots(figsize=(10, 5))
        
        ax.plot(range(len(trends)), trends['mean'], marker='o', linewidth=2, markersize=8, color='#2E86AB')
        ax.fill_between(range(len(trends)), trends['mean'], alpha=0.3, color='#2E86AB')
        
        ax.set_title(f'{metric_name} - Trend Over Time', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Period', fontsize=11)
        ax.set_ylabel(f'Average {metric_name}', fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.set_xticks(range(len(trends)))
        ax.set_xticklabels([str(p)[:10] for p in trends['period']], rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save
        chart_file = output_dir / f"trend_{metric_name.lower().replace(' ', '_')}.png"
        plt.savefig(chart_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        registry.register_chart('trend', metric_name, chart_file, periods=len(trends))
        
    print(f"  ✓ Generated {len(priority_metrics)} trend charts")


def generate_variance_charts(data: Dict, registry: ChartRegistry, output_dir: Path):
    """Generate variance visualization charts."""
    
    print("\n📊 Generating variance charts...")
    
    df_variance = data.get('variance')
    
    if df_variance is None or len(df_variance) == 0:
        print("  ⚠️  No variance data available")
        return
    
    # Get latest period
    latest_period = df_variance['current_period'].max()
    latest_var = df_variance[df_variance['current_period'] == latest_period]
    
    # Top movers chart (top 10 by absolute change)
    top_movers = latest_var.nlargest(10, 'delta_absolute')
    
    if len(top_movers) > 0:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create labels
        labels = [f"{row['metric_name']}\n{str(row['entity'])[:30]}..." 
                 for _, row in top_movers.iterrows()]
        
        colors = ['#06D6A0' if x > 0 else '#EF476F' for x in top_movers['delta_absolute']]
        
        ax.barh(range(len(top_movers)), top_movers['delta_absolute'], color=colors, alpha=0.8)
        ax.set_yticks(range(len(top_movers)))
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel('Absolute Change', fontsize=11, fontweight='bold')
        ax.set_title('Top 10 Largest Changes', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, axis='x', alpha=0.3)
        ax.axvline(x=0, color='black', linewidth=0.8, linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        
        chart_file = output_dir / "variance_top_movers.png"
        plt.savefig(chart_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        registry.register_chart('bar', 'Top Movers', chart_file, entity_count=len(top_movers))
    
    # Variance distribution by metric
    fig, ax = plt.subplots(figsize=(10, 5))
    
    metrics = latest_var['metric_name'].unique()
    for metric in metrics[:5]:  # Top 5 metrics
        metric_var = latest_var[latest_var['metric_name'] == metric]['delta_percentage']
        if len(metric_var) > 0:
            ax.hist(metric_var, bins=20, alpha=0.5, label=metric, edgecolor='black')
    
    ax.set_xlabel('Variance %', fontsize=11, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax.set_title('Variance Distribution by Metric', fontsize=14, fontweight='bold', pad=20)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    chart_file = output_dir / "variance_distribution.png"
    plt.savefig(chart_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    registry.register_chart('histogram', 'Variance Distribution', chart_file)
    
    print(f"  ✓ Generated 2 variance charts")


def generate_heatmap(data: Dict, registry: ChartRegistry, output_dir: Path):
    """Generate heatmap of metrics over time."""
    
    print("\n🔥 Generating heatmap...")
    
    df_variance = data.get('variance')
    
    if df_variance is None or len(df_variance) == 0:
        print("  ⚠️  No variance data available")
        return
    
    # Get top metrics
    metrics = df_variance['metric_name'].value_counts().head(5).index.tolist()
    
    # Sample entities for readability
    unique_entities = df_variance['entity'].unique()
    if len(unique_entities) > 15:
        sample_entities = unique_entities[:15]
    else:
        sample_entities = unique_entities
    
    # Create pivot for heatmap
    for metric in metrics[:3]:  # Top 3 metrics only
        metric_data = df_variance[
            (df_variance['metric_name'] == metric) &
            (df_variance['entity'].isin(sample_entities))
        ]
        
        if len(metric_data) == 0:
            continue
        
        # Pivot
        pivot = metric_data.pivot_table(
            index='entity',
            columns='current_period',
            values='delta_percentage',
            aggfunc='first'
        )
        
        # Limit columns
        if len(pivot.columns) > 6:
            pivot = pivot[pivot.columns[-6:]]
        
        if pivot.empty:
            continue
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        
        sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn', center=0,
                   cbar_kws={'label': 'Variance %'}, ax=ax, linewidths=0.5)
        
        ax.set_title(f'{metric} - Variance Heatmap', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Period', fontsize=11, fontweight='bold')
        ax.set_ylabel('Entity', fontsize=11, fontweight='bold')
        
        # Truncate labels
        yticklabels = [str(label.get_text())[:40] + '...' if len(str(label.get_text())) > 40 
                      else label.get_text() for label in ax.get_yticklabels()]
        ax.set_yticklabels(yticklabels, rotation=0, fontsize=8)
        
        plt.tight_layout()
        
        chart_file = output_dir / f"heatmap_{metric.lower().replace(' ', '_')}.png"
        plt.savefig(chart_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        registry.register_chart('heatmap', metric, chart_file, 
                              entities=len(pivot), periods=len(pivot.columns))
    
    print(f"  ✓ Generated heatmap(s)")


def generate_charts(analysis_dir: str, output_dir: str = None):
    """Main entry point for chart generation."""
    
    analysis_path = Path(analysis_dir)
    
    if output_dir:
        charts_dir = Path(output_dir)
    else:
        charts_dir = analysis_path / "charts"
    
    charts_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"\n📁 Input: {analysis_path}")
    print(f"📁 Output: {charts_dir}/")
    
    # Initialize registry
    registry = ChartRegistry(str(charts_dir))
    
    # Load data
    print(f"\n📊 Loading analysis data...")
    data = load_analysis_data(analysis_path)
    print(f"  ✓ Loaded {len(data)} data sources")
    
    # Generate charts
    generate_metric_trends(data, registry, charts_dir)
    generate_variance_charts(data, registry, charts_dir)
    generate_heatmap(data, registry, charts_dir)
    
    # Save registry
    registry.save_manifest()
    
    print("\n" + "="*80)
    print("✅ CHART GENERATION COMPLETE")
    print("="*80)
    print(f"\n📊 Generated {len(registry.charts)} charts")
    print(f"📁 Saved to: {charts_dir}/")
    print(f"📋 Manifest: {charts_dir}/chart_registry.json")
    print(f"\n💰 Cost: $0.00 (no API calls)")
    
    return registry


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate charts from analysis results')
    parser.add_argument('--analysis-dir', required=True, help='Directory containing analysis outputs')
    parser.add_argument('--output', help='Output directory for charts (default: <analysis-dir>/charts/)')
    
    args = parser.parse_args()
    
    try:
        generate_charts(args.analysis_dir, args.output)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
