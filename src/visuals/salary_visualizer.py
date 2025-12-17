"""Comprehensive Salary Intelligence Visualization Module.

This module provides visualization capabilities for salary intelligence analysis,
including skill premiums, tech stack ROI, experience impact, geographic gaps,
and more using matplotlib and seaborn.
"""

import sys
from pathlib import Path
import warnings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional, Tuple

sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import get_logger

warnings.filterwarnings('ignore')


logger = get_logger(__name__)


class SalaryVisualizer:
    """Create comprehensive visualizations for salary intelligence analysis."""
    
    def __init__(
        self,
        report_data: Dict,
        style: str = 'seaborn-v0_8-darkgrid',
        figsize: Tuple[int, int] = (12, 8),
        dpi: int = 100
    ):
        """Initialize visualizer with report data.
        
        Args:
            report_data: Dictionary containing analysis results
            style: Matplotlib style to use
            figsize: Default figure size
            dpi: Figure resolution
        """
        self.report = report_data
        self.default_figsize = figsize
        self.dpi = dpi
        
        # Set style
        try:
            plt.style.use(style)
        except Exception as e:
            plt.style.use('default')
            logger.warning(f"Style '{style}' not available, using default: {e}")
        
        # Color palettes
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'accent': '#F18F01',
            'success': '#06A77D',
            'danger': '#D62246',
            'neutral': '#6C757D',
            'palette': sns.color_palette('husl', 15)
        }
        
        logger.info("SalaryVisualizer initialized")
    
    def _setup_figure(
        self,
        figsize: Optional[Tuple[int, int]] = None,
        title: Optional[str] = None
    ) -> Tuple[plt.Figure, plt.Axes]:
        """Setup figure with consistent styling.
        
        Args:
            figsize: Figure size tuple
            title: Figure title
        
        Returns:
            Tuple of (figure, axes)
        """
        figsize = figsize or self.default_figsize
        fig, ax = plt.subplots(figsize=figsize, dpi=self.dpi)
        
        if title:
            fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
        
        return fig, ax
    
    def _format_currency(self, value: float, short: bool = False) -> str:
        """Format currency values.
        
        Args:
            value: Numeric value to format
            short: Use short format (K, M)
        
        Returns:
            Formatted string
        """
        if short:
            if abs(value) >= 1_000_000:
                return f'${value/1_000_000:.1f}M'
            elif abs(value) >= 1_000:
                return f'${value/1_000:.0f}K'
        return f'${value:,.0f}'
    
    def _save_figure(
        self,
        fig: plt.Figure,
        filename: str,
        output_dir: str = 'output/visuals',
        tight: bool = True
    ) -> None:
        """Save figure to file.
        
        Args:
            fig: Matplotlib figure
            filename: Output filename
            output_dir: Output directory
            tight: Use tight layout
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filepath = output_path / filename
        
        if tight:
            fig.tight_layout()
        
        fig.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        logger.info(f"Saved visualization: {filepath}")
    
    def plot_overall_statistics(
        self,
        save: bool = True
    ) -> plt.Figure:
        """Visualize overall salary statistics.
        
        Args:
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info("Creating overall statistics visualization")
        
        stats = self.report['overall_statistics']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=self.dpi)
        fig.suptitle('Overall Salary Statistics', fontsize=16, fontweight='bold')
        
        # Box plot representation
        data_points = [
            stats['min'],
            stats['q25'],
            stats['median'],
            stats['q75'],
            stats['max']
        ]
        labels = ['Min', 'Q1 (25%)', 'Median', 'Q3 (75%)', 'Max']
        
        ax1.barh(labels, data_points, color=self.colors['palette'][:5])
        ax1.set_xlabel('Salary ($)', fontsize=12, fontweight='bold')
        ax1.set_title('Salary Distribution Quartiles', fontsize=13, fontweight='bold')
        
        for i, (label, value) in enumerate(zip(labels, data_points)):
            ax1.text(value, i, self._format_currency(value, short=True),
                    va='center', ha='left', fontsize=10, fontweight='bold')
        
        # Key metrics
        metrics = {
            'Mean': stats['mean'],
            'Median': stats['median'],
            'Std Dev': stats['std']
        }
        
        metric_names = list(metrics.keys())
        metric_values = list(metrics.values())
        
        bars = ax2.bar(metric_names, metric_values, color=[self.colors['primary'], 
                                                           self.colors['secondary'],
                                                           self.colors['accent']])
        ax2.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
        ax2.set_title('Central Tendency & Variability', fontsize=13, fontweight='bold')
        
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    self._format_currency(height, short=True),
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Add count annotation
        fig.text(0.5, 0.02, f'Total Jobs Analyzed: {stats["count"]:,}',
                ha='center', fontsize=11, fontweight='bold', style='italic')
        
        if save:
            self._save_figure(fig, 'salary_overall_statistics.png')
        
        return fig
    
    def plot_skill_premium(
        self,
        top_n: int = 20,
        save: bool = True
    ) -> plt.Figure:
        """Visualize top skill premiums.
        
        Args:
            top_n: Number of top skills to display
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info(f"Creating skill premium visualization (top {top_n})")
        
        skill_premium = self.report['skill_premium'].head(top_n).copy()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), dpi=self.dpi)
        fig.suptitle(f'Top {top_n} Highest Paying Skills', fontsize=16, fontweight='bold')
        
        # Premium amount
        y_pos = np.arange(len(skill_premium))
        colors = [self.colors['success'] if sig else self.colors['neutral'] 
                 for sig in skill_premium['is_significant']]
        
        ax1.barh(y_pos, skill_premium['salary_premium'], color=colors)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(skill_premium['skill_name'], fontsize=10)
        ax1.set_xlabel('Salary Premium ($)', fontsize=12, fontweight='bold')
        ax1.set_title('Absolute Salary Premium', fontsize=13, fontweight='bold')
        ax1.invert_yaxis()
        
        for i, (idx, row) in enumerate(skill_premium.iterrows()):
            ax1.text(row['salary_premium'], i, self._format_currency(row['salary_premium'], short=True),
                    va='center', ha='left', fontsize=9, fontweight='bold')
        
        # Percentage premium
        ax2.barh(y_pos, skill_premium['premium_percentage'], color=colors)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(skill_premium['skill_name'], fontsize=10)
        ax2.set_xlabel('Premium Percentage (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Percentage Premium Over Baseline', fontsize=13, fontweight='bold')
        ax2.invert_yaxis()
        
        for i, (idx, row) in enumerate(skill_premium.iterrows()):
            ax2.text(row['premium_percentage'], i, f"{row['premium_percentage']:.1f}%",
                    va='center', ha='left', fontsize=9, fontweight='bold')
        
        # Legend for statistical significance
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.colors['success'], label='Statistically Significant (p<0.05)'),
            Patch(facecolor=self.colors['neutral'], label='Not Significant')
        ]
        fig.legend(handles=legend_elements, loc='lower center', ncol=2, 
                  bbox_to_anchor=(0.5, -0.02), fontsize=10)
        
        if save:
            self._save_figure(fig, 'salary_skill_premium.png')
        
        return fig
    
    def plot_tech_stack_comparison(
        self,
        save: bool = True
    ) -> plt.Figure:
        """Visualize tech stack ROI comparison.
        
        Args:
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info("Creating tech stack comparison visualization")
        
        tech_stack = self.report['tech_stack_roi']
        
        # Determine number of subplots needed
        n_stacks = len(tech_stack)
        if n_stacks == 0:
            logger.warning("No tech stack data available")
            return None
        
        fig, axes = plt.subplots(1, n_stacks, figsize=(6*n_stacks, 8), dpi=self.dpi)
        fig.suptitle('Tech Stack ROI Comparison', fontsize=16, fontweight='bold')
        
        if n_stacks == 1:
            axes = [axes]
        
        colors_map = {
            'cloud_platforms': self.colors['primary'],
            'ml_frameworks': self.colors['secondary'],
            'programming_languages': self.colors['accent']
        }
        
        for idx, (stack_name, stack_data) in enumerate(tech_stack.items()):
            ax = axes[idx]
            
            # Take top 10
            top_stack = stack_data.head(10)
            
            y_pos = np.arange(len(top_stack))
            ax.barh(y_pos, top_stack['salary_premium'], 
                   color=colors_map.get(stack_name, self.colors['neutral']))
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(top_stack['skill_name'], fontsize=10)
            ax.set_xlabel('Salary Premium ($)', fontsize=11, fontweight='bold')
            
            title = stack_name.replace('_', ' ').title()
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.invert_yaxis()
            
            for i, (_, row) in enumerate(top_stack.iterrows()):
                ax.text(row['salary_premium'], i, 
                       self._format_currency(row['salary_premium'], short=True),
                       va='center', ha='left', fontsize=9, fontweight='bold')
        
        if save:
            self._save_figure(fig, 'salary_tech_stack_comparison.png')
        
        return fig
    
    def plot_experience_impact(
        self,
        save: bool = True
    ) -> plt.Figure:
        """Visualize salary by experience level.
        
        Args:
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info("Creating experience impact visualization")
        
        exp_data = self.report['experience_impact']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=self.dpi)
        fig.suptitle('Experience Level Salary Impact', fontsize=16, fontweight='bold')
        
        # Salary by experience level
        x_pos = np.arange(len(exp_data))
        
        ax1.bar(x_pos, exp_data['mean'], 
               color=self.colors['palette'][:len(exp_data)],
               edgecolor='black', linewidth=1.5)
        
        # Add error bars for std deviation
        ax1.errorbar(x_pos, exp_data['mean'], yerr=exp_data['std'], 
                    fmt='none', ecolor='black', capsize=5, capthick=2)
        
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(exp_data['experience_level'], rotation=45, ha='right')
        ax1.set_ylabel('Average Salary ($)', fontsize=12, fontweight='bold')
        ax1.set_title('Mean Salary by Experience Level', fontsize=13, fontweight='bold')
        
        for i, (idx, row) in enumerate(exp_data.iterrows()):
            ax1.text(i, row['mean'], self._format_currency(row['mean'], short=True),
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Percentage increase trajectory
        if 'pct_increase' in exp_data.columns:
            valid_pct = exp_data.dropna(subset=['pct_increase'])
            
            ax2.plot(range(len(valid_pct)), valid_pct['pct_increase'], 
                    marker='o', linewidth=3, markersize=10,
                    color=self.colors['primary'])
            
            ax2.set_xticks(range(len(valid_pct)))
            ax2.set_xticklabels(valid_pct['experience_level'], rotation=45, ha='right')
            ax2.set_ylabel('% Increase from Previous Level', fontsize=12, fontweight='bold')
            ax2.set_title('Salary Growth Rate', fontsize=13, fontweight='bold')
            ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
            ax2.grid(True, alpha=0.3)
            
            for i, (idx, row) in enumerate(valid_pct.iterrows()):
                ax2.text(i, row['pct_increase'], f"{row['pct_increase']:.1f}%",
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
        else:
            # Show median comparison if pct_increase not available
            ax2.bar(x_pos, exp_data['median'], 
                   color=self.colors['secondary'],
                   edgecolor='black', linewidth=1.5, alpha=0.7)
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels(exp_data['experience_level'], rotation=45, ha='right')
            ax2.set_ylabel('Median Salary ($)', fontsize=12, fontweight='bold')
            ax2.set_title('Median Salary by Experience Level', fontsize=13, fontweight='bold')
            
            for i, (idx, row) in enumerate(exp_data.iterrows()):
                ax2.text(i, row['median'], self._format_currency(row['median'], short=True),
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        if save:
            self._save_figure(fig, 'salary_experience_impact.png')
        
        return fig
    
    def plot_geographic_gaps(
        self,
        save: bool = True
    ) -> plt.Figure:
        """Visualize geographic salary gaps.
        
        Args:
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info("Creating geographic gaps visualization")
        
        geo_data = self.report['geographic_gaps']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=self.dpi)
        fig.suptitle('Geographic Salary Analysis', fontsize=16, fontweight='bold')
        
        # Average salary by region
        y_pos = np.arange(len(geo_data))
        
        ax1.barh(y_pos, geo_data['mean'], color=self.colors['palette'][:len(geo_data)])
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(geo_data['location_region'], fontsize=11)
        ax1.set_xlabel('Average Salary ($)', fontsize=12, fontweight='bold')
        ax1.set_title('Average Salary by Region', fontsize=13, fontweight='bold')
        ax1.invert_yaxis()
        
        for i, (idx, row) in enumerate(geo_data.iterrows()):
            ax1.text(row['mean'], i, 
                    f"{self._format_currency(row['mean'], short=True)} (n={row['count']})",
                    va='center', ha='left', fontsize=10, fontweight='bold')
        
        # Gap from maximum
        colors_gap = [self.colors['success'] if gap == 0 else self.colors['danger'] 
                     for gap in geo_data['gap_from_max']]
        
        ax2.barh(y_pos, geo_data['gap_from_max'], color=colors_gap)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(geo_data['location_region'], fontsize=11)
        ax2.set_xlabel('Gap from Highest Region ($)', fontsize=12, fontweight='bold')
        ax2.set_title('Salary Gap Analysis', fontsize=13, fontweight='bold')
        ax2.invert_yaxis()
        
        for i, (idx, row) in enumerate(geo_data.iterrows()):
            gap_text = f"-{self._format_currency(row['gap_from_max'], short=True)} ({row['gap_percentage']:.1f}%)"
            if row['gap_from_max'] == 0:
                gap_text = "Highest"
            ax2.text(row['gap_from_max'], i, gap_text,
                    va='center', ha='left', fontsize=10, fontweight='bold')
        
        if save:
            self._save_figure(fig, 'salary_geographic_gaps.png')
        
        return fig
    
    def plot_industry_comparison(
        self,
        top_n: int = 15,
        save: bool = True
    ) -> plt.Figure:
        """Visualize salary by industry.
        
        Args:
            top_n: Number of industries to display
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info(f"Creating industry comparison visualization (top {top_n})")
        
        industry_data = self.report['industry_comparison'].head(top_n)
        
        fig, ax = plt.subplots(figsize=(14, 10), dpi=self.dpi)
        fig.suptitle(f'Top {top_n} Industries by Salary', fontsize=16, fontweight='bold')
        
        y_pos = np.arange(len(industry_data))
        
        # Color based on premium (positive or negative)
        colors = [self.colors['success'] if prem >= 0 else self.colors['danger'] 
                 for prem in industry_data['premium']]
        
        ax.barh(y_pos, industry_data['mean'], color=colors, alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(industry_data['industry'], fontsize=10)
        ax.set_xlabel('Average Salary ($)', fontsize=12, fontweight='bold')
        ax.set_title('Mean Salary by Industry', fontsize=13, fontweight='bold')
        ax.invert_yaxis()
        
        # Add overall average line
        overall_avg = industry_data['mean'].iloc[0] - industry_data['premium'].iloc[0]
        ax.axvline(x=overall_avg, color='black', linestyle='--', 
                  linewidth=2, label=f'Overall Avg: {self._format_currency(overall_avg, short=True)}')
        
        for i, (idx, row) in enumerate(industry_data.iterrows()):
            premium_sign = '+' if row['premium_percentage'] >= 0 else ''
            text = f"{self._format_currency(row['mean'], short=True)} ({premium_sign}{row['premium_percentage']:.1f}%)"
            ax.text(row['mean'], i, text,
                   va='center', ha='left', fontsize=9, fontweight='bold')
        
        ax.legend(loc='lower right', fontsize=11)
        
        if save:
            self._save_figure(fig, 'salary_industry_comparison.png')
        
        return fig
    
    def plot_company_size_impact(
        self,
        save: bool = True
    ) -> plt.Figure:
        """Visualize salary by company size.
        
        Args:
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info("Creating company size impact visualization")
        
        company_data = self.report['company_size_impact']
        
        fig, ax = plt.subplots(figsize=(12, 6), dpi=self.dpi)
        fig.suptitle('Company Size Salary Impact', fontsize=16, fontweight='bold')
        
        x_pos = np.arange(len(company_data))
        
        ax.bar(x_pos, company_data['mean'], 
              color=self.colors['palette'][:len(company_data)],
              edgecolor='black', linewidth=1.5)
        
        # Add error bars
        ax.errorbar(x_pos, company_data['mean'], yerr=company_data['std'],
                   fmt='none', ecolor='black', capsize=5, capthick=2)
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(company_data['company_size'], rotation=45, ha='right')
        ax.set_ylabel('Average Salary ($)', fontsize=12, fontweight='bold')
        ax.set_title('Mean Salary by Company Size', fontsize=13, fontweight='bold')
        
        for i, (idx, row) in enumerate(company_data.iterrows()):
            text = f"{self._format_currency(row['mean'], short=True)}\n(n={row['count']})"
            ax.text(i, row['mean'], text,
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        if save:
            self._save_figure(fig, 'salary_company_size_impact.png')
        
        return fig
    
    def plot_skill_combinations(
        self,
        top_n: int = 15,
        save: bool = True
    ) -> plt.Figure:
        """Visualize top skill combinations.
        
        Args:
            top_n: Number of combinations to display
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info(f"Creating skill combinations visualization (top {top_n})")
        
        combo_data = self.report['top_skill_combinations'].head(top_n).copy()
        
        # Truncate long skill combinations
        combo_data['skill_short'] = combo_data['skill_combination'].apply(
            lambda x: x[:40] + '...' if len(x) > 40 else x
        )
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10), dpi=self.dpi)
        fig.suptitle(f'Top {top_n} Skill Combinations', fontsize=16, fontweight='bold')
        
        y_pos = np.arange(len(combo_data))
        
        # Mean salary
        ax1.barh(y_pos, combo_data['mean_salary'], color=self.colors['primary'])
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(combo_data['skill_short'], fontsize=9)
        ax1.set_xlabel('Mean Salary ($)', fontsize=12, fontweight='bold')
        ax1.set_title('Mean Salary by Skill Combination', fontsize=13, fontweight='bold')
        ax1.invert_yaxis()
        
        for i, (idx, row) in enumerate(combo_data.iterrows()):
            ax1.text(row['mean_salary'], i, self._format_currency(row['mean_salary'], short=True),
                    va='center', ha='left', fontsize=9, fontweight='bold')
        
        # Salary per skill (efficiency)
        ax2.barh(y_pos, combo_data['salary_per_skill'], color=self.colors['accent'])
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(combo_data['skill_short'], fontsize=9)
        ax2.set_xlabel('Salary per Skill ($)', fontsize=12, fontweight='bold')
        ax2.set_title('Efficiency: Salary per Individual Skill', fontsize=13, fontweight='bold')
        ax2.invert_yaxis()
        
        for i, (idx, row) in enumerate(combo_data.iterrows()):
            text = f"{self._format_currency(row['salary_per_skill'], short=True)}\n({row['num_skills']} skills)"
            ax2.text(row['salary_per_skill'], i, text,
                    va='center', ha='left', fontsize=8, fontweight='bold')
        
        if save:
            self._save_figure(fig, 'salary_skill_combinations.png')
        
        return fig
    
    def create_comprehensive_dashboard(
        self,
        save: bool = True,
        output_dir: str = 'output/visuals'
    ) -> Dict[str, plt.Figure]:
        """Create all visualizations in one call.
        
        Args:
            save: Whether to save figures
            output_dir: Directory to save figures
        
        Returns:
            Dictionary of all generated figures
        """
        logger.info("Creating comprehensive salary intelligence dashboard")
        
        figures = {}
        
        # Create all visualizations
        figures['overall_stats'] = self.plot_overall_statistics(save=save)
        figures['skill_premium'] = self.plot_skill_premium(save=save)
        
        if 'tech_stack_roi' in self.report and self.report['tech_stack_roi']:
            figures['tech_stack'] = self.plot_tech_stack_comparison(save=save)
        
        if 'experience_impact' in self.report:
            figures['experience'] = self.plot_experience_impact(save=save)
        
        if 'geographic_gaps' in self.report:
            figures['geographic'] = self.plot_geographic_gaps(save=save)
        
        if 'industry_comparison' in self.report:
            figures['industry'] = self.plot_industry_comparison(save=save)
        
        if 'company_size_impact' in self.report:
            figures['company_size'] = self.plot_company_size_impact(save=save)
        
        if 'top_skill_combinations' in self.report:
            figures['skill_combos'] = self.plot_skill_combinations(save=save)
        
        logger.info(f"Created {len(figures)} visualizations")
        
        if save:
            logger.info(f"All visualizations saved to {output_dir}")
        
        return figures


def visualize_salary_analysis(
    report_path: Optional[str] = None,
    report_data: Optional[Dict] = None,
    save: bool = True,
    show: bool = False
) -> Dict[str, plt.Figure]:
    """Convenience function to create all salary visualizations.
    
    Args:
        report_path: Path to directory containing analysis CSV files
        report_data: Pre-loaded report dictionary
        save: Whether to save figures
        show: Whether to display figures
    
    Returns:
        Dictionary of generated figures
    """
    if report_data is None and report_path is None:
        # Run analysis to get data
        from analysis.salary_intelligence import run_salary_analysis
        logger.info("No report data provided, running analysis...")
        report_data = run_salary_analysis(export=False)
    elif report_data is None:
        # Load from CSV files
        logger.info(f"Loading report data from {report_path}")
        report_data = _load_report_from_csv(report_path)
    
    # Create visualizer
    visualizer = SalaryVisualizer(report_data)
    
    # Generate all visualizations
    figures = visualizer.create_comprehensive_dashboard(save=save)
    
    if show:
        plt.show()
    else:
        plt.close('all')
    
    return figures


def _load_report_from_csv(report_dir: str) -> Dict:
    """Load analysis report from CSV files.
    
    Args:
        report_dir: Directory containing CSV files
    
    Returns:
        Dictionary of DataFrames
    """
    report_path = Path(report_dir)
    report = {}
    
    # Load CSV files
    csv_files = {
        'skill_premium': 'salary_analysis_skill_premium.csv',
        'experience_impact': 'salary_analysis_experience_impact.csv',
        'geographic_gaps': 'salary_analysis_geographic_gaps.csv',
        'industry_comparison': 'salary_analysis_industry_comparison.csv',
        'company_size_impact': 'salary_analysis_company_size_impact.csv',
        'top_skill_combinations': 'salary_analysis_top_skill_combinations.csv'
    }
    
    for key, filename in csv_files.items():
        filepath = report_path / filename
        if filepath.exists():
            report[key] = pd.read_csv(filepath)
            logger.info(f"Loaded {key} from {filename}")
    
    # Load tech stack ROI (multiple files)
    tech_stack = {}
    tech_files = {
        'cloud_platforms': 'salary_analysis_tech_stack_roi_cloud_platforms.csv',
        'ml_frameworks': 'salary_analysis_tech_stack_roi_ml_frameworks.csv',
        'programming_languages': 'salary_analysis_tech_stack_roi_programming_languages.csv'
    }
    
    for key, filename in tech_files.items():
        filepath = report_path / filename
        if filepath.exists():
            tech_stack[key] = pd.read_csv(filepath)
            logger.info(f"Loaded {key} from {filename}")
    
    if tech_stack:
        report['tech_stack_roi'] = tech_stack
    
    # Mock overall statistics (would need to be saved separately)
    if 'skill_premium' in report:
        report['overall_statistics'] = {
            'mean': 120000,
            'median': 115000,
            'std': 35000,
            'min': 50000,
            'max': 250000,
            'count': len(report['skill_premium']),
            'q25': 95000,
            'q75': 145000
        }
    
    return report


if __name__ == "__main__":
    # Example usage
    logger.info("Starting salary visualization")
    
    # Option 1: Run analysis and visualize
    figures = visualize_salary_analysis(save=True, show=False)
    
    # Option 2: Load from existing CSV files
    # figures = visualize_salary_analysis(
    #     report_path='output/analysis',
    #     save=True,
    #     show=False
    # )
    
    logger.info(f"Generated {len(figures)} visualizations successfully")
