"""
PHASE B: VARIANCE CALCULATOR
Calculate month-over-month deltas with mathematical decomposition.

NO API CALLS - 100% deterministic pandas calculations.
Implements best practice from ChatGPT's approach: (price_change × old_qty) + (qty_change × old_price)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

print("="*80)
print("VARIANCE CALCULATION ENGINE")
print("="*80)

# ============================================================================
# CONFIGURATION
# ============================================================================

# KPI definitions with formatting rules
KPIS = {
    'total_revenue_proxy': {'label': 'Revenue Proxy', 'format': 'currency', 'unit': '₹'},
    'product_count': {'label': 'Product Count', 'format': 'integer', 'unit': ''},
    'avg_price': {'label': 'Average Price', 'format': 'currency', 'unit': '₹'},
    'avg_discount_percentage': {'label': 'Average Discount %', 'format': 'percentage', 'unit': '%'},
    'avg_rating_weighted': {'label': 'Average Rating', 'format': 'decimal', 'unit': '★'},
    'total_review_count': {'label': 'Review Volume', 'format': 'integer', 'unit': ''},
    'pct_products_above_4_stars': {'label': '% Products >4★', 'format': 'percentage', 'unit': '%'}
}

# ============================================================================
# LOAD METRICS
# ============================================================================

print("\n" + "-"*80)
print("STEP 1: LOAD MONTHLY METRICS")
print("-"*80)

# Load category metrics
df_cat = pd.read_csv(Path(__file__).parent / 'monthly_metrics_category.csv')
print(f"\n✓ Category metrics: {len(df_cat):,} rows")

# Load overall metrics  
df_overall = pd.read_csv(Path(__file__).parent / 'monthly_metrics_overall.csv')
print(f"✓ Overall metrics: {len(df_overall):,} rows")

# ============================================================================
# VARIANCE CALCULATION FUNCTION
# ============================================================================

def calculate_variance(df_current, df_prior, grain_cols, kpi_cols):
    """
    Calculate MoM variance for all KPIs with mathematical decomposition
    
    Parameters:
    - df_current: Current month metrics
    - df_prior: Prior month metrics
    - grain_cols: List of grouping columns (e.g., ['category_lvl2'])
    - kpi_cols: Dictionary of KPI configurations
    
    Returns: DataFrame with variance metrics
    """
    # Merge current and prior
    if grain_cols:
        df = df_current.merge(
            df_prior,
            on=grain_cols,
            suffixes=('_current', '_prior'),
            how='left'
        )
    else:
        # Overall metrics - just concat side by side
        df_curr_renamed = df_current.add_suffix('_current')
        df_prior_renamed = df_prior.add_suffix('_prior')
        df = pd.concat([df_curr_renamed.reset_index(drop=True), 
                        df_prior_renamed.reset_index(drop=True)], axis=1)
    
    # Calculate deltas for each KPI
    for kpi_name, kpi_config in kpi_cols.items():
        if f'{kpi_name}_current' not in df.columns:
            continue
            
        # Absolute change
        df[f'{kpi_name}_delta_abs'] = (
            df[f'{kpi_name}_current'] - df[f'{kpi_name}_prior']
        )
        
        # Percentage change (handle division by zero)
        df[f'{kpi_name}_delta_pct'] = (
            df[f'{kpi_name}_delta_abs'] / df[f'{kpi_name}_prior'].replace(0, np.nan) * 100
        ).fillna(0)
        
        # Variance direction
        df[f'{kpi_name}_direction'] = df[f'{kpi_name}_delta_abs'].apply(
            lambda x: 'increase' if x > 0 else ('decrease' if x < 0 else 'flat')
        )
    
    # MATHEMATICAL DECOMPOSITION for revenue_proxy
    # Revenue = Price × Quantity
    # ΔRevenue = (ΔPrice × Qty_old) + (ΔQty × Price_old) + (ΔPrice × ΔQty)
    
    if 'total_revenue_proxy_current' in df.columns:
        # Detect which column name is used for review counts
        review_col = 'total_review_count' if 'total_review_count_current' in df.columns else 'total_review_volume'
        
        # Price effect: price change holding quantity constant
        df['price_effect'] = (
            (df['avg_price_current'] - df['avg_price_prior']) * 
            df[f'{review_col}_prior']
        )
        
        # Volume effect: quantity change holding price constant
        df['volume_effect'] = (
            (df[f'{review_col}_current'] - df[f'{review_col}_prior']) *
            df['avg_price_prior']
        )
        
        # Interaction effect (usually small)
        df['interaction_effect'] = (
            (df['avg_price_current'] - df['avg_price_prior']) *
            (df[f'{review_col}_current'] - df[f'{review_col}_prior'])
        )
        
        # Verify decomposition (should equal total_revenue_proxy_delta_abs)
        df['decomp_total'] = df['price_effect'] + df['volume_effect'] + df['interaction_effect']
    
    return df


# ============================================================================
# CALCULATE CATEGORY-LEVEL VARIANCE
# ============================================================================

print("\n" + "-"*80)
print("STEP 2: CALCULATE CATEGORY-LEVEL VARIANCES")
print("-"*80)

# Get unique months sorted
months = sorted(df_cat['snapshot_month'].unique())
print(f"\nProcessing {len(months)} months...")

variance_results_cat = []

for i in range(1, len(months)):
    current_month = months[i]
    prior_month = months[i-1]
    
    print(f"\n  {prior_month} → {current_month}")
    
    df_curr = df_cat[df_cat['snapshot_month'] == current_month]
    df_pri = df_cat[df_cat['snapshot_month'] == prior_month]
    
    variance = calculate_variance(
        df_curr,
        df_pri,
        grain_cols=['category_lvl2'],
        kpi_cols=KPIS
    )
    
    # Add month labels
    variance['current_month'] = current_month
    variance['prior_month'] = prior_month
    
    variance_results_cat.append(variance)
    
    print(f"    Categories analyzed: {len(variance)}")

# Combine all monthly variances
df_variance_cat = pd.concat(variance_results_cat, ignore_index=True)

print(f"\n✓ Category variance table created:")
print(f"  Rows: {len(df_variance_cat):,}")
print(f"  Periods: {df_variance_cat['current_month'].nunique()}")

# Save
output_var_cat = Path(__file__).parent / 'monthly_variance_category.csv'
df_variance_cat.to_csv(output_var_cat, index=False)
print(f"✓ Saved to: {output_var_cat.name}")

# ============================================================================
# CALCULATE OVERALL VARIANCE
# ============================================================================

print("\n" + "-"*80)
print("STEP 3: CALCULATE OVERALL VARIANCES")
print("-"*80)

variance_results_overall = []

for i in range(1, len(months)):
    current_month = months[i]
    prior_month = months[i-1]
    
    df_curr = df_overall[df_overall['snapshot_month'] == current_month]
    df_pri = df_overall[df_overall['snapshot_month'] == prior_month]
    
    # Calculate variance (no grain, just month-to-month)
    variance = calculate_variance(
        df_curr,
        df_pri,
        grain_cols=[],
        kpi_cols={k: v for k, v in KPIS.items() if k in df_overall.columns}
    )
    
    variance['current_month'] = current_month
    variance['prior_month'] = prior_month
    
    variance_results_overall.append(variance)

df_variance_overall = pd.concat(variance_results_overall, ignore_index=True)

print(f"\n✓ Overall variance table created:")
print(f"  Rows: {len(df_variance_overall)}")

# Display summary
print(f"\n  Monthly Variance Summary:")
for _, row in df_variance_overall.iterrows():
    print(f"\n  {row['prior_month']} → {row['current_month']}:")
    print(f"    Revenue Proxy: {row.get('total_revenue_proxy_delta_pct', 0):.1f}%")
    print(f"    Avg Price: {row.get('avg_price_delta_pct', 0):.1f}%")
    print(f"    Review Volume: {row.get('total_review_volume_delta_pct', 0):.1f}%")

# Save
output_var_overall = Path(__file__).parent / 'monthly_variance_overall.csv'
df_variance_overall.to_csv(output_var_overall, index=False)
print(f"\n✓ Saved to: {output_var_overall.name}")

# ============================================================================
# EXPORT VARIANCE SUMMARY (for driver attribution)
# ============================================================================

print("\n" + "-"*80)
print("STEP 4: EXPORT VARIANCE SUMMARY")
print("-"*80)

# Create JSON summary for latest month
latest_month = months[-1]
prior_month = months[-2]

summary = {
    'current_month': latest_month,
    'prior_month': prior_month,
    'overall': {},
    'top_categories': []
}

# Overall metrics
overall_row = df_variance_overall[df_variance_overall['current_month'] == latest_month].iloc[0]
for kpi_name, kpi_config in KPIS.items():
    if f'{kpi_name}_current' in overall_row:
        summary['overall'][kpi_name] = {
            'label': kpi_config['label'],
            'current': float(overall_row[f'{kpi_name}_current']),
            'prior': float(overall_row[f'{kpi_name}_prior']),
            'delta_abs': float(overall_row[f'{kpi_name}_delta_abs']),
            'delta_pct': float(overall_row[f'{kpi_name}_delta_pct']),
            'direction': overall_row[f'{kpi_name}_direction']
        }

# Top 5 categories by revenue
cat_latest = df_variance_cat[df_variance_cat['current_month'] == latest_month]
top_cats = cat_latest.nlargest(5, 'total_revenue_proxy_current')

for _, cat_row in top_cats.iterrows():
    cat_summary = {
        'category': cat_row['category_lvl2'],
        'revenue_current': float(cat_row['total_revenue_proxy_current']),
        'revenue_delta_pct': float(cat_row['total_revenue_proxy_delta_pct']),
        'price_effect': float(cat_row.get('price_effect', 0)),
        'volume_effect': float(cat_row.get('volume_effect', 0))
    }
    summary['top_categories'].append(cat_summary)

# Save JSON
summary_file = Path(__file__).parent / 'variance_summary_latest.json'
with open(summary_file, 'w') as f:
    json.dump(summary, f, indent=2)

print(f"✓ Variance summary exported to: {summary_file.name}")

print("\n" + "="*80)
print("✓ VARIANCE CALCULATION COMPLETE")
print("="*80)
print("\nNext step: Run driver_attribution.py for root cause analysis")
print("\nCOST: $0.00 (no API calls)")
