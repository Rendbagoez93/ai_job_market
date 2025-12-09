# Refactored Code Architecture

## Overview
The codebase has been refactored into a modular, robust, and scalable architecture with clear separation of concerns.

## Directory Structure

```
src/
├── data/              # Data processing pipelines
│   ├── __init__.py
│   ├── load_data.py   # DataLoader class
│   ├── clean_data.py  # DataCleaningPipeline class
│   ├── validate.py    # DataValidationPipeline class
│   └── enrich.py      # DataEnrichmentPipeline class
│
└── utils/             # Reusable utility modules
    ├── __init__.py
    ├── config_loader.py    # ConfigLoader (singleton pattern)
    ├── logger.py           # Logger setup
    ├── file_handler.py     # FileHandler for I/O operations
    ├── data_validator.py   # DataValidator class
    ├── data_cleaner.py     # DataCleaner class (fluent interface)
    ├── enrichers.py        # Enricher classes per category
    ├── constant.py         # Constants and configurations
    └── helpers.py          # Helper functions
```

## Key Components

### 1. **Utils Module** (`src/utils/`)

#### ConfigLoader (`config_loader.py`)
- **Pattern**: Singleton
- **Purpose**: Centralized configuration management
- **Features**:
  - Lazy loading and caching of YAML configs
  - Path resolution helper methods
  - Thread-safe configuration access

```python
from utils import get_config_loader

config = get_config_loader()
value = config.get_config_value('columns.raw_columns')
path = config.get_path('paths.raw_data_file')
```

#### Logger (`logger.py`)
- **Purpose**: Centralized logging setup
- **Features**:
  - Configurable via logging.yaml
  - Named loggers for different modules
  - Automatic fallback to basic config

```python
from utils import get_logger

logger = get_logger(__name__)
logger.info("Processing data...")
```

#### FileHandler (`file_handler.py`)
- **Purpose**: File I/O operations
- **Features**:
  - CSV read/write with error handling
  - JSON read/write
  - Automatic directory creation
  - Logging integration

```python
from utils import FileHandler

handler = FileHandler()
df = handler.load_csv('data/raw/data.csv')
handler.save_csv(df, 'data/cleaned/data.csv')
```

#### DataValidator (`data_validator.py`)
- **Purpose**: Data quality validation
- **Features**:
  - Column validation
  - Data type checking
  - Missing value detection
  - Duplicate detection
  - Range validation
  - Comprehensive validation reports

```python
from utils import DataValidator

validator = DataValidator(df)
validator.validate_columns(expected_columns)
validator.check_missing_values()
summary = validator.get_summary()
```

#### DataCleaner (`data_cleaner.py`)
- **Pattern**: Fluent Interface / Method Chaining
- **Purpose**: Data cleaning operations
- **Features**:
  - Remove duplicates
  - Handle missing values (drop/fill/interpolate)
  - Filter rows
  - Convert data types
  - Standardize text
  - Generate cleaning reports

```python
from utils import DataCleaner

cleaner = DataCleaner(df)
df_clean = (cleaner
    .remove_duplicates()
    .handle_missing_values(strategy='drop')
    .standardize_text(['company_name', 'location'])
    .get_cleaned_data())

report = cleaner.get_report()
```

#### Enrichers (`enrichers.py`)
- **Purpose**: Specialized enrichment classes
- **Classes**:
  - `SalaryEnricher`: Parse and cluster salary ranges
  - `SkillsEnricher`: Parse skills, create binary features
  - `ToolsEnricher`: Parse tools, create binary features
  - `ExperienceEnricher`: Ordinal encoding
  - `LocationEnricher`: Parse and cluster locations
  - `DateEnricher`: Extract date features, aging
  - `AdditionalFeaturesEnricher`: Derived features

```python
from utils.enrichers import SalaryEnricher, SkillsEnricher

salary_enricher = SalaryEnricher(df)
df = salary_enricher.enrich()

skills_enricher = SkillsEnricher(df, top_n=20)
df, skill_counts = skills_enricher.enrich()
```

#### Constants (`constant.py`)
- **Purpose**: Centralized constants
- **Includes**:
  - Programming languages list
  - Cloud platforms list
  - ML frameworks list
  - US states list
  - Experience level mappings
  - Salary bins and labels
  - Age bins and labels
  - Common column names

#### Helpers (`helpers.py`)
- **Purpose**: Reusable utility functions
- **Functions**:
  - `parse_list_column()`: Parse delimited strings
  - `create_binary_features()`: Create binary indicator columns
  - `get_top_items()`: Get most frequent items
  - `safe_divide()`: Division with infinity/NaN handling
  - `map_experience_to_ordinal()`: Experience mapping
  - `identify_region()`: USA vs International
  - `extract_date_features()`: Extract date components
  - `get_numeric_summary()`: Numeric stats
  - `get_categorical_summary()`: Categorical stats

### 2. **Data Processing Module** (`src/data/`)

#### DataLoader (`load_data.py`)
- **Purpose**: Load raw and processed data
- **Methods**:
  - `load_raw_data()`: Load from CSV with validation
  - `load_cleaned_data()`: Load cleaned dataset
  - `load_enriched_data(category)`: Load enriched data by category

```python
from data import DataLoader

loader = DataLoader()
df_raw = loader.load_raw_data()
df_cleaned = loader.load_cleaned_data()
df_salary = loader.load_enriched_data('salary')
```

#### DataCleaningPipeline (`clean_data.py`)
- **Purpose**: End-to-end cleaning workflow
- **Methods**:
  - `clean_data(df)`: Apply cleaning operations
  - `save_cleaned_data(df)`: Save cleaned dataset

```python
from data import DataCleaningPipeline

pipeline = DataCleaningPipeline()
df_cleaned = pipeline.clean_data(df_raw)
pipeline.save_cleaned_data(df_cleaned)
```

#### DataValidationPipeline (`validate.py`)
- **Purpose**: Data validation workflow
- **Methods**:
  - `validate_data(df)`: Run all validations
  - Prints formatted validation report

```python
from data import DataValidationPipeline

pipeline = DataValidationPipeline()
results = pipeline.validate_data(df)
```

#### DataEnrichmentPipeline (`enrich.py`)
- **Purpose**: Feature engineering workflow
- **Methods**:
  - `load_cleaned_data()`: Load source data
  - `enrich_data(df)`: Apply all enrichment steps
  - `save_enriched_data(df)`: Save by category
  - `print_summary(df)`: Print enrichment summary

```python
from data import DataEnrichmentPipeline

pipeline = DataEnrichmentPipeline()
df = pipeline.load_cleaned_data()
df_enriched = pipeline.enrich_data(df)
pipeline.save_enriched_data(df_enriched)
```

## Design Patterns Used

1. **Singleton Pattern**: ConfigLoader ensures single instance
2. **Fluent Interface**: DataCleaner supports method chaining
3. **Strategy Pattern**: Different cleaning/enrichment strategies
4. **Factory Pattern**: Logger and enricher instantiation
5. **Pipeline Pattern**: Sequential data processing steps

## Key Benefits

### 1. **Modularity**
- Each module has a single responsibility
- Easy to test individual components
- Clear interfaces between modules

### 2. **Reusability**
- Utility classes can be used across different pipelines
- Generic helpers for common operations
- Configurable enrichers for different datasets

### 3. **Maintainability**
- Centralized configuration management
- Consistent logging throughout
- Clear separation of concerns
- Type hints for better IDE support

### 4. **Scalability**
- Easy to add new enrichers
- Pipeline pattern supports extensions
- Configuration-driven behavior
- Pluggable validation rules

### 5. **Robustness**
- Comprehensive error handling
- Data validation at each step
- Detailed logging and reporting
- Graceful fallbacks

## Usage Examples

### Complete Pipeline Run

```python
# 1. Load raw data
from data import load_raw_data
df_raw = load_raw_data()

# 2. Validate data
from data import validate_data
validate_data(df_raw)

# 3. Clean data
from data import clean_data, save_cleaned_data
df_cleaned = clean_data(df_raw)
save_cleaned_data(df_cleaned)

# 4. Enrich data
from data import DataEnrichmentPipeline
pipeline = DataEnrichmentPipeline()
df_enriched = pipeline.enrich_data(df_cleaned)
pipeline.save_enriched_data(df_enriched)
```

### Custom Cleaning Workflow

```python
from utils import DataCleaner, FileHandler

handler = FileHandler()
df = handler.load_csv('data/raw/data.csv')

cleaner = DataCleaner(df)
df_clean = (cleaner
    .remove_duplicates(subset=['job_id'])
    .handle_missing_values(strategy='fill', fill_value=0)
    .filter_rows(df['salary_avg'] > 50000, 'High salary filter')
    .standardize_text(['company_name'], lowercase=True)
    .get_cleaned_data())

handler.save_csv(df_clean, 'data/custom/data_clean.csv')
```

### Custom Enrichment

```python
from utils.enrichers import SalaryEnricher, SkillsEnricher
from utils import FileHandler

handler = FileHandler()
df = handler.load_csv('data/cleaned/data.csv')

# Apply specific enrichers
salary_enricher = SalaryEnricher(df)
df = salary_enricher.enrich()

skills_enricher = SkillsEnricher(df, top_n=30)  # Custom top N
df, counts = skills_enricher.enrich()

handler.save_csv(df, 'data/enriched/custom_enriched.csv')
```

## Configuration

All behavior is driven by YAML configurations:
- `config/config.yaml`: Main settings
- `config/paths.yaml`: File paths and data processing
- `config/logging.yaml`: Logging configuration

## Testing

Each module can be tested independently:

```bash
# Test individual modules
uv run python src/data/load_data.py
uv run python src/data/clean_data.py
uv run python src/data/validate.py
uv run python src/data/enrich.py
```

## Future Extensibility

### Easy to Add:
- New enrichers (e.g., `TextEnricher`, `ImageEnricher`)
- New validation rules
- New cleaning strategies
- New data sources (databases, APIs)
- New output formats
- Parallel processing
- Caching mechanisms
- Unit tests for each module
