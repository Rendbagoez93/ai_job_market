# AI Job Market Analysis

A comprehensive data analysis project for exploring and analyzing AI job market trends, skills, salaries, and employment patterns.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Data Pipeline](#data-pipeline)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Contributing](#contributing)

## 🎯 Overview

This project provides a robust, modular pipeline for analyzing AI job market data. It includes data loading, cleaning, validation, enrichment, and visualization capabilities with a focus on scalability and maintainability.

### Key Highlights

- **2,000+ job postings** analyzed across multiple industries
- **70+ enriched features** including salary clusters, skills parsing, location analysis
- **Modular architecture** with reusable utility classes
- **Configuration-driven** behavior for easy customization
- **Comprehensive logging** throughout the pipeline

## ✨ Features

### Data Processing
- ✅ **Load**: Read raw CSV data with validation
- ✅ **Clean**: Remove duplicates, handle missing values, standardize text
- ✅ **Validate**: Check data quality, types, ranges, and completeness
- ✅ **Enrich**: Parse and cluster salaries, skills, tools, locations, dates

### Enrichment Categories
- **Salary**: Min/max/average, salary clusters (7 brackets), salary per skill
- **Skills**: Top 20 skills as binary features, skill counts, programming/cloud/ML flags
- **Tools**: Top 15 tools as binary features, tool counts
- **Experience**: Ordinal encoding (Entry=1, Mid=2, Senior=3)
- **Location**: City, state, clusters, USA vs International classification
- **Date**: Year, month, quarter, day of week, aging feature (5 categories)
- **Employment**: Type flags (remote, full-time, contract, internship)
- **Company**: Size and industry flags

### Analysis Capabilities
- Exploratory Data Analysis (EDA)
- Statistical summaries
- Trend analysis
- Correlation studies
- Visualization support

## 📁 Project Structure

```
ai_job_market/
├── config/                      # Configuration files
│   ├── config.yaml             # Main configuration
│   ├── paths.yaml              # File paths and data processing settings
│   └── logging.yaml            # Logging configuration
├── data/                       # Data directory
│   ├── raw/                    # Raw data files
│   │   └── ai_job_market.csv
│   ├── cleaned/                # Cleaned data
│   │   └── ai_job_market_cleaned.csv
│   ├── enriched/               # Enriched data by category
│   │   ├── salary_enriched.csv
│   │   ├── skills_enriched.csv
│   │   ├── tools_enriched.csv
│   │   ├── experience_enriched.csv
│   │   ├── location_enriched.csv
│   │   ├── date_enriched.csv
│   │   ├── employment_enriched.csv
│   │   └── company_enriched.csv
│   └── dictionary/             # Data dictionaries and mappings
│       ├── skill_frequency.csv
│       ├── tool_frequency.csv
│       ├── location_frequency.csv
│       └── column_mapping.json
├── src/                        # Source code
│   ├── data/                   # Data processing pipelines
│   │   ├── load_data.py       # DataLoader class
│   │   ├── clean_data.py      # DataCleaningPipeline class
│   │   ├── validate.py        # DataValidationPipeline class
│   │   └── enrich.py          # DataEnrichmentPipeline class
│   ├── utils/                  # Utility modules
│   │   ├── config_loader.py   # Configuration management
│   │   ├── logger.py          # Logging setup
│   │   ├── file_handler.py    # File I/O operations
│   │   ├── data_validator.py  # Data validation
│   │   ├── data_cleaner.py    # Data cleaning
│   │   ├── enrichers.py       # Feature enrichers
│   │   ├── constant.py        # Constants
│   │   └── helpers.py         # Helper functions
│   ├── visuals/               # Visualization modules
│   └── predictions/           # ML/prediction modules
├── notebooks/                 # Jupyter notebooks
├── output/                    # Output files and logs
├── dashboards/                # Dashboard files
├── v1/                        # Version 1 legacy code
├── pyproject.toml            # Project dependencies
├── ARCHITECTURE.md           # Detailed architecture documentation
└── README.md                 # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.13+
- `uv` package manager (recommended) or `pip`

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_job_market
   ```

2. **Install dependencies with uv** (recommended)
   ```bash
   uv sync
   ```

   Or with pip:
   ```bash
   pip install -e .
   ```

3. **Verify installation**
   ```bash
   uv run python src/data/load_data.py
   ```

## 📖 Usage

### Quick Start

Run the complete data pipeline:

```bash
# 1. Load raw data
uv run python src/data/load_data.py

# 2. Validate data
uv run python src/data/validate.py

# 3. Clean data
uv run python src/data/clean_data.py

# 4. Enrich data (generates 8 category files)
uv run python src/data/enrich.py
```

### Python API

```python
# Load and validate data
from data import load_raw_data, validate_data

df_raw = load_raw_data()
validation_results = validate_data(df_raw)

# Clean data
from data import clean_data, save_cleaned_data

df_cleaned = clean_data(df_raw)
save_cleaned_data(df_cleaned)

# Enrich data
from data import DataEnrichmentPipeline

pipeline = DataEnrichmentPipeline()
df = pipeline.load_cleaned_data()
df_enriched = pipeline.enrich_data(df)
pipeline.save_enriched_data(df_enriched)
```

### Custom Workflows

```python
# Custom cleaning with method chaining
from utils import DataCleaner, FileHandler

handler = FileHandler()
df = handler.load_csv('data/raw/ai_job_market.csv')

cleaner = DataCleaner(df)
df_clean = (cleaner
    .remove_duplicates()
    .handle_missing_values(strategy='drop')
    .standardize_text(['company_name'], lowercase=True)
    .get_cleaned_data())

# Custom enrichment
from utils.enrichers import SalaryEnricher, SkillsEnricher

salary_enricher = SalaryEnricher(df_clean)
df_enriched = salary_enricher.enrich()

skills_enricher = SkillsEnricher(df_enriched, top_n=30)
df_enriched, skill_counts = skills_enricher.enrich()
```

## 🔄 Data Pipeline

### 1. Data Loading
- Reads raw CSV with configurable encoding and delimiter
- Validates expected columns
- Performs basic data checks
- Logs data shape and statistics

### 2. Data Validation
- Column presence validation
- Data type checking
- Missing value detection
- Duplicate detection
- Range validation
- Generates validation reports

### 3. Data Cleaning
- Removes duplicates (0 found in current dataset)
- Handles missing values (none found in current dataset)
- Standardizes text formatting
- Filters rows based on conditions
- Converts data types
- Generates cleaning reports

### 4. Data Enrichment
Transforms raw data into 8 enriched category files:

| Category | Columns | Description |
|----------|---------|-------------|
| **Salary** | 10 | Parsed ranges, clusters, averages, per-skill metrics |
| **Skills** | 29 | Top 20 skills binary features, counts, category flags |
| **Tools** | 14 | Top 15 tools binary features, counts |
| **Experience** | 6 | Ordinal encoding of experience levels |
| **Location** | 9 | Parsed city/state, clusters, USA/International |
| **Date** | 14 | Date components, aging feature, clusters |
| **Employment** | 9 | Type flags for remote, full-time, contract, internship |
| **Company** | 10 | Size and industry flags |

**Common columns**: `job_id`, `company_name`, `industry`, `job_title` appear in all enriched files for easy joining.

## ⚙️ Configuration

### Main Configuration (`config/config.yaml`)
- Project metadata
- Column definitions (raw, categorical, numerical, date, text)
- Analysis settings (statistics, EDA, feature engineering)
- Visualization settings
- Export and performance settings

### Paths Configuration (`config/paths.yaml`)
- Directory paths for all data folders
- File paths for raw, cleaned, enriched data
- Data processing settings (loading, cleaning, validation, enrichment)

### Logging Configuration (`config/logging.yaml`)
- Log formatters (simple, detailed)
- Handlers (console, rotating file)
- Log levels and output destinations

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed technical architecture, design patterns, and API documentation
- **Code Comments**: Inline documentation throughout the codebase
- **Type Hints**: Full type annotations for better IDE support

## 🛠️ Development

### Design Patterns Used
- **Singleton Pattern**: ConfigLoader for centralized config management
- **Fluent Interface**: DataCleaner with method chaining
- **Strategy Pattern**: Different cleaning/enrichment strategies
- **Pipeline Pattern**: Sequential data processing steps

### Key Utility Classes
- `ConfigLoader`: Centralized configuration management
- `FileHandler`: Robust file I/O operations
- `DataValidator`: Comprehensive data validation
- `DataCleaner`: Fluent interface for data cleaning
- `Enrichers`: Specialized enrichment classes per category

### Running Tests
```bash
# Test individual modules
uv run python src/data/load_data.py
uv run python src/data/clean_data.py
uv run python src/data/validate.py
uv run python src/data/enrich.py
```

## 📊 Dataset Information

### Source Data
- **Rows**: 2,000 job postings
- **Columns**: 12 original columns
- **Period**: 2023-2025
- **Industries**: Tech, Finance, Healthcare, Automotive, E-commerce, Education
- **Job Titles**: Data Analyst, ML Engineer, AI Product Manager, Data Scientist, etc.

### Data Quality
- ✅ No missing values
- ✅ No duplicates
- ✅ All expected columns present
- ✅ Data types validated
- ✅ Date ranges valid

### Enriched Output
- **Total Features**: 74 columns in full enriched dataset
- **Category Files**: 8 separate files for modular analysis
- **Data Dictionaries**: Frequency tables and mapping files included

## 🤝 Contributing

### Adding New Features

1. **New Enricher**: Create a class in `src/utils/enrichers.py`
   ```python
   class MyEnricher:
       def __init__(self, df: pd.DataFrame):
           self.df = df.copy()
       
       def enrich(self) -> pd.DataFrame:
           # Your enrichment logic
           return self.df
   ```

2. **New Validation Rule**: Add method to `DataValidator` class

3. **New Cleaning Strategy**: Add method to `DataCleaner` class

4. **New Pipeline Step**: Update respective pipeline class in `src/data/`

## 📝 License

This project is for educational and analysis purposes.

## 👥 Authors

- Your Name

## 🙏 Acknowledgments

- Data source: AI Job Market Dataset
- Built with: Python, Pandas, PyYAML, and UV package manager

---

**Last Updated**: December 9, 2025  
**Version**: 0.1.0  
**Python**: 3.13+
