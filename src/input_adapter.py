"""
INPUT ADAPTER - Schema-Agnostic Input Detection
Automatically detects column types from any CSV/Excel file.

NO HARDCODED COLUMN NAMES - Pure inference based on data characteristics.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import Dict, List, Tuple, Any
import re

print("="*80)
print("INPUT ADAPTER - SCHEMA DETECTION")
print("="*80)

class SchemaDetector:
    """Automatically detects time, entity, and measure columns."""
    
    def __init__(self, df: pd.DataFrame, sheet_name: str = "default"):
        self.df = df
        self.sheet_name = sheet_name
        self.schema_map = {
            'time_column': None,
            'entity_columns': [],
            'measure_columns': [],
            'text_columns': [],
            'excluded_columns': []
        }
    
    def detect_time_column(self) -> str:
        """Identify the time/period column."""
        candidates = []
        
        for col in self.df.columns:
            col_lower = str(col).lower()
            
            # Check column name patterns
            time_keywords = ['date', 'month', 'year', 'period', 'time', 'quarter', 'week', 'day']
            if any(kw in col_lower for kw in time_keywords):
                candidates.append((col, 3.0))  # High priority
                continue
            
            # Check data type
            if pd.api.types.is_datetime64_any_dtype(self.df[col]):
                candidates.append((col, 2.5))
                continue
            
            # Check if parseable as date
            try:
                pd.to_datetime(self.df[col].head(10))
                candidates.append((col, 2.0))
                continue
            except:
                pass
            
            # Check for YYYY-MM pattern
            if self.df[col].dtype == 'object':
                sample = str(self.df[col].iloc[0])
                if re.match(r'\d{4}-\d{2}', sample):
                    candidates.append((col, 2.5))
        
        if candidates:
            # Sort by score
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return None
    
    def detect_entity_columns(self) -> List[str]:
        """Identify grouping/entity columns (category, product, department, etc.)."""
        entities = []
        
        for col in self.df.columns:
            if col == self.schema_map['time_column']:
                continue
            
            col_lower = str(col).lower()
            
            # Check for entity keywords
            entity_keywords = ['category', 'product', 'department', 'account', 
                             'region', 'segment', 'group', 'type', 'class',
                             'id', 'name', 'code']
            
            if any(kw in col_lower for kw in entity_keywords):
                entities.append(col)
                continue
            
            # Check cardinality (low cardinality = likely entity)
            if self.df[col].dtype in ['object', 'string']:
                nunique = self.df[col].nunique()
                total = len(self.df)
                
                # If < 20% unique values, likely categorical entity
                if nunique / total < 0.2 and nunique > 1:
                    entities.append(col)
        
        return entities
    
    def detect_measure_columns(self) -> List[str]:
        """Identify numeric measure columns."""
        measures = []
        
        for col in self.df.columns:
            if col == self.schema_map['time_column']:
                continue
            if col in self.schema_map['entity_columns']:
                continue
            
            # Must be numeric
            if pd.api.types.is_numeric_dtype(self.df[col]):
                # Skip ID-like columns (mostly unique integers)
                if self.df[col].dtype in ['int64', 'int32']:
                    nunique = self.df[col].nunique()
                    if nunique / len(self.df) > 0.8:  # High cardinality int = ID
                        continue
                
                measures.append(col)
        
        return measures
    
    def detect_text_columns(self) -> List[str]:
        """Identify text/description columns."""
        text_cols = []
        
        for col in self.df.columns:
            if col == self.schema_map['time_column']:
                continue
            if col in self.schema_map['entity_columns']:
                continue
            if col in self.schema_map['measure_columns']:
                continue
            
            # High-cardinality text columns
            if self.df[col].dtype == 'object':
                nunique = self.df[col].nunique()
                if nunique / len(self.df) > 0.5:  # High cardinality = descriptions
                    text_cols.append(col)
        
        return text_cols
    
    def detect_schema(self) -> Dict[str, Any]:
        """Run full schema detection."""
        print(f"\n🔍 Analyzing schema for: {self.sheet_name}")
        print(f"  Total columns: {len(self.df.columns)}")
        print(f"  Total rows: {len(self.df)}")
        
        # Step 1: Detect time column
        self.schema_map['time_column'] = self.detect_time_column()
        print(f"\n  ✓ Time column: {self.schema_map['time_column']}")
        
        # Step 2: Detect entity columns
        self.schema_map['entity_columns'] = self.detect_entity_columns()
        print(f"  ✓ Entity columns: {self.schema_map['entity_columns']}")
        
        # Step 3: Detect measure columns
        self.schema_map['measure_columns'] = self.detect_measure_columns()
        print(f"  ✓ Measure columns ({len(self.schema_map['measure_columns'])}): {self.schema_map['measure_columns'][:5]}...")
        
        # Step 4: Detect text columns
        self.schema_map['text_columns'] = self.detect_text_columns()
        print(f"  ✓ Text columns: {self.schema_map['text_columns']}")
        
        return self.schema_map


def load_and_detect(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Load file and detect schema.
    Supports CSV and Excel (including multi-sheet).
    """
    file_path = Path(file_path)
    
    print(f"\n📂 Loading file: {file_path.name}")
    
    if file_path.suffix.lower() in ['.xlsx', '.xls']:
        # Excel file - check for multiple sheets
        excel_file = pd.ExcelFile(file_path)
        sheets = excel_file.sheet_names
        
        print(f"  Excel file with {len(sheets)} sheet(s): {sheets}")
        
        # For now, use first sheet (can extend to multi-sheet)
        df = pd.read_excel(file_path, sheet_name=sheets[0])
        sheet_name = sheets[0]
        
    elif file_path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path)
        sheet_name = "csv_data"
        
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    print(f"  Loaded {len(df):,} rows × {len(df.columns)} columns")
    
    # Detect schema
    detector = SchemaDetector(df, sheet_name=sheet_name)
    schema_map = detector.detect_schema()
    
    return df, schema_map


def save_schema_map(schema_map: Dict[str, Any], output_path: str):
    """Save detected schema to JSON for inspection."""
    with open(output_path, 'w') as f:
        json.dump(schema_map, f, indent=2)
    print(f"\n💾 Schema map saved to: {output_path}")


# ============================================================================
# DEMO - Run on existing data
# ============================================================================

if __name__ == "__main__":
    # Test on our existing time-series data
    input_file = Path(__file__).parent / 'product_performance_timeseries.csv'
    
    if input_file.exists():
        df, schema_map = load_and_detect(str(input_file))
        
        # Save schema
        save_schema_map(schema_map, 
                       str(Path(__file__).parent / 'detected_schema.json'))
        
        print("\n" + "="*80)
        print("✅ SCHEMA DETECTION COMPLETE")
        print("="*80)
        print("\nDetected Structure:")
        print(f"  Time: {schema_map['time_column']}")
        print(f"  Entities: {len(schema_map['entity_columns'])} columns")
        print(f"  Measures: {len(schema_map['measure_columns'])} columns")
        print(f"  Text: {len(schema_map['text_columns'])} columns")
        
        print("\n🎯 This schema can now drive the entire pipeline!")
        print("   No hardcoded column names needed.")
    else:
        print(f"\n⚠️  Test file not found: {input_file}")
        print("   Run monthly_snapshot_generator.py first, or provide your own CSV/Excel file.")
