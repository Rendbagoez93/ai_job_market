# Visualization Module

This directory contains comprehensive visualization tools for the AI Job Market salary intelligence analysis.

## Files

### Core Visualization Module
- **`salary_visualizer.py`**: Main visualization module containing the `SalaryVisualizer` class
  - Creates 8 different types of visualizations
  - Modular, clean, and robust design
  - Automatic figure saving with customizable styling

### Runner Scripts
- **`run_visualizations.py`**: Convenience script to generate all visualizations at once
- **`dashboard_utils.py`**: Reserved for dashboard utilities (currently empty)
- **`plot_matplotlib.py`**: Reserved for matplotlib-specific plots (currently empty)
- **`plot_seaborn.py`**: Reserved for seaborn-specific plots (currently empty)

## Usage

### Quick Start

```python
# Run from project root
python src/visuals/run_visualizations.py
```

This will:
1. Load or run the salary intelligence analysis
2. Generate all 8 visualizations
3. Save them to `output/visuals/` directory

### Programmatic Usage

```python
from visuals.salary_visualizer import visualize_salary_analysis, SalaryVisualizer

# Option 1: Run analysis and visualize in one call
figures = visualize_salary_analysis(save=True, show=False)

# Option 2: Use existing report data
from analysis.salary_intelligence import run_salary_analysis

report = run_salary_analysis(export=True)
visualizer = SalaryVisualizer(report)
figures = visualizer.create_comprehensive_dashboard(save=True)

# Option 3: Create individual visualizations
visualizer = SalaryVisualizer(report)
fig1 = visualizer.plot_overall_statistics()
fig2 = visualizer.plot_skill_premium(top_n=20)
fig3 = visualizer.plot_tech_stack_comparison()
# ... and more
```

## Available Visualizations

### 1. Overall Statistics
**File**: `salary_overall_statistics.png`
- Salary distribution quartiles (Min, Q1, Median, Q3, Max)
- Central tendency metrics (Mean, Median, Std Dev)

### 2. Skill Premium
**File**: `salary_skill_premium.png`
- Top N highest paying skills
- Both absolute premium ($) and percentage premium (%)
- Statistical significance indicators

### 3. Tech Stack Comparison
**File**: `salary_tech_stack_comparison.png`
- Cloud platforms (AWS, Azure, GCP, etc.)
- ML frameworks (TensorFlow, PyTorch, etc.)
- Programming languages (Python, R, Java, etc.)

### 4. Experience Impact
**File**: `salary_experience_impact.png`
- Mean salary by experience level
- Salary growth rate (% increase between levels)
- Standard deviation error bars

### 5. Geographic Gaps
**File**: `salary_geographic_gaps.png`
- Average salary by region
- Gap from highest paying region

### 6. Industry Comparison
**File**: `salary_industry_comparison.png`
- Top N industries by salary
- Premium/discount vs overall average
- Color-coded positive/negative premiums

### 7. Company Size Impact
**File**: `salary_company_size_impact.png`
- Salary distribution by company size
- Standard deviation indicators

### 8. Skill Combinations
**File**: `salary_skill_combinations.png`
- Top N skill combinations by salary
- Salary efficiency ($/skill)
- Number of skills in each combination

## Customization

### Styling

```python
visualizer = SalaryVisualizer(
    report_data=report,
    style='seaborn-v0_8-darkgrid',  # Matplotlib style
    figsize=(12, 8),                # Default figure size
    dpi=100                         # Resolution
)
```

### Color Palette

The visualizer uses a custom color palette:
- **Primary**: `#2E86AB` (Blue)
- **Secondary**: `#A23B72` (Purple)
- **Accent**: `#F18F01` (Orange)
- **Success**: `#06A77D` (Green)
- **Danger**: `#D62246` (Red)
- **Neutral**: `#6C757D` (Gray)

### Individual Plots

Each plot method accepts customization parameters:

```python
# Customize skill premium plot
fig = visualizer.plot_skill_premium(
    top_n=15,        # Number of skills to show
    save=True        # Save to file
)

# Customize industry comparison
fig = visualizer.plot_industry_comparison(
    top_n=20,
    save=True
)
```

## Output

All visualizations are saved to `output/visuals/` with:
- **Format**: PNG
- **Resolution**: 100 DPI (configurable)
- **Layout**: Tight layout with proper spacing
- **Naming**: Descriptive filenames (e.g., `salary_skill_premium.png`)

## Dependencies

Required packages (already in `pyproject.toml`):
- `matplotlib >= 3.10.7`
- `seaborn >= 0.13.2`
- `pandas >= 2.3.3`
- `numpy >= 2.3.5`

## Features

### Robust Design
- Comprehensive error handling
- Logging throughout execution
- Graceful handling of missing data
- Input validation

### Modular Architecture
- Separate methods for each visualization type
- Reusable helper methods
- Consistent styling across all plots
- Easy to extend with new visualizations

### Production Ready
- Clean, maintainable code
- Type hints for better IDE support
- Docstrings for all public methods
- No unused variables or imports
- Follows PEP 8 guidelines

## Integration

The visualization module integrates seamlessly with:
- `src/analysis/salary_intelligence.py` - Analysis source
- `src/analysis/run_salary_analysis.py` - Analysis runner
- `src/utils/logger.py` - Logging infrastructure
- `src/utils/data_merger.py` - Data processing

## Examples

### Generate All Visualizations

```bash
cd src/visuals
python run_visualizations.py
```

### Generate Specific Visualization

```python
from visuals.salary_visualizer import SalaryVisualizer
from analysis.salary_intelligence import run_salary_analysis

# Get analysis data
report = run_salary_analysis()

# Create visualizer
viz = SalaryVisualizer(report)

# Generate only skill premium visualization
viz.plot_skill_premium(top_n=25, save=True)
```

### Load from Existing CSV Files

```python
from visuals.salary_visualizer import visualize_salary_analysis

# Load analysis results from CSV files and visualize
figures = visualize_salary_analysis(
    report_path='output/analysis',
    save=True,
    show=False
)
```

## Troubleshooting

### Style Not Available
If you see a warning about matplotlib style not being available, the visualizer automatically falls back to the default style.

### Missing Data
The visualizer gracefully handles missing data sections. If a particular analysis component is missing, it simply skips that visualization.

### Memory Issues
For very large datasets, consider:
- Reducing `top_n` parameters
- Lowering `dpi` setting
- Generating visualizations one at a time instead of all at once

## Future Enhancements

Potential additions to consider:
- Interactive dashboards using Plotly
- Animated visualizations for trends over time
- Heatmaps for skill correlation analysis
- Network graphs for skill relationships
- Export to multiple formats (SVG, PDF)
