# Quick Start Guide

Get started with the Universal Financial Reporting Engine in 5 minutes!

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/financial-reporting-engine.git
cd financial-reporting-engine
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

That's it! You're ready to go.

## Your First Report

### Example 1: Analyze ANY CSV File

```bash
python3 src/run_universal_pipeline.py --input your_data.csv
```

The system will:
1. Auto-detect your schema (time, entities, metrics)
2. Normalize your data
3. Calculate variance
4. Generate charts
5. Create a PDF report

**Output**: `your_data_report/financial_report.pdf`

### Example 2: Specify Output Directory

```bash
python3 src/run_universal_pipeline.py --input data.csv --output my_analysis
```

**Output**: `my_analysis/financial_report.pdf`

### Example 3: Try the Examples

```bash
# Use the included example data
python3 src/run_universal_pipeline.py --input examples/financial_accounting/input.csv
```

## Understanding the Output

After running the pipeline, you'll find:

```
your_data_report/
├── financial_report.pdf        ← 📄 MAIN REPORT (open this!)
├── financial_report.md          ← Text version
├── charts/                      ← All visualizations
│   ├── trend_revenue.png
│   ├── variance_top_movers.png
│   └── heatmap_*.png
├── variance_analysis.csv        ← Detailed calculations (Excel-compatible)
├── canonical_data.csv           ← Normalized data
└── detected_schema.json         ← What the system detected
```

### What's in the PDF?

1. **Executive Summary** - Top 5 changes at a glance
2. **Visual Analysis** - 6+ embedded charts
3. **Metric Analysis** - Per-metric variance breakdown
4. **Methodology** - How the analysis was done

## Common Use Cases

### Financial Accounting
```bash
python3 src/run_universal_pipeline.py --input gl_export.csv
```

### Sales Performance
```bash
python3 src/run_universal_pipeline.py --input sales_data.xlsx
```

### Operations Metrics
```bash
python3 src/run_universal_pipeline.py --input kpi_dashboard.csv
```

### HR Analytics
```bash
python3 src/run_universal_pipeline.py --input headcount.csv
```

## Data Requirements

Your data should have:
✅ **Time column** - Dates or periods (e.g., "2024-01", "Jan-24", "2024-01-15")
✅ **One or more entity columns** - Categories, products, regions, accounts, etc.
✅ **One or more metric columns** - Numbers to analyze (revenue, units, count, etc.)

### Supported Formats
- CSV files (.csv)
- Excel files (.xlsx, .xls)

### Example Data Structure

**Option 1: Wide Format** (most common)
```
Date       | Product | Revenue | Units | Margin
2024-01-01 | Widget  | 10000   | 100   | 0.25
2024-02-01 | Widget  | 12000   | 120   | 0.26
```

**Option 2: Already Normalized**
```
period   | entity           | metric  | value
2024-01  | Product:Widget   | Revenue | 10000
2024-01  | Product:Widget   | Units   | 100
```

Both work! The system auto-detects and adapts.

## Troubleshooting

### "No time column detected"
- Ensure you have a column with dates or period strings
- Common formats: "2024-01", "2024-01-15", "Jan 2024"

### "No metrics found"
- Make sure you have numeric columns to analyze
- Text-only files won't work (need numbers!)

### "Module not found"
```bash
# Make sure you installed requirements
pip install -r requirements.txt
```

### Charts not showing in PDF
- Check that `charts/` directory was created
- Verify matplotlib/seaborn are installed
- Try regenerating: `rm -rf your_data_report && rerun`

## What's Next?

- [User Manual](USER_MANUAL.md) - Complete feature guide
- [Architecture](ARCHITECTURE.md) - How it works under the hood
- [Examples](../examples/) - More sample datasets
- [API Reference](API_REFERENCE.md) - Module documentation

## Quick Reference

```bash
# Full pipeline (recommended)
python3 src/run_universal_pipeline.py --input data.csv

# Just analysis (no charts/PDF)
python3 src/analyze_data.py --input data.csv

# Specify output location
python3 src/run_universal_pipeline.py --input data.csv --output my_reports/

# Help
python3 src/run_universal_pipeline.py --help
```

## Performance

- **Small files** (<10K rows): ~5 seconds
- **Medium files** (10K-100K rows): ~15-30 seconds
- **Large files** (100K-1M rows): ~60-120 seconds

## Cost

**$0.00** - No API calls, no cloud services, fully local.

---

**Need help?** Open an issue on GitHub or check the [User Manual](USER_MANUAL.md)!
