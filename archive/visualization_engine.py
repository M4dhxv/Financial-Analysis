"""
PHASE D: VISUALIZATION ENGINE
Generate management-friendly charts for financial reporting.

NO API CALLS - Uses matplotlib (free) and plotly (free).
Cost: $0 for chart generation.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

# Try importing plotly (optional)
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("⚠ Plotly not installed. Only matplotlib charts will be generated.")
    print("  Install with: pip install plotly")

print("="*80)
print("VISUALIZATION ENGINE")
print("="*80)

# Setup output directory
viz_dir = Path(__file__).parent / 'visualizations'
viz_dir.mkdir(exist_ok=True)

# Set matplotlib style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# ============================================================================
# LOAD DATA
# ============================================================================

print("\n" + "-"*80)
print("STEP 1: LOAD DATA")
print("-"*80)

df_cat = pd.read_csv(Path(__file__).parent / 'monthly_metrics_category.csv')
df_overall = pd.read_csv(Path(__file__).parent / 'monthly_metrics_overall.csv')
df_var_cat = pd.read_csv(Path(__file__).parent / 'monthly_variance_category.csv')

print(f"✓ Data loaded")
print(f"  Months: {df_overall['snapshot_month'].nunique()}")

# ============================================================================
# CHART 1: REVENUE TREND (Overall + Top 5 Categories)
# ============================================================================

print("\n" + "-"*80)
print("STEP 2: GENERATING TREND CHARTS")
print("-"*80)

# Overall revenue trend
fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(df_overall['snapshot_month'], df_overall['total_revenue_proxy'] / 1e6, 
        marker='o', linewidth=2.5, color='#2E86AB', label='Total')

# Top 5 categories
top_cats = df_cat.groupby('category_lvl2')['total_revenue_proxy'].sum().nlargest(5).index

colors = ['#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4B51']
for i, cat in enumerate(top_cats):
    df_cat_filtered = df_cat[df_cat['category_lvl2'] == cat]
    ax.plot(df_cat_filtered['snapshot_month'], df_cat_filtered['total_revenue_proxy'] / 1e6,
            marker='s', linewidth=1.5, alpha=0.7, color=colors[i], label=cat[:20])

ax.set_title('Revenue Proxy Trend - Overall & Top 5 Categories', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Revenue Proxy (₹ Millions)', fontsize=12)
ax.legend(loc='best', frameon=True)
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

output_file = viz_dir / '01_revenue_trend.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✓ Saved: {output_file.name}")
plt.close()

# Average price trend
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df_overall['snapshot_month'], df_overall['avg_price'],
        marker='o', linewidth=2.5, color='#2E86AB')

ax.set_title('Average Price Trend', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Average Price (₹)', fontsize=12)
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

output_file = viz_dir / '02_price_trend.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✓ Saved: {output_file.name}")
plt.close()

# ============================================================================
# CHART 2: MoM VARIANCE BAR CHART
# ============================================================================

print("\n" + "-"*80)
print("STEP 3: GENERATING VARIANCE CHARTS")
print("-"*80)

# Get latest month variance
latest_var = df_var_cat[df_var_cat['current_month'] == df_var_cat['current_month'].max()]

# Top categories by absolute revenue change
top_variance_cats = latest_var.nlargest(10, 'total_revenue_proxy_delta_abs')

fig, ax = plt.subplots(figsize=(12, 8))

colors = ['#6A994E' if x > 0 else '#C73E1D' for x in top_variance_cats['total_revenue_proxy_delta_pct']]

ax.barh(top_variance_cats['category_lvl2'], top_variance_cats['total_revenue_proxy_delta_pct'],
        color=colors, alpha=0.8)

ax.set_title(f'Top 10 Categories - Revenue Change% ({top_variance_cats.iloc[0]["prior_month"]} → {top_variance_cats.iloc[0]["current_month"]})', 
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Change (%)', fontsize=12)
ax.set_ylabel('Category', fontsize=12)
ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()

output_file = viz_dir / '03_variance_bar_chart.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✓ Saved: {output_file.name}")
plt.close()

# ============================================================================
# CHART 3: HEATMAP (Category Performance Grid)
# ============================================================================

# Create pivot table of revenue growth %
pivot = df_var_cat.pivot_table(
    index='category_lvl2',
    columns='current_month',
    values='total_revenue_proxy_delta_pct',
    aggfunc='first'
)

# Keep only top 15 categories
top_15_cats = df_cat.groupby('category_lvl2')['total_revenue_proxy'].sum().nlargest(15).index
pivot_filtered = pivot.loc[pivot.index.isin(top_15_cats)]

fig, ax = plt.subplots(figsize=(10, 8))

sns.heatmap(pivot_filtered, annot=True, fmt='.1f', cmap='RdYlGn', center=0,
            cbar_kws={'label': 'Revenue Change %'}, ax=ax, linewidths=0.5)

ax.set_title('Revenue Growth Heatmap - Top 15 Categories', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Category', fontsize=12)
plt.tight_layout()

output_file = viz_dir / '04_variance_heatmap.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✓ Saved: {output_file.name}")
plt.close()

# ============================================================================
# CHART 4: WATERFALL (plotly - if available)
# ============================================================================

if PLOTLY_AVAILABLE:
    print("\n" + "-"*80)
    print("STEP 4: GENERATING INTERACTIVE CHARTS (Plotly)")
    print("-"*80)
    
    # Load driver attribution
    with open(Path(__file__).parent / 'variance_drivers_latest.json') as f:
        drivers = json.load(f)
    
    # Find category with largest absolute change
    largest_change = max(drivers, key=lambda x: abs(x['primary_metric']['delta_abs']))
    
    cat_name = largest_change['category']
    decomp = largest_change['decomposition']
    metrics = largest_change['primary_metric']
    
    # Build waterfall
    fig = go.Figure(go.Waterfall(
        name="Revenue Decomposition",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=["Prior Month", "Price Effect", "Volume Effect", "Interaction", "Current Month"],
        y=[
            metrics['prior_value'],
            decomp['price_effect'],
            decomp['volume_effect'],
            decomp['interaction_effect'],
            metrics['current_value']
        ],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#C73E1D"}},
        increasing={"marker": {"color": "#6A994E"}},
        totals={"marker": {"color": "#2E86AB"}}
    ))
    
    fig.update_layout(
        title=f"Revenue Waterfall - {cat_name}",
        showlegend=False,
        height=600,
        yaxis_title="Revenue Proxy (₹)"
    )
    
    output_file = viz_dir / '05_waterfall_interactive.html'
    fig.write_html(str(output_file))
    print(f"✓ Saved: {output_file.name} (interactive)")

print("\n" + "="*80)
print("✓ VISUALIZATION COMPLETE")
print("="*80)
print(f"\nGenerated charts in: {viz_dir}/")
print(f"  Static charts (PNG): 4 files")
if PLOTLY_AVAILABLE:
    print(f"  Interactive charts (HTML): 1 file")

print("\nNext step: Run report_generator.py for AI narratives")
print("\nCOST: $0.00 (no API calls)")
