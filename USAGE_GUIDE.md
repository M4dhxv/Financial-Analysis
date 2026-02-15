# HOW TO USE: Schema-Agnostic Analyzer

## 🚀 **Quick Start - Terminal Usage**

### **Basic Command:**

```bash
cd "/Users/madhavsharma/F:O model/FP&A model"
python3 analyze_data.py --input YOUR_FILE.csv
```

### **With Custom Output Directory:**

```bash
python3 analyze_data.py --input YOUR_FILE.xlsx --output results/
```

---

## 📝 **What It Does**

The analyzer automatically:

1. **Detects your schema** (no configuration needed!)
   - Identifies time/date columns
   - Finds entity/grouping columns (category, product, region, etc.)
   - Locates numeric measures
   - Classifies text fields

2. **Converts to canonical format**
   - Normalizes to: (period, entity, metric_name, metric_value)
   - Makes data ready for analysis

3. **Classifies metrics**
   - Level metrics (counts, quantities)
   - Flow metrics (revenue, costs)
   - Ratio metrics (percentages, averages)
   - Identifies decomposable metrics (price × volume)

4. **Generates analysis files**
   - `detected_schema.json` - Schema mappings
   - `canonical_data.csv` - Normalized data
   - `metric_registry.json` - Metric types
   - `analysis_summary.json` - Overall summary

---

## 💻 **Example 1: Analyze Existing Data**

```bash
cd "/Users/madhavsharma/F:O model/FP&A model"

# Analyze the time-series data
python3 analyze_data.py --input product_performance_timeseries.csv
```

**Output:**
```
✅ Analysis Summary:
  Input: product_performance_timeseries.csv
  Rows: 8,106
  Columns: 30

  Schema Detected:
    Time column: snapshot_month
    Entity columns: 13
    Measure columns: 16

  Canonical Format:
    Total rows: 115,512
    Periods: 6
    Entities: 8,072
    Metrics: 16

  Metric Classification:
    level: 6
    ratio: 10

📂 Output Files:
  ├── detected_schema.json
  ├── canonical_data.csv
  ├── metric_registry.json
  └── analysis_summary.json

📁 All files saved to: product_performance_timeseries_analysis/
```

---

## 💻 **Example 2: Analyze YOUR Data**

```bash
# Copy your CSV/Excel file to the FP&A folder (or use full path)
cp ~/Downloads/my_sales_data.xlsx "/Users/madhavsharma/F:O model/FP&A model/"

# Run analysis
cd "/Users/madhavsharma/F:O model/FP&A model"
python3 analyze_data.py --input my_sales_data.xlsx

# Check results
ls my_sales_data_analysis/
```

**Works with ANY structure:**
- Sales data (date, product, region, revenue, units)
- Finance data (period, account, department, actuals, budget)
- Operations data (week, facility, metric, value)
- HR data (month, department, headcount, cost)

---

## 📊 **Understanding the Output**

### **1. detected_schema.json**

Shows what columns were detected:

```json
{
  "time_column": "Month",
  "entity_columns": ["Region", "Product"],
  "measure_columns": ["Revenue", "Units", "Price"],
  "text_columns": []
}
```

**Use this to verify** the system correctly identified your columns.

### **2. canonical_data.csv**

Long-format normalized data:

```
period,entity,metric_name,metric_value
2024-01,Region:East|Product:Widget,Revenue,10000
2024-01,Region:East|Product:Widget,Units,100
...
```

**Use this for** variance analysis (coming in Phase 2).

### **3. metric_registry.json**

How metrics were classified:

```json
{
  "Revenue": {
    "type": "flow",
    "driver_category": "other",
    "is_decomposable": true,
    "analysis_priority": 1
  },
  "Units": {
    "type": "level",
    "driver_category": "volume",
    "is_decomposable": false,
    "analysis_priority": 2
  }
}
```

**Use this to understand** how variance analysis will work.

### **4. analysis_summary.json**

Overall statistics:

```json
{
  "input_file": "my_sales_data.xlsx",
  "rows_analyzed": 1200,
  "canonical_format": {
    "unique_periods": 12,
    "unique_entities": 100
  },
  "metrics": {
    "decomposable": ["Revenue", "Gross_Margin"]
  }
}
```

---

## 🎯 **Current Capabilities (Phase 1)**

✅ **Schema Detection** - Automatic column type identification  
✅ **Canonical Conversion** - Universal data normalization  
✅ **Metric Classification** - Type-based grouping  
✅ **Zero Configuration** - Works on any CSV/Excel  
✅ **Explainable** - All mappings saved to JSON  
✅ **Zero Cost** - No API calls  

---

## 🚧 **Coming Next (Phase 2)**

⏳ **Variance Analysis** - MoM/QoQ change calculation  
⏳ **Driver Attribution** - Price × volume decomposition  
⏳ **Chart Generation** - Auto-generated visualizations  
⏳ **PDF Report** - Single consolidated output  

---

## ❓ **FAQ**

**Q: What file formats are supported?**  
A: CSV (.csv) and Excel (.xlsx, .xls). Multi-sheet Excel uses first sheet.

**Q: Do I need to configure column names?**  
A: No! The system auto-detects everything.

**Q: What if detection is wrong?**  
A: Check `detected_schema.json` and you can manually edit the schema map if needed (advanced).

**Q: Can I analyze multiple files?**  
A: Yes, run the command multiple times:
```bash
python3 analyze_data.py --input sales_jan.csv --output jan_analysis/
python3 analyze_data.py --input sales_feb.csv --output feb_analysis/
```

**Q: Does this replace the original demo?**  
A: No! The original `run_demo.py` still works for the product performance dataset. This is a NEW capability for ANY data.

---

## 🎉 **Quick Test**

Try it right now with the existing data:

```bash
cd "/Users/madhavsharma/F:O model/FP&A model"
python3 analyze_data.py --input product_performance_timeseries.csv --output test_output/
```

You'll see it auto-detect 30 columns, create 115K canonical rows, and classify 16 metrics - all in ~2 seconds with $0 cost!

---

## 💡 **Pro Tip**

To see help and all options:

```bash
python3 analyze_data.py --help
```

To process your own data, just point it at any CSV/Excel:

```bash
python3 analyze_data.py --input ~/Desktop/my_monthly_data.xlsx
```

That's it! The system does the rest. 🚀
