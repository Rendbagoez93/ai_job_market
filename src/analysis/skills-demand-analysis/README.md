# Skills Demand & Talent Gap Analysis

## Overview

This module provides comprehensive analysis of skills demand patterns, talent gaps, and high-value skills in the AI job market.

## Features

### 1. Skill Demand Ranking
- Uses `skill_frequency.csv` for demand metrics
- Calculates demand percentages and categorizes demand levels
- Ranks skills by market demand

### 2. Skill Correlation Analysis
- Creates correlation matrix of skill binary features
- Identifies skill co-occurrence patterns
- Finds complementary skill combinations

### 3. Job Title Analysis
- Groups by job_title to calculate skill prevalence rates
- Identifies top skills for each job role
- Provides role-specific skill requirements

### 4. High-Value Skills Identification
- Cross-references skills with salary data
- Calculates salary premiums for each skill
- Performs statistical significance testing
- Combines demand and premium into value scores

### 5. Talent Gap Analysis
- **Critical Skills**: High demand + high premium (priority learning)
- **Emerging Opportunities**: Medium demand + very high premium (future-proof)
- **Oversupplied Skills**: High demand + low premium (saturated market)
- **Undervalued Gems**: Low demand + high premium (niche opportunities)

### 6. Skill Recommendations
- Personalized learning recommendations
- ROI calculation for skill acquisition
- Priority-based learning paths

## Usage

### Basic Usage

```python
from src.analysis.skills_demand_analyzer import run_skills_demand_analysis

# Run complete analysis with export
report = run_skills_demand_analysis(export=True)

# Access specific results
demand_ranking = report['skill_demand_ranking']
high_value_skills = report['high_value_skills']
talent_gap = report['talent_gap']
recommendations = report['recommendations']
```

### Advanced Usage

```python
from src.analysis.skills_demand_analyzer import SkillsDemandAnalyzer

# Create analyzer instance
analyzer = SkillsDemandAnalyzer()

# Load data
analyzer.load_data()

# Run specific analyses
demand = analyzer.get_skill_demand_ranking()
correlation = analyzer.create_skill_correlation_matrix()
prevalence = analyzer.calculate_skill_prevalence_by_job_title()
high_value = analyzer.identify_high_value_skills()

# Get recommendations based on current skills
current_skills = ['Python', 'SQL', 'Excel']
recommendations = analyzer.generate_skill_recommendations(current_skills)

# Export results
analyzer.export_results()
```

### Command Line Usage

```bash
# Run from project root
python src/analysis/skills-demand-analysis/run_skills_demand_analysis.py

# Or navigate to the directory
cd src/analysis/skills-demand-analysis
python run_skills_demand_analysis.py
```

## Output Files

All results are exported to `output/analysis/`:

1. **skills_demand_ranking.csv** - Skill demand metrics and rankings
2. **skills_correlation_matrix.csv** - Correlation matrix of all skills
3. **skills_cooccurrence.csv** - Skill pair correlations and strengths
4. **skills_prevalence_by_job_title.csv** - Skill prevalence rates by job role
5. **skills_top_by_job_title.csv** - Top 5 skills for each job title
6. **skills_high_value.csv** - High-value skills with premiums and demand
7. **skills_talent_gap_critical_skills.csv** - Critical skills to learn
8. **skills_talent_gap_emerging_opportunities.csv** - Emerging high-value skills
9. **skills_talent_gap_oversupplied_skills.csv** - Saturated skills
10. **skills_talent_gap_undervalued_gems.csv** - Niche opportunity skills
11. **skills_recommendations.csv** - Prioritized learning recommendations

## Key Metrics

### Demand Metrics
- **Count**: Number of job postings requiring the skill
- **Demand Percentage**: Percentage of total jobs requiring the skill
- **Demand Level**: Categorized as Low/Medium/High/Very High

### Value Metrics
- **Salary Premium**: Absolute salary difference with vs without skill
- **Premium Percentage**: Percentage salary increase from having the skill
- **Value Score**: Combined metric of premium and demand (0-100)
- **Value Tier**: Categorized as Standard/High-Value/Premium

### Statistical Metrics
- **P-value**: Statistical significance of salary difference
- **T-statistic**: Effect size of skill on salary
- **Is Significant**: Whether difference is statistically significant (p < 0.05)

### Correlation Metrics
- **Correlation**: Pearson correlation between skill pairs (-1 to 1)
- **Strength**: Categorized as Moderate (0.3-0.6) or Strong (>0.6)

## Interpretation Guide

### High-Value Skills
- Focus on skills with **value_tier = 'Premium'**
- Prioritize skills with **is_significant = True**
- Consider both demand and premium percentages

### Talent Gaps
- **Critical Skills**: Must-learn for competitive advantage
- **Emerging Opportunities**: Invest early for future returns
- **Oversupplied Skills**: May not differentiate you
- **Undervalued Gems**: Specialized skills for niche roles

### Learning Recommendations
- **Critical Priority**: Learn immediately
- **High Priority**: Plan to learn within 3-6 months
- **Medium Priority**: Consider for long-term career development

## Dependencies

```python
pandas
numpy
scipy
pathlib
```

## Example Analysis Workflow

```python
# 1. Load and analyze
from src.analysis.skills_demand_analyzer import SkillsDemandAnalyzer

analyzer = SkillsDemandAnalyzer()
analyzer.load_data()

# 2. Identify top opportunities
high_value = analyzer.identify_high_value_skills()
premium_skills = high_value[high_value['value_tier'] == 'Premium']

# 3. Check talent gaps
talent_gap = analyzer.analyze_talent_gap()
critical = talent_gap['critical_skills']

# 4. Get personalized recommendations
my_skills = ['Python', 'Pandas', 'SQL']
to_learn = analyzer.generate_skill_recommendations(my_skills)

# 5. Export for further analysis
analyzer.export_results()
```

## Notes

- Analysis uses binary skill features from `skills_enriched.csv`
- Salary data comes from `salary_enriched.csv`
- Demand ranking uses `skill_frequency.csv` from data dictionary
- All statistical tests use α = 0.05 significance level
- Correlations calculated using Pearson correlation coefficient
- Value scores are normalized to 0-100 scale

## Future Enhancements

- [ ] Add time-based trend analysis for skill demand
- [ ] Include industry-specific skill recommendations
- [ ] Add skill acquisition difficulty ratings
- [ ] Implement skill pathway visualization
- [ ] Add machine learning for demand forecasting
