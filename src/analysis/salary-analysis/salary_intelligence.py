"""Salary Intelligence and Compensation Analysis Module.

This module provides comprehensive salary analysis capabilities including:
- Skill-based salary premiums
- Tech stack ROI analysis
- Experience level impact
- Geographic salary gaps
- Industry comparisons
- Company size impact
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

try:
    from scipy import stats
except ImportError:
    print("Warning: scipy not installed. Statistical tests will be limited.")
    stats = None

from utils.data_merger import DataMerger
from utils.logger import get_logger
from utils.enums import (
    SalaryMetric, GroupingDimension, SkillCategory,
    get_skill_columns, get_cloud_platforms, get_ml_frameworks,
    get_programming_languages
)


logger = get_logger(__name__)


@dataclass
class SalaryStatistics:
    """Container for salary statistics."""
    mean: float
    median: float
    std: float
    min: float
    max: float
    count: int
    q25: float
    q75: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'mean': self.mean,
            'median': self.median,
            'std': self.std,
            'min': self.min,
            'max': self.max,
            'count': self.count,
            'q25': self.q25,
            'q75': self.q75
        }


@dataclass
class SkillPremiumResult:
    """Result of skill premium analysis."""
    skill_name: str
    avg_salary_with_skill: float
    avg_salary_without_skill: float
    salary_premium: float
    premium_percentage: float
    count_with_skill: int
    count_without_skill: int
    p_value: float
    is_significant: bool
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'skill_name': self.skill_name,
            'avg_salary_with_skill': self.avg_salary_with_skill,
            'avg_salary_without_skill': self.avg_salary_without_skill,
            'salary_premium': self.salary_premium,
            'premium_percentage': self.premium_percentage,
            'count_with_skill': self.count_with_skill,
            'count_without_skill': self.count_without_skill,
            'p_value': self.p_value,
            'is_significant': self.is_significant
        }


class SalaryIntelligenceAnalyzer:
    """Analyze salary intelligence and compensation patterns."""
    
    def __init__(self, master_df: Optional[pd.DataFrame] = None):
        """Initialize analyzer.
        
        Args:
            master_df: Pre-merged master dataset. If None, will load and merge.
        """
        self.logger = get_logger(__name__)
        
        if master_df is None:
            self.logger.info("Loading and merging datasets...")
            merger = DataMerger()
            self.df = merger.merge_datasets()
        else:
            self.df = master_df.copy()
        
        self.logger.info(f"Initialized with {len(self.df)} jobs")
        self._validate_required_columns()
    
    def _validate_required_columns(self) -> None:
        """Validate that required columns exist."""
        required = ['salary_avg', 'job_id']
        missing = [col for col in required if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    
    def _calculate_statistics(self, salary_series: pd.Series) -> SalaryStatistics:
        """Calculate comprehensive statistics for salary series.
        
        Args:
            salary_series: Series of salary values
        
        Returns:
            SalaryStatistics object
        """
        return SalaryStatistics(
            mean=float(salary_series.mean()),
            median=float(salary_series.median()),
            std=float(salary_series.std()),
            min=float(salary_series.min()),
            max=float(salary_series.max()),
            count=int(len(salary_series)),
            q25=float(salary_series.quantile(0.25)),
            q75=float(salary_series.quantile(0.75))
        )
    
    def calculate_overall_statistics(self) -> SalaryStatistics:
        """Calculate overall salary statistics.
        
        Returns:
            SalaryStatistics for entire dataset
        """
        self.logger.info("Calculating overall salary statistics")
        stats = self._calculate_statistics(self.df['salary_avg'])
        self.logger.info(f"Overall average salary: ${stats.mean:,.2f}")
        return stats
    
    def analyze_skill_premium(
        self,
        skill_columns: Optional[List[str]] = None,
        alpha: float = 0.05
    ) -> pd.DataFrame:
        """Analyze salary premium for each skill.
        
        Args:
            skill_columns: List of skill column names. If None, uses all.
            alpha: Significance level for statistical tests
        
        Returns:
            DataFrame with skill premium analysis
        """
        if skill_columns is None:
            skill_columns = get_skill_columns()
        
        self.logger.info(f"Analyzing salary premium for {len(skill_columns)} skills")
        
        results = []
        
        for skill_col in skill_columns:
            if skill_col not in self.df.columns:
                self.logger.warning(f"Skill column {skill_col} not found, skipping")
                continue
            
            # Split data by skill presence
            with_skill = self.df[self.df[skill_col] == 1]['salary_avg']
            without_skill = self.df[self.df[skill_col] == 0]['salary_avg']
            
            if len(with_skill) == 0 or len(without_skill) == 0:
                continue
            
            # Calculate statistics
            avg_with = with_skill.mean()
            avg_without = without_skill.mean()
            premium = avg_with - avg_without
            premium_pct = (premium / avg_without) * 100
            
            # Statistical test (t-test)
            if stats is not None:
                t_stat, p_value = stats.ttest_ind(with_skill, without_skill)
            else:
                p_value = 0.05  # Default if scipy not available
            
            # Extract skill name
            skill_name = skill_col.replace('skill_', '').replace('_', ' ').title()
            
            result = SkillPremiumResult(
                skill_name=skill_name,
                avg_salary_with_skill=avg_with,
                avg_salary_without_skill=avg_without,
                salary_premium=premium,
                premium_percentage=premium_pct,
                count_with_skill=len(with_skill),
                count_without_skill=len(without_skill),
                p_value=p_value,
                is_significant=(p_value < alpha)
            )
            
            results.append(result.to_dict())
        
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('salary_premium', ascending=False)
        
        self.logger.info(f"Completed skill premium analysis for {len(results_df)} skills")
        return results_df
    
    def analyze_tech_stack_roi(self) -> Dict[str, pd.DataFrame]:
        """Analyze ROI of different tech stacks (cloud, ML, programming).
        
        Returns:
            Dictionary with DataFrames for each tech stack category
        """
        self.logger.info("Analyzing tech stack ROI")
        
        results = {}
        
        # Cloud platforms
        cloud_skills = get_cloud_platforms()
        if all(col in self.df.columns for col in cloud_skills):
            results['cloud_platforms'] = self.analyze_skill_premium(cloud_skills)
            self.logger.info("Completed cloud platform analysis")
        
        # ML frameworks
        ml_skills = get_ml_frameworks()
        if all(col in self.df.columns for col in ml_skills):
            results['ml_frameworks'] = self.analyze_skill_premium(ml_skills)
            self.logger.info("Completed ML framework analysis")
        
        # Programming languages
        prog_skills = get_programming_languages()
        if all(col in self.df.columns for col in prog_skills):
            results['programming_languages'] = self.analyze_skill_premium(prog_skills)
            self.logger.info("Completed programming language analysis")
        
        return results
    
    def analyze_experience_impact(
        self,
        group_by: str = 'experience_level'
    ) -> pd.DataFrame:
        """Analyze salary impact by experience level.
        
        Args:
            group_by: Column to group by (default: 'experience_level')
        
        Returns:
            DataFrame with experience level analysis
        """
        if group_by not in self.df.columns:
            raise ValueError(f"Column {group_by} not found in dataset")
        
        self.logger.info(f"Analyzing salary by {group_by}")
        
        grouped = self.df.groupby(group_by)['salary_avg'].agg([
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max'),
            ('count', 'count'),
            ('q25', lambda x: x.quantile(0.25)),
            ('q75', lambda x: x.quantile(0.75))
        ]).reset_index()
        
        # Calculate salary progression
        if 'experience_level_ordinal' in self.df.columns:
            exp_order = self.df.groupby(group_by)['experience_level_ordinal'].first().to_dict()
            grouped['ordinal'] = grouped[group_by].map(exp_order)
            grouped = grouped.sort_values('ordinal')
            
            # Calculate % increase from previous level
            grouped['pct_increase'] = grouped['mean'].pct_change() * 100
        
        self.logger.info(f"Completed experience impact analysis")
        return grouped
    
    def analyze_geographic_gap(
        self,
        region_col: str = 'location_region'
    ) -> pd.DataFrame:
        """Analyze salary gaps between geographic regions.
        
        Args:
            region_col: Column containing region information
        
        Returns:
            DataFrame with geographic salary analysis
        """
        if region_col not in self.df.columns:
            raise ValueError(f"Column {region_col} not found in dataset")
        
        self.logger.info(f"Analyzing geographic salary gaps by {region_col}")
        
        results = self.df.groupby(region_col)['salary_avg'].agg([
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('count', 'count')
        ]).reset_index()
        
        # Calculate gap from highest paying region
        max_salary = results['mean'].max()
        results['gap_from_max'] = max_salary - results['mean']
        results['gap_percentage'] = (results['gap_from_max'] / max_salary) * 100
        
        # Statistical test between USA and International (if applicable)
        if stats is not None and 'USA' in results[region_col].values and 'International' in results[region_col].values:
            usa_salaries = self.df[self.df[region_col] == 'USA']['salary_avg']
            intl_salaries = self.df[self.df[region_col] == 'International']['salary_avg']
            
            t_stat, p_value = stats.ttest_ind(usa_salaries, intl_salaries)
            self.logger.info(f"USA vs International t-test p-value: {p_value:.4f}")
        
        self.logger.info("Completed geographic gap analysis")
        return results.sort_values('mean', ascending=False)
    
    def analyze_salary_per_skill(self) -> pd.DataFrame:
        """Analyze salary efficiency (salary per skill).
        
        Returns:
            DataFrame with salary per skill analysis
        """
        if 'salary_per_skill' not in self.df.columns:
            self.logger.warning("salary_per_skill column not found")
            if 'skills_count' in self.df.columns:
                self.df['salary_per_skill'] = self.df['salary_avg'] / self.df['skills_count']
                self.logger.info("Calculated salary_per_skill from skills_count")
        
        self.logger.info("Analyzing salary per skill efficiency")
        
        # Overall statistics
        stats_dict = self._calculate_statistics(self.df['salary_per_skill']).to_dict()
        
        # By experience level
        if 'experience_level' in self.df.columns:
            by_experience = self.df.groupby('experience_level')['salary_per_skill'].agg([
                ('mean', 'mean'),
                ('median', 'median'),
                ('count', 'count')
            ]).reset_index()
        else:
            by_experience = None
        
        # By industry
        if 'industry' in self.df.columns:
            by_industry = self.df.groupby('industry')['salary_per_skill'].agg([
                ('mean', 'mean'),
                ('median', 'median'),
                ('count', 'count')
            ]).reset_index().sort_values('mean', ascending=False)
        else:
            by_industry = None
        
        results = {
            'overall_stats': stats_dict,
            'by_experience': by_experience,
            'by_industry': by_industry
        }
        
        self.logger.info("Completed salary per skill analysis")
        return results
    
    def analyze_industry_comparison(self) -> pd.DataFrame:
        """Compare salaries across industries.
        
        Returns:
            DataFrame with industry comparison
        """
        if 'industry' not in self.df.columns:
            raise ValueError("industry column not found in dataset")
        
        self.logger.info("Analyzing salary by industry")
        
        results = self.df.groupby('industry')['salary_avg'].agg([
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max'),
            ('count', 'count')
        ]).reset_index()
        
        # Calculate industry premium
        overall_avg = self.df['salary_avg'].mean()
        results['premium'] = results['mean'] - overall_avg
        results['premium_percentage'] = (results['premium'] / overall_avg) * 100
        
        # ANOVA test
        if stats is not None:
            industry_groups = [group['salary_avg'].values for name, group in self.df.groupby('industry')]
            f_stat, p_value = stats.f_oneway(*industry_groups)
            self.logger.info(f"Industry ANOVA F-statistic: {f_stat:.2f}, p-value: {p_value:.4f}")
        
        results = results.sort_values('mean', ascending=False)
        self.logger.info("Completed industry comparison")
        return results
    
    def analyze_company_size_impact(self) -> pd.DataFrame:
        """Analyze salary impact by company size.
        
        Returns:
            DataFrame with company size analysis
        """
        if 'company_size' not in self.df.columns:
            raise ValueError("company_size column not found in dataset")
        
        self.logger.info("Analyzing salary by company size")
        
        results = self.df.groupby('company_size')['salary_avg'].agg([
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('count', 'count')
        ]).reset_index()
        
        # Compare startup vs large company if binary flags exist
        if stats is not None and 'is_startup' in self.df.columns and 'is_large_company' in self.df.columns:
            startup_salaries = self.df[self.df['is_startup'] == 1]['salary_avg']
            large_salaries = self.df[self.df['is_large_company'] == 1]['salary_avg']
            
            if len(startup_salaries) > 0 and len(large_salaries) > 0:
                t_stat, p_value = stats.ttest_ind(startup_salaries, large_salaries)
                self.logger.info(f"Startup vs Large company t-test p-value: {p_value:.4f}")
        
        self.logger.info("Completed company size analysis")
        return results.sort_values('mean', ascending=False)
    
    def analyze_skill_combinations(
        self,
        min_count: int = 10
    ) -> pd.DataFrame:
        """Analyze salary for skill combinations.
        
        Args:
            min_count: Minimum number of jobs to include combination
        
        Returns:
            DataFrame with top skill combination analysis
        """
        self.logger.info("Analyzing skill combinations")
        
        skill_cols = get_skill_columns()
        available_skills = [col for col in skill_cols if col in self.df.columns]
        
        # Create skill combination signature
        self.df['skill_signature'] = self.df[available_skills].apply(
            lambda row: ','.join([col.replace('skill_', '') for col in available_skills if row[col] == 1]),
            axis=1
        )
        
        # Analyze combinations
        combo_analysis = self.df.groupby('skill_signature').agg({
            'salary_avg': ['mean', 'median', 'count'],
            'skills_count': 'first'
        }).reset_index()
        
        combo_analysis.columns = ['skill_combination', 'mean_salary', 'median_salary', 'count', 'num_skills']
        
        # Filter by minimum count
        combo_analysis = combo_analysis[combo_analysis['count'] >= min_count]
        
        # Calculate efficiency
        combo_analysis['salary_per_skill'] = combo_analysis['mean_salary'] / combo_analysis['num_skills']
        
        # Sort by mean salary
        combo_analysis = combo_analysis.sort_values('mean_salary', ascending=False)
        
        self.logger.info(f"Found {len(combo_analysis)} skill combinations with min {min_count} jobs")
        return combo_analysis
    
    def generate_comprehensive_report(self) -> Dict[str, Union[pd.DataFrame, Dict]]:
        """Generate comprehensive salary intelligence report.
        
        Returns:
            Dictionary containing all analysis results
        """
        self.logger.info("Generating comprehensive salary intelligence report")
        
        report = {
            'overall_statistics': self.calculate_overall_statistics().to_dict(),
            'skill_premium': self.analyze_skill_premium(),
            'tech_stack_roi': self.analyze_tech_stack_roi(),
            'experience_impact': self.analyze_experience_impact(),
            'geographic_gaps': self.analyze_geographic_gap(),
            'salary_per_skill': self.analyze_salary_per_skill(),
            'industry_comparison': self.analyze_industry_comparison(),
            'company_size_impact': self.analyze_company_size_impact(),
            'top_skill_combinations': self.analyze_skill_combinations(min_count=5).head(20)
        }
        
        self.logger.info("Comprehensive report generated successfully")
        return report
    
    def export_report(
        self,
        report: Dict,
        output_dir: str = 'output/analysis'
    ) -> None:
        """Export report results to CSV files.
        
        Args:
            report: Report dictionary from generate_comprehensive_report
            output_dir: Directory to save reports
        """
        from utils.file_handler import FileHandler
        file_handler = FileHandler()
        
        output_path = Path(output_dir)
        file_handler.ensure_directory(output_path)
        
        for key, value in report.items():
            if isinstance(value, pd.DataFrame):
                filepath = output_path / f"salary_analysis_{key}.csv"
                file_handler.save_csv(value, filepath)
                self.logger.info(f"Exported {key} to {filepath}")
            elif isinstance(value, dict) and 'overall_stats' not in key:
                # For nested dictionaries (like tech_stack_roi)
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, pd.DataFrame):
                        filepath = output_path / f"salary_analysis_{key}_{subkey}.csv"
                        file_handler.save_csv(subvalue, filepath)
                        self.logger.info(f"Exported {key}/{subkey} to {filepath}")


def run_salary_analysis(
    master_df: Optional[pd.DataFrame] = None,
    export: bool = True
) -> Dict:
    """Convenience function to run complete salary analysis.
    
    Args:
        master_df: Pre-merged master dataset. If None, will load and merge.
        export: Whether to export results to CSV files
    
    Returns:
        Dictionary with all analysis results
    """
    analyzer = SalaryIntelligenceAnalyzer(master_df)
    report = analyzer.generate_comprehensive_report()
    
    if export:
        analyzer.export_report(report)
    
    return report


if __name__ == "__main__":
    # Run analysis
    logger.info("Starting salary intelligence analysis")
    report = run_salary_analysis(export=True)
    
    # Print summary
    print("\n" + "="*80)
    print("SALARY INTELLIGENCE ANALYSIS SUMMARY")
    print("="*80)
    
    print("\n1. OVERALL STATISTICS:")
    stats = report['overall_statistics']
    print(f"   Average Salary: ${stats['mean']:,.2f}")
    print(f"   Median Salary: ${stats['median']:,.2f}")
    print(f"   Salary Range: ${stats['min']:,.2f} - ${stats['max']:,.2f}")
    print(f"   Total Jobs Analyzed: {stats['count']:,}")
    
    print("\n2. TOP 10 HIGHEST PAYING SKILLS:")
    top_skills = report['skill_premium'].head(10)
    for idx, row in top_skills.iterrows():
        print(f"   {row['skill_name']}: ${row['salary_premium']:,.2f} "
              f"({row['premium_percentage']:.1f}% premium)")
    
    print("\n3. EXPERIENCE LEVEL IMPACT:")
    exp_impact = report['experience_impact']
    for idx, row in exp_impact.iterrows():
        pct = f"{row['pct_increase']:.1f}%" if 'pct_increase' in row and not pd.isna(row['pct_increase']) else "N/A"
        print(f"   {row['experience_level']}: ${row['mean']:,.2f} (n={row['count']}, +{pct})")
    
    print("\n4. INDUSTRY COMPARISON:")
    industry = report['industry_comparison'].head(5)
    for idx, row in industry.iterrows():
        print(f"   {row['industry']}: ${row['mean']:,.2f} "
              f"({row['premium_percentage']:+.1f}% vs avg)")
    
    print("\n" + "="*80)
    print("Analysis complete! Results exported to output/analysis/")
    print("="*80 + "\n")
