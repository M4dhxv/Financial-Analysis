#!/usr/bin/env python3
"""
GENERIC VARIANCE CALCULATOR
Calculates period-over-period variance for any metric in canonical format.

Works with ANY dataset - no hardcoded column names.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import Dict, List, Tuple, Any

print("="*80)
print("GENERIC VARIANCE CALCULATOR")
print("="*80)

def load_inputs(canonical_file: str, registry_file: str) -> Tuple[pd.DataFrame, Dict]:
    """Load canonical data and metric registry."""
    df_canonical = pd.read_csv(canonical_file)
    
    with open(registry_file, 'r') as f:
        metric_registry = json.load(f)
    
    return df_canonical, metric_registry


def calculate_variance(df_canonical: pd.DataFrame, metric_registry: Dict) -> pd.DataFrame:
    """
    Calculate period-over-period variance for all metrics.
    
    Returns wide-format DataFrame with columns:
    - entity
    - period
    - metric_name
    - current_value
    - prior_value
    - delta_absolute
    - delta_percentage
    """
    
    print("\n📊 Calculating variance...")
    
    all_variance = []
    
    # Get unique entities and metrics
    entities = df_canonical['entity'].unique()
    metrics = df_canonical['metric_name'].unique()
    
    print(f"  Processing {len(entities):,} entities × {len(metrics)} metrics...")
    
    for metric in metrics:
        # Filter to this metric
        df_metric = df_canonical[df_canonical['metric_name'] == metric].copy()
        
        # Pivot to wide format (entity × period)
        pivot = df_metric.pivot_table(
            index='entity',
            columns='period',
            values='metric_value',
            aggfunc='first'
        )
        
        # Sort periods chronologically
        periods = sorted(pivot.columns)
        
        # Calculate variance for each consecutive period pair
        for i in range(1, len(periods)):
            current_period = periods[i]
            prior_period = periods[i-1]
            
            if current_period not in pivot.columns or prior_period not in pivot.columns:
                continue
            
            # Calculate deltas
            current_val = pivot[current_period]
            prior_val = pivot[prior_period]
            
            delta_abs = current_val - prior_val
            delta_pct = ((current_val - prior_val) / prior_val * 100).replace([np.inf, -np.inf], np.nan)
            
            # Create variance records
            for entity in pivot.index:
                if pd.notna(current_val[entity]) and pd.notna(prior_val[entity]):
                    all_variance.append({
                        'entity': entity,
                        'metric_name': metric,
                        'current_period': current_period,
                        'prior_period': prior_period,
                        'current_value': current_val[entity],
                        'prior_value': prior_val[entity],
                        'delta_absolute': delta_abs[entity],
                        'delta_percentage': delta_pct[entity]
                    })
    
    df_variance = pd.DataFrame(all_variance)
    
    print(f"  ✓ Calculated {len(df_variance):,} variance records")
    
    return df_variance


def decompose_revenue_variance(df_variance: pd.DataFrame, 
                               df_canonical: pd.DataFrame,
                               metric_registry: Dict) -> pd.DataFrame:
    """
    Apply price × volume decomposition to revenue-like metrics.
    
    Formula: ΔRevenue = (ΔPrice × Volume₀) + (ΔVolume × Price₀) + interaction
    """
    
    print("\n🔬 Applying price × volume decomposition...")
    
    # Find decomposable metrics
    decomposable = [m for m, info in metric_registry.items() if info.get('is_decomposable', False)]
    
    if not decomposable:
        print("  ℹ️  No decomposable metrics found (would need revenue/sales metrics)")
        return df_variance
    
    print(f"  Decomposable metrics: {decomposable}")
    
    # Find potential price and volume metrics
    price_metrics = [m for m, info in metric_registry.items() 
                    if info.get('driver_category') == 'price']
    volume_metrics = [m for m, info in metric_registry.items() 
                     if info.get('driver_category') == 'volume']
    
    print(f"  Price metrics: {price_metrics}")
    print(f"  Volume metrics: {volume_metrics}")
    
    # Add decomposition columns
    df_variance['price_effect'] = np.nan
    df_variance['volume_effect'] = np.nan
    df_variance['interaction_effect'] = np.nan
    
    # For each decomposable metric, try to find matching price/volume
    decomposition_count = 0
    
    for rev_metric in decomposable:
        # This is a simplified approach - in reality you'd need business logic
        # to map revenue metric → its corresponding price + volume metrics
        
        if price_metrics and volume_metrics:
            # Use first available price and volume metrics as proxies
            price_metric = price_metrics[0]
            vol_metric = volume_metrics[0]
            
            # Get variance for these metrics
            rev_var = df_variance[df_variance['metric_name'] == rev_metric]
            price_var = df_variance[df_variance['metric_name'] == price_metric]
            vol_var = df_variance[df_variance['metric_name'] == vol_metric]
            
            # For matching entity-periods, calculate decomposition
            for idx, row in rev_var.iterrows():
                entity = row['entity']
                curr_per = row['current_period']
                prior_per = row['prior_period']
                
                # Find matching price and volume rows
                price_row = price_var[
                    (price_var['entity'] == entity) &
                    (price_var['current_period'] == curr_per) &
                    (price_var['prior_period'] == prior_per)
                ]
                
                vol_row = vol_var[
                    (vol_var['entity'] == entity) &
                    (vol_var['current_period'] == curr_per) &
                    (vol_var['prior_period'] == prior_per)
                ]
                
                if not price_row.empty and not vol_row.empty:
                    # Extract values
                    price_curr = price_row.iloc[0]['current_value']
                    price_prior = price_row.iloc[0]['prior_value']
                    vol_curr = vol_row.iloc[0]['current_value']
                    vol_prior = vol_row.iloc[0]['prior_value']
                    
                    # Calculate effects
                    delta_price = price_curr - price_prior
                    delta_vol = vol_curr - vol_prior
                    
                    price_effect = delta_price * vol_prior
                    volume_effect = delta_vol * price_prior
                    interaction = delta_price * delta_vol
                    
                    # Update variance record
                    df_variance.loc[idx, 'price_effect'] = price_effect
                    df_variance.loc[idx, 'volume_effect'] = volume_effect
                    df_variance.loc[idx, 'interaction_effect'] = interaction
                    
                    decomposition_count += 1
    
    if decomposition_count > 0:
        print(f"  ✓ Applied decomposition to {decomposition_count} records")
    
    return df_variance


def save_variance_results(df_variance: pd.DataFrame, output_dir: Path):
    """Save variance results to CSV and JSON."""
    
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Save full variance table
    csv_file = output_dir / "variance_analysis.csv"
    df_variance.to_csv(csv_file, index=False)
    print(f"\n💾 Saved variance CSV: {csv_file}")
    
    # Save summary statistics
    latest_period = df_variance['current_period'].max()
    latest_variance = df_variance[df_variance['current_period'] == latest_period]
    
    summary = {
        'latest_period': str(latest_period),
        'total_variance_records': len(df_variance),
        'entities_analyzed': df_variance['entity'].nunique(),
        'metrics_analyzed': df_variance['metric_name'].nunique(),
        'top_movers': latest_variance.nlargest(10, 'delta_absolute')[
            ['entity', 'metric_name', 'delta_absolute', 'delta_percentage']
        ].to_dict('records')
    }
    
    json_file = output_dir / "variance_summary.json"
    with open(json_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"💾 Saved variance summary: {json_file}")


def run_variance_analysis(canonical_file: str, registry_file: str, output_dir: str):
    """Main entry point for variance analysis."""
    
    # Load inputs
    df_canonical, metric_registry = load_inputs(canonical_file, registry_file)
    
    print(f"\n📂 Input Statistics:")
    print(f"  Canonical rows: {len(df_canonical):,}")
    print(f"  Unique periods: {df_canonical['period'].nunique()}")
    print(f"  Unique entities: {df_canonical['entity'].nunique():,}")
    print(f"  Unique metrics: {df_canonical['metric_name'].nunique()}")
    
    # Calculate variance
    df_variance = calculate_variance(df_canonical, metric_registry)
    
    # Apply decomposition
    df_variance = decompose_revenue_variance(df_variance, df_canonical, metric_registry)
    
    # Save results
    save_variance_results(df_variance, Path(output_dir))
    
    print("\n" + "="*80)
    print("✅ VARIANCE ANALYSIS COMPLETE")
    print("="*80)
    print(f"\n💰 Cost: $0.00 (no API calls)")
    
    return df_variance


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate variance on canonical format data')
    parser.add_argument('--canonical', required=True, help='Path to canonical_data.csv')
    parser.add_argument('--registry', required=True, help='Path to metric_registry.json')
    parser.add_argument('--output', default='variance_analysis', help='Output directory')
    
    args = parser.parse_args()
    
    try:
        run_variance_analysis(args.canonical, args.registry, args.output)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
