#!/usr/bin/env python3
"""
CHART REGISTRY - Track generated charts for embedding in reports
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class ChartRegistry:
    """Manages chart generation tracking and manifest."""
    
    def __init__(self, output_dir: str = "charts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.charts = []
        self.manifest_file = self.output_dir / "chart_registry.json"
    
    def register_chart(self, 
                      chart_type: str,
                      metric_name: str,
                      file_path: str,
                      **metadata):
        """Register a generated chart."""
        
        chart_entry = {
            'chart_type': chart_type,
            'metric_name': metric_name,
            'file_path': str(file_path),
            'generated_at': datetime.now().isoformat(),
            **metadata
        }
        
        self.charts.append(chart_entry)
        print(f"  ✓ Registered: {chart_type} for {metric_name}")
    
    def save_manifest(self):
        """Save chart manifest to JSON."""
        manifest = {
            'total_charts': len(self.charts),
            'generated_at': datetime.now().isoformat(),
            'charts': self.charts
        }
        
        with open(self.manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n💾 Chart manifest saved: {self.manifest_file}")
        return self.manifest_file
    
    def get_chart_path(self, metric_name: str, chart_type: str = None) -> str:
        """Get path to a specific chart."""
        for chart in self.charts:
            if chart['metric_name'] == metric_name:
                if chart_type is None or chart['chart_type'] == chart_type:
                    return chart['file_path']
        return None
    
    def list_charts(self) -> List[Dict]:
        """Get list of all charts."""
        return self.charts


if __name__ == "__main__":
    # Demo
    registry = ChartRegistry("test_charts")
    registry.register_chart("trend", "Revenue", "charts/revenue_trend.png", periods=12)
    registry.register_chart("waterfall", "Revenue", "charts/revenue_waterfall.png")
    registry.save_manifest()
    print(f"\n✅ Registry created with {len(registry.charts)} charts")
