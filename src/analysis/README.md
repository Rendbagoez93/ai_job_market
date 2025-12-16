# Salary Intelligence & Compensation Analysis

## Overview

This module provides comprehensive salary intelligence and compensation analysis for the AI job market dataset. It includes multiple analysis dimensions to understand salary patterns, skill premiums, and market dynamics.

## Architecture

```
src/analysis/
├── __init__.py                    # Module exports
├── salary_intelligence.py         # Main analyzer class
└── run_salary_analysis.py         # Runner script

src/utils/
├── data_merger.py                 # Dataset merging utility
└── enums.py                       # Analysis enumerations
```

## Features

### 1. Skill Premium Analysis
Analyzes salary premiums for individual skills:
- Average salary with vs without each skill
- Premium amount and percentage
- Statistical significance (t-tests)
- Sample sizes for each skill

### 2. Tech Stack ROI Analysis
Compares return on investment for different tech stacks:
- **Cloud Platforms**: AWS, Azure, GCP
- **ML Frameworks**: TensorFlow, PyTorch, Keras, Scikit-learn, Hugging Face
- **Programming Languages**: Python, R, CUDA

### 3. Experience Impact Analysis
Analyzes salary progression by experience level:
- Salary statistics by experience level
- Percentage increase between levels
- Career progression insights

### 4. Geographic Gap Analysis
Compares salaries across geographic regions:
- USA vs International comparison
- Statistical tests for regional differences
- Gap calculations from highest paying region

### 5. Salary Per Skill Analysis
Analyzes salary efficiency metrics:
- Overall salary per skill statistics
- Breakdown by experience level
- Breakdown by industry

### 6. Industry Comparison
Compares compensation across industries:
- Industry-specific salary statistics
- Industry premiums vs overall average
- ANOVA tests for statistical significance

### 7. Company Size Impact
Analyzes how company size affects compensation:
- Salary by company size category
- Startup vs Large company comparison
- Statistical significance tests

### 8. Skill Combination Analysis
Identifies high-value skill combinations:
- Top skill combinations by salary
- Salary per skill efficiency
- Combination frequency analysis

## Usage

### Basic Usage

```python
from analysis.salary_intelligence import SalaryIntelligenceAnalyzer

# Initialize analyzer (will load and merge data automatically)
analyzer = SalaryIntelligenceAnalyzer()

# Generate comprehensive report
report = analyzer.generate_comprehensive_report()

# Export results to CSV
analyzer.export_report(report, output_dir='output/analysis')
```

### Using Pre-loaded Data

```python
import pandas as pd
from utils.data_merger import create_master_dataset
from analysis.salary_intelligence import SalaryIntelligenceAnalyzer

# Create master dataset first
master_df = create_master_dataset(save=True)

# Use with analyzer
analyzer = SalaryIntelligenceAnalyzer(master_df)
report = analyzer.generate_comprehensive_report()
```

### Individual Analyses

```python
# Overall statistics
stats = analyzer.calculate_overall_statistics()
print(f"Average salary: ${stats.mean:,.2f}")

# Skill premium analysis
skill_premiums = analyzer.analyze_skill_premium()
print(skill_premiums.head(10))

# Tech stack ROI
tech_roi = analyzer.analyze_tech_stack_roi()
print(tech_roi['cloud_platforms'])

# Experience impact
exp_impact = analyzer.analyze_experience_impact()
print(exp_impact)

# Geographic gaps
geo_gaps = analyzer.analyze_geographic_gap()
print(geo_gaps)

# Industry comparison
industry_comp = analyzer.analyze_industry_comparison()
print(industry_comp)

# Company size impact
company_impact = analyzer.analyze_company_size_impact()
print(company_impact)

# Skill combinations
combos = analyzer.analyze_skill_combinations(min_count=10)
print(combos.head(20))
```

### Running from Command Line

```bash
# Run complete analysis with export
uv run src/analysis/run_salary_analysis.py

# Or using Python
cd src/analysis
python run_salary_analysis.py
```

## Output Files

Analysis results are exported to `output/analysis/` with the following files:

- `salary_analysis_skill_premium.csv` - Skill premium analysis
- `salary_analysis_tech_stack_roi_cloud_platforms.csv` - Cloud platform comparison
- `salary_analysis_tech_stack_roi_ml_frameworks.csv` - ML framework comparison
- `salary_analysis_tech_stack_roi_programming_languages.csv` - Programming language comparison
- `salary_analysis_experience_impact.csv` - Experience level analysis
- `salary_analysis_geographic_gaps.csv` - Geographic comparison
- `salary_analysis_industry_comparison.csv` - Industry comparison
- `salary_analysis_company_size_impact.csv` - Company size analysis
- `salary_analysis_top_skill_combinations.csv` - Top skill combinations

## Data Requirements

The analyzer requires the following enriched datasets:
- `data/enriched/salary_enriched.csv`
- `data/enriched/skills_enriched.csv`
- `data/enriched/experience_enriched.csv`
- `data/enriched/location_enriched.csv`
- `data/enriched/company_enriched.csv`
- `data/enriched/industry_enriched.csv` (optional)

### Required Columns

**Salary columns:**
- `salary_avg`, `salary_min`, `salary_max`, `salary_per_skill`

**Skills columns:**
- `skill_*` (binary flags for each skill)
- `skills_count`

**Experience columns:**
- `experience_level`, `experience_level_ordinal`

**Location columns:**
- `location_region`, `location_state`

**Company columns:**
- `company_size`, `is_startup`, `is_large_company`

## Statistical Methods

### T-Tests
Used for comparing two groups:
- Skill premium (with vs without skill)
- Geographic comparison (USA vs International)
- Company size (Startup vs Large)

### ANOVA
Used for comparing multiple groups:
- Industry comparison

### Significance Level
Default alpha = 0.05 (95% confidence level)

## Data Classes

### SalaryStatistics
Container for comprehensive salary statistics:
- `mean`, `median`, `std`, `min`, `max`
- `count`, `q25`, `q75`

### SkillPremiumResult
Result of skill premium analysis:
- `skill_name`
- `avg_salary_with_skill`, `avg_salary_without_skill`
- `salary_premium`, `premium_percentage`
- `count_with_skill`, `count_without_skill`
- `p_value`, `is_significant`

## Enumerations

### AnalysisType
- `SKILL_PREMIUM`
- `TECH_STACK_ROI`
- `EXPERIENCE_IMPACT`
- `GEOGRAPHIC_GAP`
- `SALARY_PER_SKILL`
- `INDUSTRY_COMPARISON`
- `COMPANY_SIZE_IMPACT`
- `SKILL_COMBINATION`

### SalaryMetric
- `AVERAGE`, `MINIMUM`, `MAXIMUM`, `MEDIAN`, `PER_SKILL`

### GroupingDimension
- `SKILL`, `EXPERIENCE_LEVEL`, `INDUSTRY`, `LOCATION_REGION`
- `LOCATION_STATE`, `COMPANY_SIZE`, `JOB_TITLE`, `EMPLOYMENT_TYPE`

## Error Handling

The module includes comprehensive error handling:
- Missing columns validation
- Empty dataset checks
- Statistical test validity checks
- Logging for all operations

## Performance Considerations

- Dataset merging is done once and cached
- Statistical tests only run when sufficient data exists
- Results can be filtered by minimum sample size
- Large skill combinations can be filtered by min_count parameter

## Dependencies

Required packages:
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `scipy` - Statistical tests
- Custom utilities from `utils` module

## Logging

All operations are logged using the centralized logging system:
- Info level: Analysis progress and results
- Warning level: Missing columns or insufficient data
- Error level: Failures and exceptions

Log files: `output/app.log`

## Examples

### Example 1: Find Highest Paying Skills

```python
analyzer = SalaryIntelligenceAnalyzer()
premiums = analyzer.analyze_skill_premium()
top_10 = premiums.nlargest(10, 'salary_premium')

for _, row in top_10.iterrows():
    print(f"{row['skill_name']}: ${row['salary_premium']:,.0f} premium "
          f"({row['premium_percentage']:.1f}%)")
```

### Example 2: Compare Cloud Platforms

```python
analyzer = SalaryIntelligenceAnalyzer()
tech_roi = analyzer.analyze_tech_stack_roi()
cloud_comp = tech_roi['cloud_platforms']

print("Cloud Platform Comparison:")
for _, row in cloud_comp.iterrows():
    print(f"{row['skill_name']}: "
          f"With: ${row['avg_salary_with_skill']:,.0f}, "
          f"Premium: {row['premium_percentage']:+.1f}%")
```

### Example 3: Experience Progression

```python
analyzer = SalaryIntelligenceAnalyzer()
exp_impact = analyzer.analyze_experience_impact()

print("Salary by Experience Level:")
for _, row in exp_impact.iterrows():
    pct_inc = row.get('pct_increase', 0)
    print(f"{row['experience_level']}: ${row['mean']:,.0f} "
          f"(+{pct_inc:.1f}% from previous)")
```

## Future Enhancements

Potential additions:
- Time series analysis of salary trends
- Predictive modeling for salary estimation
- Interactive visualization dashboard
- A/B testing framework for compensation experiments
- Regional cost-of-living adjustments
- Skills demand forecasting

## Contributing

When adding new analysis features:
1. Follow the existing pattern with dataclasses for results
2. Include comprehensive docstrings
3. Add statistical validation where appropriate
4. Update this README with new features
5. Add unit tests for new functionality

## License

Part of the AI Job Market Analysis project.
