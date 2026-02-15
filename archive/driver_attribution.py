"""
PHASE C: DRIVER ATTRIBUTION
Deterministic root-cause analysis for metric changes.

NO API CALLS - 100% rule-based logic.
Combines my impact scoring with ChatGPT's mathematical decomposition.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

print("="*80)
print("DRIVER ATTRIBUTION ENGINE")
print("="*80)

# ============================================================================
# LOAD VARIANCE DATA
# ============================================================================

print("\n" + "-"*80)
print("STEP 1: LOAD VARIANCE DATA")
print("-"*80)

df_var_cat = pd.read_csv(Path(__file__).parent / 'monthly_variance_category.csv')
print(f"✓ Category variances: {len(df_var_cat):,} rows")

# ============================================================================
# DRIVER ANALYSIS FUNCTIONS
# ============================================================================

def analyze_pricing_driver(row):
    """Price effect on revenue"""
    price_change_pct = row.get('avg_price_delta_pct', 0)
    price_effect = row.get('price_effect', 0)
    revenue_delta = row.get('total_revenue_proxy_delta_abs', 0)
    
    if abs(price_change_pct) > 5 and revenue_delta != 0:
        contribution_pct = (price_effect / revenue_delta * 100) if revenue_delta != 0 else 0
        
        return {
            'driver': 'pricing',
            'impact_score': abs(price_change_pct) * 2,
            'contribution_pct': contribution_pct,
            'narrative': f"Price {'increased' if price_change_pct > 0 else 'decreased'} {abs(price_change_pct):.1f}%, contributing {contribution_pct:.1f}% of revenue change"
        }
    return None

def analyze_volume_driver(row):
    """Volume effect on revenue"""
    volume_change_pct = row.get('total_review_count_delta_pct', 0)
    volume_effect = row.get('volume_effect', 0)
    revenue_delta = row.get('total_revenue_proxy_delta_abs', 0)
    
    if abs(volume_change_pct) > 10 and revenue_delta != 0:
        contribution_pct = (volume_effect / revenue_delta * 100) if revenue_delta != 0 else 0
        
        return {
            'driver': 'volume',
            'impact_score': abs(volume_change_pct),
            'contribution_pct': contribution_pct,
            'narrative': f"Demand volume {'increased' if volume_change_pct > 0 else 'decreased'} {abs(volume_change_pct):.1f}%, contributing {contribution_pct:.1f}% of revenue change"
        }
    return None

def analyze_discount_driver(row):
    """Discount promotional activity"""
    discount_change = row.get('avg_discount_percentage_delta_abs', 0)
    
    if abs(discount_change) > 5:
        return {
            'driver': 'discounting',
            'impact_score': abs(discount_change) * 3,
            'contribution_pct': None,  # Not directly calculable from revenue decomp
            'narrative': f"Discounting {'increased' if discount_change > 0 else 'decreased'} by {abs(discount_change):.1f}pp"
        }
    return None

def analyze_quality_driver(row):
    """Quality perception shift"""
    rating_change = row.get('avg_rating_weighted_delta_abs', 0)
    
    if abs(rating_change) > 0.1:
        return {
            'driver': 'quality',
            'impact_score': abs(rating_change) * 10,
            'contribution_pct': None,
            'narrative': f"Quality perception {'improved' if rating_change > 0 else 'declined'}: rating {' improved by' if rating_change > 0 else 'dropped'} {abs(rating_change):.2f} stars"
        }
    return None

def rank_drivers(drivers_list):
    """Rank drivers by impact score"""
    valid = [d for d in drivers_list if d is not None]
    
    if not valid:
        return [{
            'rank': 1,
            'driver': 'no_significant_change',
            'impact_score': 0,
            'narrative': 'No significant drivers identified'
        }]
    
    sorted_drivers = sorted(valid, key=lambda x: x['impact_score'], reverse=True)
    
    for i, driver in enumerate(sorted_drivers[:3], 1):
        driver['rank'] = i
    
    return sorted_drivers[:3]

# ============================================================================
# ANALYZE ALL CATEGORIES
# ============================================================================

print("\n" + "-"*80)
print("STEP 2: ANALYZE DRIVERS FOR ALL CATEGORIES")
print("-"*80)

all_attributions = []

for _, row in df_var_cat.iterrows():
    # Run all driver analyses
    drivers = [
        analyze_pricing_driver(row),
        analyze_volume_driver(row),
        analyze_discount_driver(row),
        analyze_quality_driver(row)
    ]
    
    # Rank drivers
    top_drivers = rank_drivers(drivers)
    
    # Create attribution record
    attribution = {
        'current_month': row['current_month'],
        'category': row['category_lvl2'],
        'primary_metric': {
            'kpi': 'revenue_proxy',
            'current_value': float(row['total_revenue_proxy_current']),
            'prior_value': float(row['total_revenue_proxy_prior']),
            'delta_abs': float(row['total_revenue_proxy_delta_abs']),
            'delta_pct': float(row['total_revenue_proxy_delta_pct']),
            'direction': row['total_revenue_proxy_direction']
        },
        'decomposition': {
            'price_effect': float(row.get('price_effect', 0)),
            'volume_effect': float(row.get('volume_effect', 0)),
            'interaction_effect': float(row.get('interaction_effect', 0))
        },
        'drivers': top_drivers
    }
    
    all_attributions.append(attribution)

print(f"✓ Analyzed {len(all_attributions)} category-month combinations")

# ============================================================================
# SAVE RESULTS
# ============================================================================

print("\n" + "-"*80)
print("STEP 3: SAVE ATTRIBUTION RESULTS")
print("-"*80)

# Save full attribution JSON
output_json = Path(__file__).parent / 'variance_drivers.json'
with open(output_json, 'w') as f:
    json.dump(all_attributions, f, indent=2)

print(f"✓ Saved full attribution to: {output_json.name}")

# Save latest month summary
latest_month = sorted(df_var_cat['current_month'].unique())[-1]
latest_attributions = [a for a in all_attributions if a['current_month'] == latest_month]

output_latest = Path(__file__).parent / 'variance_drivers_latest.json'
with open(output_latest, 'w') as f:
    json.dump(latest_attributions, f, indent=2)

print(f"✓ Saved latest month ({latest_month}) to: {output_latest.name}")

# Print sample
print(f"\n  Sample Driver Analysis ({latest_month}):")
for attr in latest_attributions[:3]:
    print(f"\n  Category: {attr['category']}")
    print(f"    Revenue: ₹{attr['primary_metric']['current_value']:.0f} ({attr['primary_metric']['delta_pct']:+.1f}%)")
    print(f"    Top Driver: {attr['drivers'][0]['narrative']}")

print("\n" + "="*80)
print("✓ DRIVER ATTRIBUTION COMPLETE")
print("="*80)
print("\nNext step: Run visualization_engine.py for charts")
print("\nCOST: $0.00 (no API calls)")
