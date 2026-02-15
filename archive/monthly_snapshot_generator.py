"""
PHASE A: MONTHLY SNAPSHOT GENERATOR
Transform static product table into time-series data for financial reporting demo.

NO API CALLS - 100% deterministic pandas transformations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Time period for demo (6 months)
START_MONTH = '2024-01'
NUM_MONTHS = 6

# Variation parameters (realistic monthly changes)
PRICE_VOLATILITY = 0.05  # ±5% monthly price changes
RATING_DRIFT = 0.15      # ±0.15 stars monthly rating changes
REVIEW_GROWTH_RATE = 0.03  # 3% monthly review accumulation
DISCOUNT_VOLATILITY = 3.0   # ±3 percentage points

# Random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

print("="*80)
print("MONTHLY SNAPSHOT GENERATOR")
print("="*80)
print(f"\nConfiguration:")
print(f"  Time period: {START_MONTH} + {NUM_MONTHS} months")
print(f"  Price volatility: ±{PRICE_VOLATILITY*100:.1f}%")
print(f"  Rating drift: ±{RATING_DRIFT:.2f} stars")
print(f"  Review growth: {REVIEW_GROWTH_RATE*100:.1f}% monthly")
print(f"  Discount volatility: ±{DISCOUNT_VOLATILITY:.1f}pp")

# ============================================================================
# LOAD BASE DATA
# ============================================================================

print("\n" + "-"*80)
print("STEP 1: LOAD BASE PRODUCT DATA")
print("-"*80)

input_file = Path(__file__).parent / 'product_performance_table.csv'
df_base = pd.read_csv(input_file)

print(f"\n✓ Loaded {len(df_base):,} products from {input_file.name}")
print(f"  Columns: {len(df_base.columns)}")
print(f"  Categories: {df_base['category_lvl2'].nunique()}")

# ============================================================================
# GENERATE MONTHLY SNAPSHOTS
# ============================================================================

print("\n" + "-"*80)
print("STEP 2: GENERATE MONTHLY SNAPSHOTS")
print("-"*80)

def generate_month_label(start_month, offset):
    """Generate YYYY-MM label for month offset"""
    year, month = map(int, start_month.split('-'))
    month += offset
    while month > 12:
        month -= 12
        year += 1
    return f"{year:04d}-{month:02d}"

def apply_monthly_variation(base_value, month_idx, volatility, drift_type='random_walk'):
    """
    Apply realistic monthly variation to a metric
    
    Parameters:
    - base_value: Starting value
    - month_idx: Month number (0-5)
    - volatility: Standard deviation of changes
    - drift_type: 'random_walk', 'growth', or 'mean_reverting'
    """
    if pd.isna(base_value):
        return base_value
    
    if drift_type == 'random_walk':
        # Random walk: cumulative random changes
        changes = np.random.normal(0, volatility, month_idx + 1)
        cumulative_change = np.sum(changes)
        return base_value * (1 + cumulative_change)
    
    elif drift_type == 'growth':
        # Steady growth with noise
        trend = volatility * month_idx
        noise = np.random.normal(0, volatility * 0.5)
        return base_value * (1 + trend + noise)
    
    elif drift_type == 'mean_reverting':
        # Oscillates around base value
        deviation = np.random.normal(0, volatility)
        reversion = -0.3 * (month_idx - NUM_MONTHS/2) * volatility
        return base_value * (1 + deviation + reversion)
    
    return base_value

# Create list to store monthly snapshots
snapshots = []

for month_idx in range(NUM_MONTHS):
    month_label = generate_month_label(START_MONTH, month_idx)
    
    print(f"\n  Generating snapshot for {month_label}...")
    
    # Copy base data
    df_month = df_base.copy()
    
    # Add month column
    df_month['snapshot_month'] = month_label
    
    # Apply variations to each product
    for idx, row in df_month.iterrows():
        # Price variations (random walk with mean reversion)
        if pd.notna(row['discounted_price_clean']):
            base_price = row['discounted_price_clean']
            # Add product-specific random walk
            product_seed = hash(row['product_id']) % 10000
            np.random.seed(RANDOM_SEED + product_seed + month_idx)
            
            price_change = np.random.normal(0, PRICE_VOLATILITY)
            df_month.at[idx, 'discounted_price_clean'] = base_price * (1 + price_change)
            
            # Recalculate discount percentage if we have actual price
            if pd.notna(row['actual_price_clean']):
                new_discount = (
                    (row['actual_price_clean'] - df_month.at[idx, 'discounted_price_clean']) / 
                    row['actual_price_clean'] * 100
                )
                df_month.at[idx, 'discount_percentage_clean'] = max(0, min(100, new_discount))
        
        # Rating variations (slow drift)
        if pd.notna(row['avg_rating']):
            np.random.seed(RANDOM_SEED + product_seed + month_idx + 1000)
            rating_change = np.random.normal(0, RATING_DRIFT / NUM_MONTHS)
            new_rating = row['avg_rating'] + rating_change * month_idx
            df_month.at[idx, 'avg_rating'] = max(1.0, min(5.0, new_rating))
        
        # Review count growth (cumulative)
        if pd.notna(row['rating_count_clean']):
            np.random.seed(RANDOM_SEED + product_seed + month_idx + 2000)
            growth = np.random.normal(REVIEW_GROWTH_RATE, REVIEW_GROWTH_RATE * 0.5)
            growth_factor = (1 + growth) ** month_idx
            df_month.at[idx, 'rating_count_clean'] = int(row['rating_count_clean'] * growth_factor)
    
    # Recalculate category benchmarks for this month
    category_benchmarks = df_month.groupby('category_lvl2').agg({
        'discounted_price_clean': 'median',
        'discount_percentage_clean': 'median',
        'avg_rating': 'median',
        'rating_count_clean': 'median'
    }).reset_index()
    
    category_benchmarks.columns = [
        'category_lvl2',
        'median_price',
        'median_discount_percentage',
        'median_rating',
        'median_rating_count'
    ]
    
    # Drop old benchmark columns
    benchmark_cols = ['median_price', 'median_discount_percentage', 
                     'median_rating', 'median_rating_count']
    df_month = df_month.drop(columns=benchmark_cols, errors='ignore')
    
    # Join new benchmarks
    df_month = df_month.merge(category_benchmarks, on='category_lvl2', how='left')
    
    # Recalculate relative metrics
    df_month['price_vs_category_median'] = (
        (df_month['discounted_price_clean'] - df_month['median_price']) / 
        df_month['median_price'] * 100
    )
    
    df_month['discount_vs_category_median'] = (
        (df_month['discount_percentage_clean'] - df_month['median_discount_percentage']) / 
        df_month['median_discount_percentage'] * 100
    )
    
    df_month['rating_vs_category_median'] = (
        df_month['avg_rating'] - df_month['median_rating']
    )
    
    df_month['rating_count_vs_category_median'] = (
        (df_month['rating_count_clean'] - df_month['median_rating_count']) / 
        df_month['median_rating_count'] * 100
    )
    
    snapshots.append(df_month)
    
    print(f"    Products: {len(df_month):,}")
    print(f"    Avg price: ₹{df_month['discounted_price_clean'].mean():.2f}")
    print(f"    Avg rating: {df_month['avg_rating'].mean():.2f}★")
    print(f"    Total reviews: {df_month['rating_count_clean'].sum():,}")

# Reset random seed
np.random.seed(RANDOM_SEED)

# ============================================================================
# COMBINE & VALIDATE
# ============================================================================

print("\n" + "-"*80)
print("STEP 3: COMBINE & VALIDATE")
print("-"*80)

df_timeseries = pd.concat(snapshots, ignore_index=True)

print(f"\n✓ Combined time-series data:")
print(f"  Total rows: {len(df_timeseries):,}")
print(f"  Unique products: {df_timeseries['product_id'].nunique():,}")
print(f"  Months: {df_timeseries['snapshot_month'].nunique()}")
print(f"  Expected rows: {len(df_base) * NUM_MONTHS:,}")

# Validation checks
print(f"\n  Data quality checks:")
missing_months = df_timeseries.groupby('product_id')['snapshot_month'].count()
if (missing_months != NUM_MONTHS).any():
    print(f"    ⚠ Warning: {(missing_months != NUM_MONTHS).sum()} products missing some months")
else:
    print(f"    ✓ All products have {NUM_MONTHS} monthly snapshots")

print(f"    ✓ Price range: ₹{df_timeseries['discounted_price_clean'].min():.2f} - ₹{df_timeseries['discounted_price_clean'].max():.2f}")
print(f"    ✓ Rating range: {df_timeseries['avg_rating'].min():.2f} - {df_timeseries['avg_rating'].max():.2f}★")
print(f"    ✓ Categories: {df_timeseries['category_lvl2'].nunique()}")

# ============================================================================
# SAVE OUTPUT
# ============================================================================

print("\n" + "-"*80)
print("STEP 4: SAVE OUTPUT")
print("-"*80)

output_file = Path(__file__).parent / 'product_performance_timeseries.csv'
df_timeseries.to_csv(output_file, index=False)

print(f"\n✓ Saved to: {output_file.name}")
print(f"  Size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")

# Save summary stats
summary_file = Path(__file__).parent / 'timeseries_summary.txt'
with open(summary_file, 'w') as f:
    f.write("MONTHLY TIME-SERIES DATA SUMMARY\n")
    f.write("="*80 + "\n\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Source: {input_file.name}\n")
    f.write(f"Output: {output_file.name}\n\n")
    
    f.write(f"Time Period:\n")
    f.write(f"  Start: {START_MONTH}\n")
    f.write(f"  Months: {NUM_MONTHS}\n")
    f.write(f"  End: {generate_month_label(START_MONTH, NUM_MONTHS-1)}\n\n")
    
    f.write(f"Data Dimensions:\n")
    f.write(f"  Total rows: {len(df_timeseries):,}\n")
    f.write(f"  Unique products: {df_timeseries['product_id'].nunique():,}\n")
    f.write(f"  Categories: {df_timeseries['category_lvl2'].nunique()}\n\n")
    
    f.write(f"Monthly Metrics (Average):\n")
    for month in sorted(df_timeseries['snapshot_month'].unique()):
        df_m = df_timeseries[df_timeseries['snapshot_month'] == month]
        f.write(f"\n  {month}:\n")
        f.write(f"    Products: {len(df_m):,}\n")
        f.write(f"    Avg Price: ₹{df_m['discounted_price_clean'].mean():.2f}\n")
        f.write(f"    Avg Discount: {df_m['discount_percentage_clean'].mean():.1f}%\n")
        f.write(f"    Avg Rating: {df_m['avg_rating'].mean():.2f}★\n")
        f.write(f"    Total Reviews: {df_m['rating_count_clean'].sum():,}\n")

print(f"✓ Saved summary to: {summary_file.name}")

print("\n" + "="*80)
print("✓ SNAPSHOT GENERATION COMPLETE")
print("="*80)
print("\nNext step: Run monthly_aggregates.py to create category/overall metrics")
print("\nCOST: $0.00 (no API calls)")
