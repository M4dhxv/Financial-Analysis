"""
PHASE A: MONTHLY AGGREGATES
Generate canonical monthly metrics at category and overall levels.

NO API CALLS - 100% deterministic pandas aggregations.
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("="*80)
print("MONTHLY AGGREGATION ENGINE")
print("="*80)

# ============================================================================
# LOAD TIME-SERIES DATA
# ============================================================================

print("\n" + "-"*80)
print("STEP 1: LOAD TIME-SERIES DATA")
print("-"*80)

input_file = Path(__file__).parent / 'product_performance_timeseries.csv'
df = pd.read_csv(input_file)

print(f"\n✓ Loaded {len(df):,} rows")
print(f"  Products: {df['product_id'].nunique():,}")
print(f"  Months: {df['snapshot_month'].nunique()}")
print(f"  Categories: {df['category_lvl2'].nunique()}")

# ============================================================================
# CATEGORY-LEVEL AGGREGATES
# ============================================================================

print("\n" + "-"*80)
print("STEP 2: CATEGORY-LEVEL MONTHLY METRICS")
print("-"*80)

# Calculate revenue proxy (price × demand signal)
df['revenue_proxy'] = df['discounted_price_clean'] * df['rating_count_clean']

# Group by month and category
df_category = df.groupby(['snapshot_month', 'category_lvl2']).agg({
    # Count
    'product_id': 'count',
    
    # Revenue metrics
    'revenue_proxy': 'sum',
    'discounted_price_clean': 'mean',
    'discount_percentage_clean': 'mean',
    
    # Quality metrics
    'avg_rating': lambda x: np.average(x, weights=df.loc[x.index, 'rating_count_clean']),  # Weighted avg
    'rating_count_clean': 'sum',
    
    # Distribution metrics
    'avg_rating': ['median', lambda x: (x >= 4.0).mean() * 100]  # Median rating, % >= 4 stars
}).reset_index()

# Flatten column names
df_category.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                       for col in df_category.columns.values]

# Rename for clarity
df_category = df_category.rename(columns={
    'product_id_count': 'product_count',
    'revenue_proxy_sum': 'total_revenue_proxy',
    'discounted_price_clean_mean': 'avg_price',
    'discount_percentage_clean_mean': 'avg_discount_percentage',
    'avg_rating_<lambda>': 'avg_rating_weighted',
    'rating_count_clean_sum': 'total_review_count',
    'avg_rating_median': 'median_rating',
    'avg_rating_<lambda_0>': 'pct_products_above_4_stars'
})

print(f"\n✓ Category-level metrics calculated:")
print(f"  Rows: {len(df_category):,} (month × category combinations)")
print(f"  Columns: {len(df_category.columns)}")
print(f"\n  Sample (first 3 rows):")
print(df_category.head(3).to_string(index=False))

# Save category metrics
output_category = Path(__file__).parent / 'monthly_metrics_category.csv'
df_category.to_csv(output_category, index=False)
print(f"\n✓ Saved to: {output_category.name}")

# ============================================================================
# OVERALL-LEVEL AGGREGATES
# ============================================================================

print("\n" + "-"*80)
print("STEP 3: OVERALL MONTHLY METRICS")
print("-"*80)

# Group by month only
df_overall = df.groupby('snapshot_month').agg({
    # Counts
    'product_id': 'count',
    'category_lvl2': 'nunique',
    
    # Revenue metrics
    'revenue_proxy': 'sum',
    'discounted_price_clean': 'mean',
    'discount_percentage_clean': 'mean',
    
    # Quality metrics (weighted by review count)
    'avg_rating': lambda x: np.average(x, weights=df.loc[x.index, 'rating_count_clean']),
    'rating_count_clean': 'sum',
}).reset_index()

# Rename columns
df_overall.columns = [
    'snapshot_month',
    'total_products',
    'category_count',
    'total_revenue_proxy',
    'avg_price',
    'avg_discount_percentage',
    'avg_rating_weighted',
    'total_review_volume'
]

# Add top category by revenue for each month
top_categories = df_category.loc[
    df_category.groupby('snapshot_month')['total_revenue_proxy'].idxmax()
][['snapshot_month', 'category_lvl2']].rename(columns={'category_lvl2': 'top_category_by_revenue'})

df_overall = df_overall.merge(top_categories, on='snapshot_month', how='left')

print(f"\n✓ Overall metrics calculated:")
print(f"  Rows: {len(df_overall):,} (one per month)")
print(f"  Columns: {len(df_overall.columns)}")
print(f"\n  Monthly Summary:")
print(df_overall.to_string(index=False))

# Save overall metrics
output_overall = Path(__file__).parent / 'monthly_metrics_overall.csv'
df_overall.to_csv(output_overall, index=False)
print(f"\n✓ Saved to: {output_overall.name}")

print("\n" + "="*80)
print("✓ AGGREGATION COMPLETE")
print("="*80)
print("\nNext step: Run variance_calculator.py for MoM analysis")
print("\nCOST: $0.00 (no API calls)")
