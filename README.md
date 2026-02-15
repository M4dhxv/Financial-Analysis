# Universal Financial Reporting Engine

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Cost: $0](https://img.shields.io/badge/cost-$0.00-green.svg)](/)

> **Transform ANY CSV/Excel file into professional financial reports with embedded charts in 30 seconds. Zero configuration required.**

## 🎯 What Is This?

A **schema-agnostic financial reporting engine** that automatically analyzes any monthly data and generates professional PDF reports with charts. Built for finance teams, analysts, and data scientists who need instant insights without manual configuration.

### Key Features

- ✅ **Universal Input**: Works with ANY CSV/Excel structure (sales, finance, operations, HR)
- ✅ **Auto-Detection**: Automatically identifies time, entities, and metrics
- ✅ **Variance Analysis**: Period-over-period changes with price × volume decomposition
- ✅ **Auto-Generated Charts**: 6+ visualizations (trends, heatmaps, distributions)
- ✅ **Professional PDFs**: Single consolidated report with embedded charts
- ✅ **Zero Cost**: No API calls, fully deterministic
- ✅ **Fast**: Complete analysis in ~30 seconds

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/financial-reporting-engine.git
cd financial-reporting-engine

# Install dependencies
pip install -r requirements.txt
```

### Usage (One Command!)

```bash
python3 run_universal_pipeline.py --input your_data.csv
```

That's it! Your PDF report will be in `your_data_report/financial_report.pdf`

### Example

```bash
# Analyze your financial accounting data
python3 run_universal_pipeline.py --input financial_data.csv

# Analyze sales performance
python3 run_universal_pipeline.py --input sales_data.xlsx

# Analyze ANY monthly metrics
python3 run_universal_pipeline.py --input operations_metrics.csv
```

## 📊 What You Get

After running the pipeline, you'll get:

```
your_data_report/
├── financial_report.pdf        ← 📄 YOUR MAIN REPORT (with embedded charts)
├── financial_report.md          ← Markdown version
├── charts/                      ← 📊 All visualizations
│   ├── trend_*.png
│   ├── variance_*.png
│   └── heatmap_*.png
├── variance_analysis.csv        ← Detailed calculations
├── canonical_data.csv           ← Normalized data
└── detected_schema.json         ← Auto-detected structure
```

### Sample Output

**Input**: 100,000 rows of financial accounting data  
**Time**: 29.6 seconds  
**Cost**: $0.00  
**Output**: Professional PDF with 6 embedded charts

## 🏗️ Architecture

The system follows a modular pipeline architecture:

```
CSV/Excel Input
      ↓
[Schema Detection] ← Auto-detects columns
      ↓
[Canonical Format] ← Normalizes to (period, entity, metric, value)
      ↓
[Variance Analysis] ← Calculates period-over-period changes
      ↓
[Chart Generation] ← Creates 6+ visualizations
      ↓
[PDF Builder] ← Embeds charts into professional report
      ↓
PDF Output (with embedded charts)
```

### Core Modules

| Module | Purpose | Lines of Code |
|--------|---------|---------------|
| `input_adapter.py` | Auto-detect schema from any file | 267 |
| `canonical_format.py` | Normalize to universal format | 226 |
| `metric_registry.py` | Classify metrics by type | 244 |
| `generic_variance.py` | Calculate variance | 280 |
| `chart_generator.py` | Generate visualizations | 290 |
| `pdf_report_builder.py` | Build PDF reports | 310 |
| `run_universal_pipeline.py` | Orchestrate everything | 180 |

**Total**: ~1,800 lines of production code

## 📖 Documentation

- [**Quick Start Guide**](docs/QUICK_START.md) - Get started in 5 minutes
- [**User Manual**](docs/USER_MANUAL.md) - Complete usage guide
- [**Architecture**](docs/ARCHITECTURE.md) - Technical design details
- [**API Reference**](docs/API_REFERENCE.md) - Module documentation
- [**Examples**](examples/) - Sample datasets and outputs

## 🔬 How It Works

### 1. Schema Detection (Auto-Magic!)

```python
# NO configuration needed - the system figures it out
Input: any_data.csv
✓ Detected time column: "Date"
✓ Detected entities: ["Account", "Category", "Region"]
✓ Detected metrics: ["Revenue", "Units", "Margin"]
```

### 2. Canonical Normalization

```python
# Converts ANY structure to universal format
Wide format (original):
  Date     | Product | Revenue | Units
  2024-01  | Widget  | 10000   | 100

Long format (canonical):
  period   | entity           | metric  | value
  2024-01  | Product:Widget   | Revenue | 10000
  2024-01  | Product:Widget   | Units   | 100
```

### 3. Variance Analysis

```python
# Automatic period-over-period analysis
- Month-over-month changes (absolute & %)
- Price × volume decomposition
- Top movers identification
- Statistical aggregation
```

### 4. Chart Generation

```python
# 6+ auto-generated visualizations
- Trend charts (metric over time)
- Variance bar charts (top movers)
- Heatmaps (entity × period grid)
- Distribution histograms
```

### 5. PDF Report

```python
# Professional PDF with embedded charts
- Executive summary
- Visual analysis (charts embedded)
- Detailed variance breakdown
- Methodology section
```

## 💡 Use Cases

### Finance Teams
- Monthly P&L variance analysis
- Budget vs. actuals reporting
- Revenue driver attribution
- Multi-entity consolidation

### Sales Analytics
- Regional performance tracking
- Product mix analysis
- Customer segmentation
- Pipeline velocity

### Operations
- KPI trending and monitoring
- Resource utilization
- Efficiency metrics
- Capacity planning

### HR Analytics
- Headcount reporting
- Compensation analysis
- Turnover tracking
- Department benchmarking

## 🆚 Comparison

| Feature | This Engine | Excel | BI Tools | Custom Code |
|---------|-------------|-------|----------|-------------|
| **Setup Time** | 0 min | 30-60 min | 2-4 hours | Days/Weeks |
| **Config Needed** | None | Manual | Extensive | Custom |
| **Cost** | $0 | License fee | $$$-$$$$ | Dev time |
| **Works with ANY data** | ✅ | ❌ | ⚠️ | ✅ |
| **Auto-generates charts** | ✅ | ❌ | ✅ | Depends |
| **PDF output** | ✅ | Manual | ⚠️ | Depends |
| **Reproducible** | ✅ | ❌ | ✅ | ✅ |
| **Auditable** | ✅ | ⚠️ | ⚠️ | ✅ |

## 🎓 Requirements

- Python 3.9+
- pandas
- numpy
- matplotlib
- seaborn  
- reportlab

See [requirements.txt](requirements.txt) for full list.

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/financial-reporting-engine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/financial-reporting-engine/discussions)

## 🌟 Star History

If this project helps you, please give it a star! ⭐

## 🙏 Acknowledgments

Built with:
- pandas for data manipulation
- matplotlib/seaborn for visualization  
- reportlab for PDF generation

---

**Made with ❤️ for financial analysts everywhere**

**Cost: $0.00** | **No API calls** | **100% deterministic** | **Fully auditable**
