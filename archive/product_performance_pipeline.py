"""
LAYER 1: PRODUCT PERFORMANCE TABLE BUILDER
A deterministic, explainable foundation for business performance analysis
No forecasting, no ML, no recommendations - pure data engineering
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path

# ============================================================================
# DOWNLOAD DATASET
# ============================================================================

import kagglehub
# Download latest version
path = kagglehub.dataset_download("karkavelrajaj/amazon-sales-dataset")
print("Path to dataset files:", path)

# Find the CSV file
dataset_path = Path(path)
csv_files = list(dataset_path.glob("*.csv"))
if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {path}")

data_file = csv_files[0]
print(f"Loading data from: {data_file}")

# Load raw data
df_raw = pd.read_csv(data_file)
print(f"\nRaw data shape: {df_raw.shape}")
print(f"Columns: {list(df_raw.columns)}")

# ============================================================================
# STEP 1: DATA UNDERSTANDING
# ============================================================================

print("\n" + "="*80)
print("STEP 1: DATA UNDERSTANDING")
print("="*80)

# Identify grain
print("\n1. DATASET GRAIN:")
print(f"   Total rows: {len(df_raw):,}")
print(f"   Unique products: {df_raw['product_id'].nunique():,}")
print(f"   Rows per product (avg): {len(df_raw) / df_raw['product_id'].nunique():.2f}")
print("\n   GRAIN: Review-level (multiple reviews per product)")

# Column classification
print("\n2. COLUMN CLASSIFICATION:")
print("\n   PRODUCT-LEVEL (constant within product_id):")
product_cols = ['product_id', 'product_name', 'category', 'actual_price', 
                'discounted_price', 'discount_percentage', 'img_link', 'product_link']
for col in product_cols:
    if col in df_raw.columns:
        print(f"   - {col}")

print("\n   REVIEW-LEVEL (varies within product_id):")
review_cols = ['user_id', 'user_name', 'review_id', 'review_title', 
               'review_content', 'rating', 'rating_count']
for col in review_cols:
    if col in df_raw.columns:
        print(f"   - {col}")

print("\n3. WHY AGGREGATION IS REQUIRED:")
print("   - Dataset contains repeated product attributes across multiple review rows")
print("   - Analysis requires ONE ROW PER PRODUCT for performance metrics")
print("   - Review-level data must be aggregated to product-level to avoid:")
print("     * Double-counting product attributes")
print("     * Incorrect category-level benchmarks")
print("     * Inflated product counts in reporting")

# ============================================================================
# STEP 2: DATA CLEANING
# ============================================================================

print("\n" + "="*80)
print("STEP 2: DATA CLEANING")
print("="*80)

df = df_raw.copy()

def clean_price(price_str):
    """Convert price string to numeric, handling currency symbols and commas"""
    if pd.isna(price_str):
        return np.nan
    # Remove currency symbols (₹, $, etc.) and commas
    clean = str(price_str).replace('₹', '').replace('$', '').replace(',', '').strip()
    try:
        return float(clean)
    except:
        return np.nan

def clean_percentage(pct_str):
    """Convert percentage string to numeric"""
    if pd.isna(pct_str):
        return np.nan
    clean = str(pct_str).replace('%', '').strip()
    try:
        return float(clean)
    except:
        return np.nan

def clean_numeric(value):
    """Convert to numeric, handling various formats"""
    if pd.isna(value):
        return np.nan
    try:
        return float(value)
    except:
        return np.nan

print("\n1. CLEANING PRICE COLUMNS:")
df['actual_price_clean'] = df['actual_price'].apply(clean_price)
df['discounted_price_clean'] = df['discounted_price'].apply(clean_price)
print(f"   - actual_price: {df['actual_price_clean'].notna().sum():,} / {len(df):,} valid")
print(f"   - discounted_price: {df['discounted_price_clean'].notna().sum():,} / {len(df):,} valid")

print("\n2. CLEANING DISCOUNT PERCENTAGE:")
df['discount_percentage_clean'] = df['discount_percentage'].apply(clean_percentage)
print(f"   - discount_percentage: {df['discount_percentage_clean'].notna().sum():,} / {len(df):,} valid")

print("\n3. CLEANING RATING COLUMNS:")
df['rating_clean'] = df['rating'].apply(clean_numeric)
df['rating_count_clean'] = df['rating_count'].apply(clean_numeric)
print(f"   - rating: {df['rating_clean'].notna().sum():,} / {len(df):,} valid")
print(f"   - rating_count: {df['rating_count_clean'].notna().sum():,} / {len(df):,} valid")

print("\n4. HANDLING MISSING VALUES:")
print("   ASSUMPTION: Conservative approach - retain all rows")
print("   RATIONALE: Missing values will be handled during aggregation")
print("   - Products with no valid prices: will have NaN in price metrics")
print("   - Products with no valid ratings: will have NaN in rating metrics")
print("   - This preserves maximum data for other analyses")

missing_before = len(df)
# Only drop if absolutely necessary (e.g., no product_id)
df = df.dropna(subset=['product_id'])
missing_after = len(df)
print(f"   - Rows dropped (missing product_id): {missing_before - missing_after}")

# ============================================================================
# STEP 3: CATEGORY NORMALIZATION
# ============================================================================

print("\n" + "="*80)
print("STEP 3: CATEGORY NORMALIZATION")
print("="*80)

def parse_category(category_str):
    """Split category into hierarchical levels"""
    if pd.isna(category_str):
        return [None, None, None, None]
    
    # Split by common delimiters
    parts = str(category_str).split('|')
    if len(parts) == 1:
        parts = str(category_str).split('>')
    if len(parts) == 1:
        parts = str(category_str).split('&')
    
    # Clean and pad
    parts = [p.strip() for p in parts]
    while len(parts) < 4:
        parts.append(None)
    
    return parts[:4]

print("\n1. PARSING CATEGORY HIERARCHY:")
category_parsed = df['category'].apply(parse_category)
df['category_lvl1'] = category_parsed.apply(lambda x: x[0])
df['category_lvl2'] = category_parsed.apply(lambda x: x[1])
df['category_lvl3'] = category_parsed.apply(lambda x: x[2])
df['category_lvl4'] = category_parsed.apply(lambda x: x[3])

print(f"   - category_lvl1: {df['category_lvl1'].nunique()} unique values")
print(f"   - category_lvl2: {df['category_lvl2'].nunique()} unique values")
print(f"   - category_lvl3: {df['category_lvl3'].nunique()} unique values")
print(f"   - category_lvl4: {df['category_lvl4'].nunique()} unique values")

print("\n2. ORIGINAL CATEGORY COLUMN RETAINED:")
print(f"   - category (original): {df['category'].nunique()} unique values")

# ============================================================================
# STEP 4: PRODUCT-LEVEL AGGREGATION
# ============================================================================

print("\n" + "="*80)
print("STEP 4: PRODUCT-LEVEL AGGREGATION")
print("="*80)

print("\n1. AGGREGATION STRATEGY:")
print("   Grouping by: product_id")
print("   Target: ONE ROW PER PRODUCT")

# Calculate review-level metrics before aggregation
print("\n2. CALCULATING REVIEW-LEVEL METRICS:")

# Review length
df['review_length'] = df['review_content'].fillna('').astype(str).str.len()

# Keyword matching (case-insensitive)
price_keywords = r'\b(price|cost|expensive|cheap|afford|worth|value|money)\b'
quality_keywords = r'\b(quality|excellent|good|bad|poor|great|terrible)\b'
durability_keywords = r'\b(durable|durability|last|lasting|break|broke|broken|sturdy|fragile)\b'

df['mentions_price'] = df['review_content'].fillna('').astype(str).str.lower().str.contains(price_keywords, regex=True).astype(int)
df['mentions_quality'] = df['review_content'].fillna('').astype(str).str.lower().str.contains(quality_keywords, regex=True).astype(int)
df['mentions_durability'] = df['review_content'].fillna('').astype(str).str.lower().str.contains(durability_keywords, regex=True).astype(int)

print("   - Review length calculated")
print("   - Price mentions identified (keywords: price, cost, expensive, cheap, afford, worth, value, money)")
print("   - Quality mentions identified (keywords: quality, excellent, good, bad, poor, great, terrible)")
print("   - Durability mentions identified (keywords: durable, last, break, sturdy, fragile)")

# Aggregation function
print("\n3. AGGREGATING TO PRODUCT LEVEL:")

agg_dict = {
    # Product attributes (take first - should be constant)
    'product_name': 'first',
    'category': 'first',
    'category_lvl1': 'first',
    'category_lvl2': 'first',
    'category_lvl3': 'first',
    'category_lvl4': 'first',
    'img_link': 'first',
    'product_link': 'first',
    
    # Pricing metrics
    'actual_price_clean': 'first',  # Should be constant per product
    'discounted_price_clean': 'first',
    'discount_percentage_clean': 'first',
    
    # Rating metrics
    'rating_clean': 'mean',  # Average of review ratings
    'rating_count_clean': 'first',  # Total rating count (should be constant)
    
    # Review metrics
    'review_id': 'count',  # Count of reviews
    'review_length': 'mean',
    'mentions_price': 'sum',
    'mentions_quality': 'sum',
    'mentions_durability': 'sum',
}

# Add std for rating if possible
df_product = df.groupby('product_id').agg({
    **agg_dict,
    'rating_clean': ['mean', 'std']
}).reset_index()

# Flatten column names
df_product.columns = [col[0] if col[1] in ('', 'first') else '_'.join(col).strip('_') 
                       for col in df_product.columns.values]

# Rename for clarity
df_product = df_product.rename(columns={
    'review_id_count': 'review_count',
    'rating_clean_mean': 'avg_rating',
    'rating_clean_std': 'rating_std',
    'review_length_mean': 'avg_review_length',
    'mentions_price_sum': 'reviews_mentioning_price',
    'mentions_quality_sum': 'reviews_mentioning_quality',
    'mentions_durability_sum': 'reviews_mentioning_durability',
})

print(f"   Products aggregated: {len(df_product):,}")

# Calculate derived metrics
print("\n4. CALCULATING DERIVED METRICS:")

# Absolute discount
df_product['absolute_discount'] = (df_product['actual_price_clean'] - 
                                    df_product['discounted_price_clean'])

# Percentage metrics for review intelligence
df_product['percent_reviews_mentioning_price'] = (
    df_product['reviews_mentioning_price'] / df_product['review_count'] * 100
)
df_product['percent_reviews_mentioning_quality'] = (
    df_product['reviews_mentioning_quality'] / df_product['review_count'] * 100
)
df_product['percent_reviews_mentioning_durability'] = (
    df_product['reviews_mentioning_durability'] / df_product['review_count'] * 100
)

print("   ✓ absolute_discount = actual_price - discounted_price")
print("   ✓ percent_reviews_mentioning_price")
print("   ✓ percent_reviews_mentioning_quality")
print("   ✓ percent_reviews_mentioning_durability")

# ============================================================================
# STEP 5: CATEGORY BENCHMARKS
# ============================================================================

print("\n" + "="*80)
print("STEP 5: CATEGORY BENCHMARKS")
print("="*80)

print("\n1. CALCULATING CATEGORY-LEVEL BENCHMARKS:")
print("   Using: category_lvl2 (most granular consistent level)")

# Calculate benchmarks at category_lvl2
category_benchmarks = df_product.groupby('category_lvl2').agg({
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

print(f"   Categories with benchmarks: {len(category_benchmarks):,}")
print("\n   Benchmark metrics:")
print("   - median_price")
print("   - median_discount_percentage")
print("   - median_rating")
print("   - median_rating_count")

# Join back to product table
print("\n2. JOINING BENCHMARKS TO PRODUCT TABLE:")
df_product = df_product.merge(category_benchmarks, on='category_lvl2', how='left')
print(f"   ✓ Benchmarks joined to {len(df_product):,} products")

# ============================================================================
# STEP 6: RELATIVE PERFORMANCE METRICS
# ============================================================================

print("\n" + "="*80)
print("STEP 6: RELATIVE PERFORMANCE METRICS")
print("="*80)

print("\n1. CALCULATING RELATIVE METRICS:")

# Price vs category median (% difference)
df_product['price_vs_category_median'] = (
    (df_product['discounted_price_clean'] - df_product['median_price']) / 
    df_product['median_price'] * 100
)

# Discount vs category median (% difference)
df_product['discount_vs_category_median'] = (
    (df_product['discount_percentage_clean'] - df_product['median_discount_percentage']) / 
    df_product['median_discount_percentage'] * 100
)

# Rating vs category median (absolute difference)
df_product['rating_vs_category_median'] = (
    df_product['avg_rating'] - df_product['median_rating']
)

# Rating count vs category median (% difference)
df_product['rating_count_vs_category_median'] = (
    (df_product['rating_count_clean'] - df_product['median_rating_count']) / 
    df_product['median_rating_count'] * 100
)

print("   ✓ price_vs_category_median (% difference)")
print("   ✓ discount_vs_category_median (% difference)")
print("   ✓ rating_vs_category_median (absolute difference)")
print("   ✓ rating_count_vs_category_median (% difference)")

# ============================================================================
# STEP 7: OUTPUT
# ============================================================================

print("\n" + "="*80)
print("STEP 7: OUTPUT")
print("="*80)

# Define final schema
final_columns = [
    # Identifiers
    'product_id',
    'product_name',
    
    # Category hierarchy
    'category',
    'category_lvl1',
    'category_lvl2',
    'category_lvl3',
    'category_lvl4',
    
    # Pricing metrics
    'actual_price_clean',
    'discounted_price_clean',
    'discount_percentage_clean',
    'absolute_discount',
    
    # Demand & sentiment metrics
    'avg_rating',
    'rating_count_clean',
    'rating_std',
    'review_count',
    
    # Review intelligence
    'avg_review_length',
    'percent_reviews_mentioning_price',
    'percent_reviews_mentioning_quality',
    'percent_reviews_mentioning_durability',
    
    # Category benchmarks
    'median_price',
    'median_discount_percentage',
    'median_rating',
    'median_rating_count',
    
    # Relative performance
    'price_vs_category_median',
    'discount_vs_category_median',
    'rating_vs_category_median',
    'rating_count_vs_category_median',
    
    # Links
    'img_link',
    'product_link',
]

df_final = df_product[final_columns].copy()

print("\n1. FINAL PRODUCT-LEVEL TABLE SCHEMA:")
print(f"\n   Total columns: {len(final_columns)}")
print(f"   Total products: {len(df_final):,}")
print("\n   COLUMN GROUPS:")

print("\n   IDENTIFIERS (2 columns):")
print("   - product_id, product_name")

print("\n   CATEGORY HIERARCHY (5 columns):")
print("   - category, category_lvl1, category_lvl2, category_lvl3, category_lvl4")

print("\n   PRICING METRICS (4 columns):")
print("   - actual_price_clean, discounted_price_clean")
print("   - discount_percentage_clean, absolute_discount")

print("\n   DEMAND & SENTIMENT METRICS (4 columns):")
print("   - avg_rating, rating_count_clean, rating_std, review_count")

print("\n   REVIEW INTELLIGENCE (4 columns):")
print("   - avg_review_length")
print("   - percent_reviews_mentioning_price")
print("   - percent_reviews_mentioning_quality")
print("   - percent_reviews_mentioning_durability")

print("\n   CATEGORY BENCHMARKS (4 columns):")
print("   - median_price, median_discount_percentage")
print("   - median_rating, median_rating_count")

print("\n   RELATIVE PERFORMANCE (4 columns):")
print("   - price_vs_category_median, discount_vs_category_median")
print("   - rating_vs_category_median, rating_count_vs_category_median")

print("\n   LINKS (2 columns):")
print("   - img_link, product_link")

# Display sample rows
print("\n2. SAMPLE ROWS (5 products):")
print("\n" + "-"*120)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)
pd.set_option('display.max_colwidth', 30)

sample = df_final.head(5)
print(sample.to_string(index=False))
print("-"*120)

# Summary statistics
print("\n3. DATA QUALITY SUMMARY:")
print(f"\n   Product-level records: {len(df_final):,}")
print(f"   Products with valid pricing: {df_final['discounted_price_clean'].notna().sum():,}")
print(f"   Products with valid ratings: {df_final['avg_rating'].notna().sum():,}")
print(f"   Products with reviews: {df_final['review_count'].gt(0).sum():,}")
print(f"   Average reviews per product: {df_final['review_count'].mean():.2f}")

# ============================================================================
# USAGE AS FOUNDATION FOR "WHY DID PERFORMANCE CHANGE?" SYSTEM
# ============================================================================

print("\n" + "="*80)
print("HOW THIS TABLE ENABLES AUTOMATED PERFORMANCE CHANGE ANALYSIS")
print("="*80)

print("""
FOUNDATION FOR DETERMINISTIC PERFORMANCE DIAGNOSTICS:

This product-level table provides the foundation for a time-series based
performance change detection and attribution system. Here's how:

1. TEMPORAL EXTENSION:
   - Append a 'snapshot_date' column
   - Run this pipeline daily/weekly to create historical snapshots
   - Structure: (product_id, snapshot_date) -> all metrics
   
2. CHANGE DETECTION:
   - Compare current period vs prior period for each product
   - Calculate delta for all numeric metrics:
     * Δ avg_rating
     * Δ review_count  
     * Δ price_vs_category_median
     * Δ percent_reviews_mentioning_quality
   
3. PERFORMANCE ATTRIBUTION (Deterministic Logic):
   - IF Δ avg_rating < -0.5 AND Δ percent_reviews_mentioning_quality > 10:
     → "Performance decline driven by quality concerns in reviews"
   
   - IF Δ review_count > 50 AND Δ rating_vs_category_median > 0:
     → "Performance improvement driven by increased engagement and above-category ratings"
   
   - IF Δ price_vs_category_median > 20 AND Δ review_count < -10:
     → "Performance decline potentially driven by relative price increase"

4. CATEGORY-RELATIVE ANALYSIS:
   - All relative metrics automatically adjust for category-level shifts
   - Example: If entire category median_price increases 15%, but product
     price_vs_category_median stays constant, product maintained competitive positioning
   
5. REVIEW INTELLIGENCE SIGNALS:
   - Track Δ percent_reviews_mentioning_price as early warning for price sensitivity
   - Track Δ percent_reviews_mentioning_durability for product quality issues
   - Cross-reference with Δ rating_std to detect polarization

6. EXPLAINABILITY:
   - Every metric is directly calculable from source data
   - No black-box ML models
   - Stakeholders can validate logic by inspecting raw reviews
   - Attribution rules are explicit IF-THEN statements

7. AUTOMATED REPORTING STRUCTURE:
   Product X performance change:
   - Primary metric: avg_rating declined 0.8 stars
   - Contributing factors:
     * percent_reviews_mentioning_quality increased 15%
     * rating_std increased from 0.5 to 1.2 (increased polarization)
     * review_count stable (not a sample size issue)
   - Category context: 
     * rating_vs_category_median declined 0.3 (outpaced by competitors)
   - Recommended investigation: Manual review of recent reviews mentioning "quality"

8. FINANCIAL-STYLE RIGOR:
   - Like a balance sheet: every figure ties to underlying transaction data
   - Like variance analysis: actual vs benchmark with explicit drivers
   - Like a cash flow statement: changes decomposed into identifiable components
   
This is NOT a recommendation engine. It is a diagnostic framework that
surfaces factual changes in observable metrics and provides structured
context for human investigation.
""")

# Save output
output_file = 'product_performance_table.csv'
df_final.to_csv(output_file, index=False)
print(f"\n✓ Final table saved to: {output_file}")

print("\n" + "="*80)
print("PIPELINE COMPLETE")
print("="*80)
