"""
CANONICAL FORMAT - Long-Format Normalization
Converts any input data to canonical (period, entity, metric_name, metric_value) format.

This allows all downstream logic to be schema-agnostic.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from pathlib import Path

print("="*80)
print("CANONICAL FORMAT CONVERTER")
print("="*80)

class CanonicalConverter:
    """Converts wide-format data to long-format canonical structure."""
    
    def __init__(self, df: pd.DataFrame, schema_map: Dict[str, Any]):
        self.df = df
        self.schema = schema_map
        
    def to_canonical(self) -> pd.DataFrame:
        """
        Convert to canonical long format:
        Columns: [period, entity, metric_name, metric_value]
        
        Where:
        - period: Time dimension value
        - entity: Concatenated entity dimensions (e.g., "Category:Electronics|Product:Laptop")
        - metric_name: Name of the measure
        - metric_value: Numeric value of the measure
        """
        
        print("\n🔄 Converting to canonical format...")
        
        time_col = self.schema['time_column']
        entity_cols = self.schema['entity_columns']
        measure_cols = self.schema['measure_columns']
        
        if not time_col:
            raise ValueError("No time column detected - cannot create canonical format")
        
        if not measure_cols:
            raise ValueError("No measure columns detected - nothing to analyze")
        
        # Create entity key (concatenate all entity columns)
        if entity_cols:
            self.df['_entity_key'] = self.df[entity_cols].apply(
                lambda row: '|'.join([f"{col}:{val}" for col, val in zip(entity_cols, row)]),
                axis=1
            )
        else:
            self.df['_entity_key'] = 'Overall'  # No entities = overall level only
        
        # Melt to long format
        id_vars = [time_col, '_entity_key'] + entity_cols
        
        df_long = pd.melt(
            self.df,
            id_vars=id_vars,
            value_vars=measure_cols,
            var_name='metric_name',
            value_name='metric_value'
        )
        
        # Rename time column to standard 'period'
        df_long = df_long.rename(columns={time_col: 'period'})
        
        # Rename _entity_key to entity
        df_long = df_long.rename(columns={'_entity_key': 'entity'})
        
        # Keep individual entity columns for filtering
        canonical_cols = ['period', 'entity', 'metric_name', 'metric_value'] + entity_cols
        df_canonical = df_long[canonical_cols].copy()
        
        # Drop nulls
        df_canonical = df_canonical.dropna(subset=['metric_value'])
        
        print(f"  ✓ Canonical format created:")
        print(f"    Input: {len(self.df):,} rows × {len(self.df.columns)} cols")
        print(f"    Output: {len(df_canonical):,} rows × {len(df_canonical.columns)} cols")
        print(f"    Unique periods: {df_canonical['period'].nunique()}")
        print(f"    Unique entities: {df_canonical['entity'].nunique()}")
        print(f"    Unique metrics: {df_canonical['metric_name'].nunique()}")
        
        return df_canonical
    
    def from_canonical(self, df_canonical: pd.DataFrame) -> pd.DataFrame:
        """
        Convert back from canonical to wide format.
        Useful for final outputs and reports.
        """
        
        print("\n🔄 Converting from canonical back to wide format...")
        
        # Get entity column names (all cols except period, entity, metric_name, metric_value)
        entity_cols = [col for col in df_canonical.columns 
                      if col not in ['period', 'entity', 'metric_name', 'metric_value']]
        
        # Pivot back to wide
        pivot_cols = ['period'] + entity_cols
        
        df_wide = df_canonical.pivot_table(
            index=pivot_cols,
            columns='metric_name',
            values='metric_value',
            aggfunc='first'  # Should be one value per entity-period-metric
        ).reset_index()
        
        print(f"  ✓ Wide format restored:")
        print(f"    Input: {len(df_canonical):,} rows (long)")
        print(f"    Output: {len(df_wide):,} rows (wide)")
        
        return df_wide


def save_canonical(df_canonical: pd.DataFrame, output_path: str):
    """Save canonical format to CSV."""
    df_canonical.to_csv(output_path, index=False)
    print(f"\n💾 Canonical data saved to: {output_path}")


# ============================================================================
# DEMO - Run on existing data
# ============================================================================

if __name__ == "__main__":
    from input_adapter import load_and_detect
    
    input_file = Path(__file__).parent / 'product_performance_timeseries.csv'
    
    if input_file.exists():
        # Load and detect schema
        df, schema_map = load_and_detect(str(input_file))
        
        # Convert to canonical
        converter = CanonicalConverter(df, schema_map)
        df_canonical = converter.to_canonical()
        
        # Save
        save_canonical(df_canonical, 
                      str(Path(__file__).parent / 'canonical_data.csv'))
        
        # Show sample
        print("\n📊 Sample canonical data:")
        print(df_canonical.head(10).to_string(index=False))
        
        # Test conversion back
        df_wide = converter.from_canonical(df_canonical)
        print("\n📊 Sample wide data (restored):")
        print(df_wide.head(5))
        
        print("\n" + "="*80)
        print("✅ CANONICAL CONVERSION COMPLETE")
        print("="*80)
        print("\n🎯 All downstream modules can now work with canonical format!")
        print("   Schema-agnostic, structured, ready for variance analysis.")
    else:
        print(f"\n⚠️  Test file not found: {input_file}")
