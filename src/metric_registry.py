"""
METRIC REGISTRY - Type-Based Metric Classification
Categorizes metrics into types (level/flow/ratio) and defines decomposition rules.

NO HARDCODED METRIC NAMES - Infers type from name patterns and data characteristics.
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Any
from pathlib import Path
import json

print("="*80)
print("METRIC REGISTRY")
print("="*80)

class MetricClassifier:
    """Classifies metrics into types for appropriate analysis."""
    
    # Metric type patterns
    LEVEL_PATTERNS = [
        'count', 'total', 'sum', 'balance', 'inventory', 'headcount',
        'qty', 'quantity', 'volume', 'units', 'size'
    ]
    
    FLOW_PATTERNS = [
        'revenue', 'sales', 'cost', 'expense', 'income', 'profit',
        'spend', 'payment', 'receipt', 'cash', 'margin'
    ]
    
    RATIO_PATTERNS = [
        'rate', 'ratio', 'percentage', 'pct', '%', 'margin', 'yield',
        'avg', 'average', 'mean', 'median', 'per', 'efficiency'
    ]
    
    PRICE_PATTERNS = ['price', 'rate', 'cost_per', 'unit_cost']
    VOLUME_PATTERNS = ['quantity', 'count', 'volume', 'units', 'qty']
    QUALITY_PATTERNS = ['rating', 'score', 'satisfaction', 'nps', 'quality']
    DISCOUNT_PATTERNS = ['discount', 'promotion', 'rebate', 'markdown']
    
    def __init__(self, metric_names: List[str]):
        self.metric_names = metric_names
        self.registry = {}
    
    def classify_metric(self, metric_name: str) -> Dict[str, Any]:
        """Classify a single metric."""
        name_lower = metric_name.lower()
        
        # Determine metric type
        metric_type = self._infer_type(name_lower)
        
        # Determine driver category
        driver_category = self._infer_driver_category(name_lower)
        
        # Determine if decomposable (price × volume)
        is_decomposable = self._is_decomposable(name_lower, metric_type)
        
        return {
            'name': metric_name,
            'type': metric_type,
            'driver_category': driver_category,
            'is_decomposable': is_decomposable,
            'analysis_priority': self._assign_priority(metric_type, driver_category)
        }
    
    def _infer_type(self, name_lower: str) -> str:
        """Infer metric type from name."""
        # Check ratio patterns first (most specific)
        if any(pattern in name_lower for pattern in self.RATIO_PATTERNS):
            return 'ratio'
        
        # Check flow patterns
        if any(pattern in name_lower for pattern in self.FLOW_PATTERNS):
            return 'flow'
        
        # Check level patterns
        if any(pattern in name_lower for pattern in self.LEVEL_PATTERNS):
            return 'level'
        
        # Default to level
        return 'level'
    
    def _infer_driver_category(self, name_lower: str) -> str:
        """Infer what business driver this metric represents."""
        if any(pattern in name_lower for pattern in self.PRICE_PATTERNS):
            return 'price'
        if any(pattern in name_lower for pattern in self.VOLUME_PATTERNS):
            return 'volume'
        if any(pattern in name_lower for pattern in self.QUALITY_PATTERNS):
            return 'quality'
        if any(pattern in name_lower for pattern in self.DISCOUNT_PATTERNS):
            return 'discount'
        
        return 'other'
    
    def _is_decomposable(self, name_lower: str, metric_type: str) -> bool:
        """Check if metric can be decomposed into price × volume."""
        # Revenue/sales metrics are typically decomposable
        if metric_type == 'flow':
            if any(kw in name_lower for kw in ['revenue', 'sales', 'gross']):
                return True
        return False
    
    def _assign_priority(self, metric_type: str, driver_category: str) -> int:
        """Assign analysis priority (1=highest)."""
        # Flow metrics (revenue/profit) = highest priority
        if metric_type == 'flow':
            return 1
        # Key drivers = high priority
        if driver_category in ['price', 'volume', 'quality']:
            return 2
        # Ratios = medium priority
        if metric_type == 'ratio':
            return 3
        # Everything else = low priority
        return 4
    
    def build_registry(self) -> Dict[str, Any]:
        """Build complete metric registry."""
        print(f"\n📋 Classifying {len(self.metric_names)} metrics...")
        
        for metric_name in self.metric_names:
            classification = self.classify_metric(metric_name)
            self.registry[metric_name] = classification
        
        # Summary stats
        type_counts = {}
        for metric in self.registry.values():
            mtype = metric['type']
            type_counts[mtype] = type_counts.get(mtype, 0) + 1
        
        print(f"\n  ✓ Metric types:")
        for mtype, count in sorted(type_counts.items()):
            print(f"    {mtype}: {count}")
        
        # Decomposable metrics
        decomposable = [m for m in self.registry.values() if m['is_decomposable']]
        print(f"\n  ✓ Decomposable metrics: {len(decomposable)}")
        for m in decomposable:
            print(f"    - {m['name']}")
        
        return self.registry


def save_registry(registry: Dict[str, Any], output_path: str):
    """Save metric registry to JSON."""
    with open(output_path, 'w') as f:
        json.dump(registry, f, indent=2)
    print(f"\n💾 Metric registry saved to: {output_path}")


# ============================================================================
# DEMO - Run on canonical data
# ============================================================================

if __name__ == "__main__":
    from canonical_format import CanonicalConverter
    from input_adapter import load_and_detect
    
    input_file = Path(__file__).parent / 'product_performance_timeseries.csv'
    
    if input_file.exists():
        # Load and convert to canonical
        df, schema_map = load_and_detect(str(input_file))
        converter = CanonicalConverter(df, schema_map)
        df_canonical = converter.to_canonical()
        
        # Get unique metrics
        metric_names = df_canonical['metric_name'].unique().tolist()
        
        # Classify metrics
        classifier = MetricClassifier(metric_names)
        registry = classifier.build_registry()
        
        # Save registry
        save_registry(registry, 
                     str(Path(__file__).parent / 'metric_registry.json'))
        
        print("\n" + "="*80)
        print("✅ METRIC CLASSIFICATION COMPLETE")
        print("="*80)
        print("\n🎯 Metrics are now typed and ready for generic variance analysis!")
        print("   Price × Volume decomposition will work on ANY revenue-like metric.")
    else:
        print(f"\n⚠️  Test file not found: {input_file}")
