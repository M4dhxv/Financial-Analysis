# Financial Reporting Engine - Project Structure

```
financial-reporting-engine/
├── README.md                          ← Main documentation
├── LICENSE                            ← MIT License
├── requirements.txt                   ← Python dependencies
├── .gitignore                         ← Git ignore rules
│
├── src/                               ← Source code
│   ├── __init__.py
│   ├── input_adapter.py               ← Schema detection
│   ├── canonical_format.py            ← Data normalization
│   ├── metric_registry.py             ←  Metric classification
│   ├── generic_variance.py            ← Variance calculation
│   ├── chart_generator.py             ← Chart generation
│   ├── chart_registry.py              ← Chart tracking
│   ├── report_generator_universal.py  ← Markdown reports
│   ├── pdf_report_builder.py          ← PDF generation
│   ├── analyze_data.py                ← CLI for analysis
│   └── run_universal_pipeline.py      ← Main orchestrator
│
├── docs/                              ← Documentation
│   ├── QUICK_START.md                 ← 5-minute guide
│   ├── USER_MANUAL.md                 ← Complete usage guide
│   ├── ARCHITECTURE.md                ← Technical design
│   ├── API_REFERENCE.md               ← Module documentation
│   └── CONTRIBUTING.md                ← Contribution guidelines
│
├── examples/                          ← Example datasets & outputs
│   ├── financial_accounting/
│   │   ├── input.csv
│   │   └── expected_output/
│   ├── sales_data/
│   │   ├── input.csv
│   │   └── expected_output/
│   └── README.md
│
└── tests/                             ← Test suite
    ├── test_input_adapter.py
    ├── test_canonical_format.py
    ├── test_variance.py
    └── README.md
```

## File Organization

### Core Modules (`src/`)

All production code lives in the `src/` directory:

- **Input Processing**: `input_adapter.py`, `canonical_format.py`
- **Analysis**: `metric_registry.py`, `generic_variance.py`
- **Visualization**: `chart_generator.py`, `chart_registry.py`
- **Reporting**: `report_generator_universal.py`, `pdf_report_builder.py`
- **Orchestration**: `run_universal_pipeline.py`, `analyze_data.py`

### Documentation (`docs/`)

Comprehensive documentation for users and developers:

- **Quick Start**: Get running in 5 minutes
- **User Manual**: Complete feature guide
- **Architecture**: Technical design and decisions
- **API Reference**: Module-level documentation
- **Contributing**: How to contribute to the project

### Examples (`examples/`)

Real-world examples with sample data and expected outputs:

- Financial accounting data
- Sales performance data
- Operations metrics
- HR analytics

### Tests (`tests/`)

Unit and integration tests for all modules.

## Usage

From the project root:

```bash
# Run the complete pipeline
python3 src/run_universal_pipeline.py --input your_data.csv

# Or just analyze (no charts/PDF)
python3 src/analyze_data.py --input your_data.csv
```

## Development

To work on the code:

```bash
# Install in development mode
pip install -r requirements.txt
pip install -e .

# Run tests
python -m pytest tests/

# Check code quality
python -m pylint src/
```
