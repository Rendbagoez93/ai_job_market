"""Skills Demand & Talent Gap Visualization Module.

This module provides comprehensive visualizations for skills demand analysis,
including demand rankings, correlation heatmaps, talent gap analysis,
and skill recommendations using matplotlib and seaborn.
"""

import sys
from pathlib import Path
import warnings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional, Tuple, List

sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import get_logger

warnings.filterwarnings('ignore')


logger = get_logger(__name__)


class SkillsDemandVisualizer:
    """Create comprehensive visualizations for skills demand analysis."""
    
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
            'warning': '#F9C74F',
            'info': '#4D908E',
            'neutral': '#6C757D',
            'palette': sns.color_palette('husl', 20),
            'sequential': sns.color_palette('viridis', 10),
            'diverging': sns.color_palette('RdYlGn', 10)
        }
        
        logger.info("SkillsDemandVisualizer initialized")
    
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
    
    def plot_skill_demand_ranking(
        self,
        top_n: int = 20,
        save: bool = True
    ) -> plt.Figure:
        """Visualize top skills by demand ranking.
        
        Args:
            top_n: Number of top skills to display
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info(f"Creating skill demand ranking visualization (top {top_n})")
        
        df = self.report['skill_demand_ranking'].head(top_n)
        
        fig, ax = plt.subplots(figsize=(12, 8), dpi=self.dpi)
        
        # Create color mapping by demand level
        demand_colors = {
            'Very High': self.colors['danger'],
            'High': self.colors['warning'],
            'Medium': self.colors['info'],
            'Low': self.colors['neutral']
        }
        colors = [demand_colors.get(level, self.colors['primary']) for level in df['demand_level']]
        
        # Horizontal bar chart
        bars = ax.barh(range(len(df)), df['demand_percentage'], color=colors)
        
        # Set labels
        ax.set_yticks(range(len(df)))
        ax.set_yticklabels(df['skill_name'])
        ax.set_xlabel('Demand (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n} Most In-Demand Skills', fontsize=14, fontweight='bold', pad=20)
        
        # Add value labels
        for i, (idx, row) in enumerate(df.iterrows()):
            ax.text(row['demand_percentage'] + 0.5, i, 
                   f"{row['demand_percentage']:.1f}% ({row['count']})",
                   va='center', fontsize=9)
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=demand_colors[level], label=level) 
                          for level in ['Very High', 'High', 'Medium', 'Low'] 
                          if level in df['demand_level'].values]
        ax.legend(handles=legend_elements, loc='lower right', title='Demand Level')
        
        # Invert y-axis to show highest at top
        ax.invert_yaxis()
        
        if save:
            self._save_figure(fig, 'skills_demand_ranking.png')
        
        return fig
    
    def plot_skill_correlation_heatmap(
        self,
        top_n: int = 15,
        save: bool = True
    ) -> plt.Figure:
        """Visualize skill correlation matrix as heatmap.
        
        Args:
            top_n: Number of top skills to include
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info(f"Creating skill correlation heatmap (top {top_n})")
        
        corr_matrix = self.report['correlation_matrix']
        
        # Get top N skills by average correlation
        avg_corr = corr_matrix.mean().sort_values(ascending=False)
        top_skills = avg_corr.head(top_n).index
        corr_subset = corr_matrix.loc[top_skills, top_skills]
        
        fig, ax = plt.subplots(figsize=(14, 12), dpi=self.dpi)
        
        # Create heatmap
        sns.heatmap(
            corr_subset,
            annot=True,
            fmt='.2f',
            cmap='RdYlGn',
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={'label': 'Correlation Coefficient'},
            ax=ax,
            vmin=-1,
            vmax=1
        )
        
        ax.set_title(f'Skill Correlation Matrix - Top {top_n} Skills', 
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        plt.setp(ax.get_yticklabels(), rotation=0)
        
        if save:
            self._save_figure(fig, 'skills_correlation_heatmap.png')
        
        return fig
    
    def plot_skill_cooccurrence_network(
        self,
        top_n: int = 20,
        min_correlation: float = 0.4,
        save: bool = True
    ) -> plt.Figure:
        """Visualize skill co-occurrence as network plot.
        
        Args:
            top_n: Number of top skill pairs to show
            min_correlation: Minimum correlation threshold
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info("Creating skill co-occurrence network visualization")
        
        df = self.report['skill_cooccurrence']
        
        # Check if DataFrame is empty or missing required columns
        if df.empty or 'correlation' not in df.columns:
            logger.warning("No skill co-occurrences to visualize")
            return None
        
        df = df[df['correlation'] >= min_correlation].head(top_n)
        
        if df.empty:
            logger.warning(f"No skill co-occurrences with correlation >= {min_correlation}")
            return None
        
        fig, ax = plt.subplots(figsize=(14, 10), dpi=self.dpi)
        
        # Create vertical bar chart
        skill_pairs = [f"{row['skill_1']}\n+\n{row['skill_2']}" 
                      for _, row in df.iterrows()]
        
        colors = [self.colors['danger'] if strength == 'Strong' else self.colors['info'] 
                 for strength in df['strength']]
        
        bars = ax.bar(range(len(df)), df['correlation'], color=colors)
        
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(skill_pairs, rotation=45, ha='right', fontsize=8)
        ax.set_ylabel('Correlation Coefficient', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n} Skill Combinations (Correlation ≥ {min_correlation})', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim(0, 1)
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, df['correlation'])):
            ax.text(bar.get_x() + bar.get_width()/2, val + 0.02,
                   f'{val:.2f}', ha='center', fontsize=9, fontweight='bold')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.colors['danger'], label='Strong (≥0.6)'),
            Patch(facecolor=self.colors['info'], label='Moderate (0.3-0.6)')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        if save:
            self._save_figure(fig, 'skills_cooccurrence_network.png')
        
        return fig
    
    def plot_high_value_skills(
        self,
        top_n: int = 15,
        save: bool = True
    ) -> plt.Figure:
        """Visualize high-value skills with premium and demand.
        
        Args:
            top_n: Number of top skills to display
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info(f"Creating high-value skills visualization (top {top_n})")
        
        df = self.report['high_value_skills'].head(top_n)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), dpi=self.dpi)
        fig.suptitle(f'Top {top_n} High-Value Skills Analysis', 
                    fontsize=16, fontweight='bold')
        
        # Left: Salary Premium
        colors1 = [self.colors['success'] if sig else self.colors['neutral'] 
                   for sig in df['is_significant']]
        
        bars1 = ax1.barh(range(len(df)), df['premium_percentage'], color=colors1)
        ax1.set_yticks(range(len(df)))
        ax1.set_yticklabels(df['skill_name'])
        ax1.set_xlabel('Salary Premium (%)', fontsize=12, fontweight='bold')
        ax1.set_title('Salary Premium Impact', fontsize=13, fontweight='bold')
        ax1.invert_yaxis()
        
        for i, (idx, row) in enumerate(df.iterrows()):
            ax1.text(row['premium_percentage'] + 0.5, i,
                    f"{row['premium_percentage']:.1f}%",
                    va='center', fontsize=9)
        
        # Right: Demand vs Premium Scatter
        scatter_colors = [self.colors['danger'] if tier == 'Premium' 
                         else self.colors['warning'] if tier == 'High-Value'
                         else self.colors['info']
                         for tier in df['value_tier']]
        
        scatter = ax2.scatter(
            df['demand_percentage'],
            df['premium_percentage'],
            s=df['value_score'] * 5,
            c=scatter_colors,
            alpha=0.6,
            edgecolors='black',
            linewidth=1.5
        )
        
        # Add labels for each point
        for idx, row in df.iterrows():
            ax2.annotate(
                row['skill_name'],
                (row['demand_percentage'], row['premium_percentage']),
                fontsize=8,
                ha='center',
                xytext=(5, 5),
                textcoords='offset points'
            )
        
        ax2.set_xlabel('Demand (%)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Salary Premium (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Demand vs Premium Matrix', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Add quadrant lines
        ax2.axhline(y=df['premium_percentage'].median(), color='gray', 
                   linestyle='--', alpha=0.5, linewidth=1)
        ax2.axvline(x=df['demand_percentage'].median(), color='gray', 
                   linestyle='--', alpha=0.5, linewidth=1)
        
        # Legend for scatter
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.colors['danger'], label='Premium'),
            Patch(facecolor=self.colors['warning'], label='High-Value'),
            Patch(facecolor=self.colors['info'], label='Standard')
        ]
        ax2.legend(handles=legend_elements, loc='upper left', title='Value Tier')
        
        if save:
            self._save_figure(fig, 'skills_high_value.png')
        
        return fig
    
    def plot_talent_gap_analysis(
        self,
        save: bool = True
    ) -> plt.Figure:
        """Visualize talent gap analysis across all categories.
        
        Args:
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info("Creating talent gap analysis visualization")
        
        talent_gap = self.report['talent_gap']
        
        fig = plt.figure(figsize=(16, 12), dpi=self.dpi)
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        fig.suptitle('Talent Gap Analysis: Strategic Skill Categories', 
                    fontsize=16, fontweight='bold')
        
        # 1. Critical Skills (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        critical = talent_gap['critical_skills'].head(10)
        
        if not critical.empty:
            bars1 = ax1.barh(range(len(critical)), critical['value_score'], 
                            color=self.colors['danger'], alpha=0.7)
            ax1.set_yticks(range(len(critical)))
            ax1.set_yticklabels(critical['skill_name'], fontsize=9)
            ax1.set_xlabel('Value Score', fontsize=10, fontweight='bold')
            ax1.set_title('🎯 Critical Skills\n(High Demand + High Premium)', 
                         fontsize=11, fontweight='bold', color=self.colors['danger'])
            ax1.invert_yaxis()
            
            for i, val in enumerate(critical['value_score']):
                ax1.text(val + 1, i, f'{val:.1f}', va='center', fontsize=8)
        else:
            ax1.text(0.5, 0.5, 'No critical skills identified', 
                    ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('🎯 Critical Skills', fontsize=11, fontweight='bold')
        
        # 2. Emerging Opportunities (top right)
        ax2 = fig.add_subplot(gs[0, 1])
        emerging = talent_gap['emerging_opportunities'].head(10)
        
        if not emerging.empty:
            bars2 = ax2.barh(range(len(emerging)), emerging['premium_percentage'], 
                            color=self.colors['warning'], alpha=0.7)
            ax2.set_yticks(range(len(emerging)))
            ax2.set_yticklabels(emerging['skill_name'], fontsize=9)
            ax2.set_xlabel('Premium (%)', fontsize=10, fontweight='bold')
            ax2.set_title('🚀 Emerging Opportunities\n(Medium Demand + Very High Premium)', 
                         fontsize=11, fontweight='bold', color=self.colors['warning'])
            ax2.invert_yaxis()
            
            for i, val in enumerate(emerging['premium_percentage']):
                ax2.text(val + 1, i, f'{val:.1f}%', va='center', fontsize=8)
        else:
            ax2.text(0.5, 0.5, 'No emerging opportunities identified', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('🚀 Emerging Opportunities', fontsize=11, fontweight='bold')
        
        # 3. Oversupplied Skills (bottom left)
        ax3 = fig.add_subplot(gs[1, 0])
        oversupplied = talent_gap['oversupplied_skills'].head(10)
        
        if not oversupplied.empty:
            bars3 = ax3.barh(range(len(oversupplied)), oversupplied['demand_percentage'], 
                            color=self.colors['neutral'], alpha=0.7)
            ax3.set_yticks(range(len(oversupplied)))
            ax3.set_yticklabels(oversupplied['skill_name'], fontsize=9)
            ax3.set_xlabel('Demand (%)', fontsize=10, fontweight='bold')
            ax3.set_title('⚠️ Oversupplied Skills\n(High Demand + Low Premium)', 
                         fontsize=11, fontweight='bold', color=self.colors['neutral'])
            ax3.invert_yaxis()
            
            for i, val in enumerate(oversupplied['demand_percentage']):
                ax3.text(val + 0.5, i, f'{val:.1f}%', va='center', fontsize=8)
        else:
            ax3.text(0.5, 0.5, 'No oversupplied skills identified', 
                    ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('⚠️ Oversupplied Skills', fontsize=11, fontweight='bold')
        
        # 4. Undervalued Gems (bottom right)
        ax4 = fig.add_subplot(gs[1, 1])
        undervalued = talent_gap['undervalued_gems'].head(10)
        
        if not undervalued.empty:
            # Scatter plot showing premium vs demand
            scatter = ax4.scatter(
                undervalued['demand_percentage'],
                undervalued['premium_percentage'],
                s=undervalued['value_score'] * 5,
                c=self.colors['success'],
                alpha=0.6,
                edgecolors='black',
                linewidth=1.5
            )
            
            for idx, row in undervalued.iterrows():
                ax4.annotate(
                    row['skill_name'],
                    (row['demand_percentage'], row['premium_percentage']),
                    fontsize=7,
                    ha='center',
                    xytext=(3, 3),
                    textcoords='offset points'
                )
            
            ax4.set_xlabel('Demand (%)', fontsize=10, fontweight='bold')
            ax4.set_ylabel('Premium (%)', fontsize=10, fontweight='bold')
            ax4.set_title('💎 Undervalued Gems\n(Low Demand + High Premium)', 
                         fontsize=11, fontweight='bold', color=self.colors['success'])
            ax4.grid(True, alpha=0.3)
        else:
            ax4.text(0.5, 0.5, 'No undervalued gems identified', 
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('💎 Undervalued Gems', fontsize=11, fontweight='bold')
        
        if save:
            self._save_figure(fig, 'skills_talent_gap_analysis.png', tight=False)
        
        return fig
    
    def plot_skill_recommendations(
        self,
        top_n: int = 15,
        save: bool = True
    ) -> plt.Figure:
        """Visualize skill learning recommendations.
        
        Args:
            top_n: Number of top recommendations to show
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info(f"Creating skill recommendations visualization (top {top_n})")
        
        df = self.report['recommendations'].head(top_n)
        
        # Check if DataFrame is empty
        if df.empty:
            logger.warning("No skill recommendations to visualize")
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), dpi=self.dpi)
        fig.suptitle(f'Top {top_n} Skill Learning Recommendations', 
                    fontsize=16, fontweight='bold')
        
        # Left: Value Score ranking
        priority_colors = {
            'Critical': self.colors['danger'],
            'High': self.colors['warning'],
            'Medium': self.colors['info']
        }
        colors1 = [priority_colors.get(p, self.colors['primary']) for p in df['priority']]
        
        bars1 = ax1.barh(range(len(df)), df['value_score'], color=colors1)
        ax1.set_yticks(range(len(df)))
        ax1.set_yticklabels(df['skill_name'], fontsize=9)
        ax1.set_xlabel('Value Score', fontsize=12, fontweight='bold')
        ax1.set_title('Overall Value Score', fontsize=13, fontweight='bold')
        ax1.invert_yaxis()
        
        for i, (idx, row) in enumerate(df.iterrows()):
            ax1.text(row['value_score'] + 0.5, i,
                    f"{row['value_score']:.1f}",
                    va='center', fontsize=9)
        
        # Right: Learning ROI
        bars2 = ax2.barh(range(len(df)), df['learning_roi'], 
                        color=self.colors['success'], alpha=0.7)
        ax2.set_yticks(range(len(df)))
        ax2.set_yticklabels(df['skill_name'], fontsize=9)
        ax2.set_xlabel('Learning ROI (Premium × Demand)', fontsize=12, fontweight='bold')
        ax2.set_title('Expected Return on Investment', fontsize=13, fontweight='bold')
        ax2.invert_yaxis()
        
        for i, (idx, row) in enumerate(df.iterrows()):
            ax2.text(row['learning_roi'] + 0.5, i,
                    f"{row['learning_roi']:.1f}",
                    va='center', fontsize=9)
        
        # Add legend for priority
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=priority_colors[p], label=p) 
                          for p in ['Critical', 'High', 'Medium'] 
                          if p in df['priority'].values]
        ax1.legend(handles=legend_elements, loc='lower right', title='Priority')
        
        if save:
            self._save_figure(fig, 'skills_recommendations.png')
        
        return fig
    
    def plot_skills_by_job_title(
        self,
        job_titles: Optional[List[str]] = None,
        top_skills: int = 8,
        save: bool = True
    ) -> plt.Figure:
        """Visualize top skills by job title.
        
        Args:
            job_titles: List of job titles to visualize (default: top 4 by job count)
            top_skills: Number of skills per job title
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info("Creating skills by job title visualization")
        
        df = self.report['top_skills_by_job']
        
        if job_titles is None:
            # Get top job titles by count
            top_jobs = df.groupby('job_title')['job_count'].first().nlargest(4)
            job_titles = top_jobs.index.tolist()
        
        # Filter for selected job titles and top skills
        df_filtered = df[df['job_title'].isin(job_titles)]
        df_filtered = df_filtered[df_filtered['rank'] <= top_skills]
        
        n_jobs = len(job_titles)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=self.dpi)
        axes = axes.flatten()
        
        fig.suptitle('Top Skills Required by Job Title', 
                    fontsize=16, fontweight='bold')
        
        for idx, job_title in enumerate(job_titles):
            if idx >= len(axes):
                break
                
            ax = axes[idx]
            job_data = df_filtered[df_filtered['job_title'] == job_title]
            
            if job_data.empty:
                ax.text(0.5, 0.5, f'No data for {job_title}', 
                       ha='center', va='center', transform=ax.transAxes)
                continue
            
            # Create color gradient
            colors = sns.color_palette('viridis', len(job_data))
            
            bars = ax.barh(range(len(job_data)), job_data['prevalence_rate'], 
                          color=colors)
            
            ax.set_yticks(range(len(job_data)))
            ax.set_yticklabels(job_data['skill'], fontsize=9)
            ax.set_xlabel('Prevalence Rate (%)', fontsize=10, fontweight='bold')
            ax.set_title(f'{job_title}\n({job_data["job_count"].iloc[0]} jobs)', 
                        fontsize=11, fontweight='bold')
            ax.invert_yaxis()
            ax.set_xlim(0, 100)
            
            # Add value labels
            for i, val in enumerate(job_data['prevalence_rate']):
                ax.text(val + 1, i, f'{val:.1f}%', va='center', fontsize=8)
        
        # Hide extra subplots
        for idx in range(len(job_titles), len(axes)):
            axes[idx].axis('off')
        
        if save:
            self._save_figure(fig, 'skills_by_job_title.png', tight=False)
        
        return fig
    
    def plot_demand_vs_premium_quadrant(
        self,
        save: bool = True
    ) -> plt.Figure:
        """Create quadrant analysis of demand vs premium.
        
        Args:
            save: Whether to save the figure
        
        Returns:
            Matplotlib figure
        """
        logger.info("Creating demand vs premium quadrant analysis")
        
        df = self.report['high_value_skills']
        
        fig, ax = plt.subplots(figsize=(14, 10), dpi=self.dpi)
        
        # Calculate medians for quadrant lines
        demand_median = df['demand_percentage'].median()
        premium_median = df['premium_percentage'].median()
        
        # Color by value tier
        tier_colors = {
            'Premium': self.colors['danger'],
            'High-Value': self.colors['warning'],
            'Standard': self.colors['info']
        }
        colors = [tier_colors.get(tier, self.colors['primary']) for tier in df['value_tier']]
        
        # Scatter plot
        scatter = ax.scatter(
            df['demand_percentage'],
            df['premium_percentage'],
            s=df['value_score'] * 3,
            c=colors,
            alpha=0.6,
            edgecolors='black',
            linewidth=1
        )
        
        # Add labels for high-value skills
        high_value = df[df['value_score'] > 70]
        for idx, row in high_value.iterrows():
            ax.annotate(
                row['skill_name'],
                (row['demand_percentage'], row['premium_percentage']),
                fontsize=8,
                ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7),
                xytext=(5, 5),
                textcoords='offset points'
            )
        
        # Add quadrant lines
        ax.axhline(y=premium_median, color='gray', linestyle='--', 
                  alpha=0.7, linewidth=2, label=f'Median Premium: {premium_median:.1f}%')
        ax.axvline(x=demand_median, color='gray', linestyle='--', 
                  alpha=0.7, linewidth=2, label=f'Median Demand: {demand_median:.1f}%')
        
        # Add quadrant labels
        ax.text(0.95, 0.95, 'HIGH DEMAND\nHIGH PREMIUM\n(Critical)', 
               transform=ax.transAxes, ha='right', va='top',
               fontsize=10, fontweight='bold', 
               bbox=dict(boxstyle='round', facecolor=self.colors['danger'], alpha=0.3))
        
        ax.text(0.05, 0.95, 'LOW DEMAND\nHIGH PREMIUM\n(Niche Gems)', 
               transform=ax.transAxes, ha='left', va='top',
               fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor=self.colors['success'], alpha=0.3))
        
        ax.text(0.95, 0.05, 'HIGH DEMAND\nLOW PREMIUM\n(Oversupplied)', 
               transform=ax.transAxes, ha='right', va='bottom',
               fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor=self.colors['neutral'], alpha=0.3))
        
        ax.text(0.05, 0.05, 'LOW DEMAND\nLOW PREMIUM\n(Low Value)', 
               transform=ax.transAxes, ha='left', va='bottom',
               fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.3))
        
        ax.set_xlabel('Demand (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Salary Premium (%)', fontsize=12, fontweight='bold')
        ax.set_title('Skills Demand vs Premium Quadrant Analysis', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left', framealpha=0.9)
        
        if save:
            self._save_figure(fig, 'skills_demand_vs_premium_quadrant.png')
        
        return fig
    
    def create_complete_report(
        self,
        output_dir: str = 'output/visuals',
        top_n: int = 15
    ) -> None:
        """Generate all visualizations for the complete report.
        
        Args:
            output_dir: Directory to save visualizations
            top_n: Number of top items to show in each visualization
        """
        logger.info("="*80)
        logger.info("GENERATING COMPLETE SKILLS DEMAND VISUALIZATION REPORT")
        logger.info("="*80)
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate all visualizations
        logger.info("1. Skill Demand Ranking...")
        self.plot_skill_demand_ranking(top_n=top_n, save=True)
        
        logger.info("2. Skill Correlation Heatmap...")
        self.plot_skill_correlation_heatmap(top_n=top_n, save=True)
        
        logger.info("3. Skill Co-occurrence Network...")
        self.plot_skill_cooccurrence_network(top_n=20, save=True)
        
        logger.info("4. High-Value Skills...")
        self.plot_high_value_skills(top_n=top_n, save=True)
        
        logger.info("5. Talent Gap Analysis...")
        self.plot_talent_gap_analysis(save=True)
        
        logger.info("6. Skill Recommendations...")
        self.plot_skill_recommendations(top_n=top_n, save=True)
        
        logger.info("7. Skills by Job Title...")
        self.plot_skills_by_job_title(save=True)
        
        logger.info("8. Demand vs Premium Quadrant...")
        self.plot_demand_vs_premium_quadrant(save=True)
        
        logger.info("="*80)
        logger.info(f"COMPLETE REPORT GENERATED: {output_dir}")
        logger.info("="*80)
        
        plt.close('all')


def create_skills_demand_visualizations(
    report_data: Dict,
    output_dir: str = 'output/visuals',
    top_n: int = 15
) -> SkillsDemandVisualizer:
    """Convenience function to create skills demand visualizations.
    
    Args:
        report_data: Dictionary containing analysis results
        output_dir: Directory to save visualizations
        top_n: Number of top items to show
    
    Returns:
        SkillsDemandVisualizer instance
    """
    visualizer = SkillsDemandVisualizer(report_data)
    visualizer.create_complete_report(output_dir=output_dir, top_n=top_n)
    return visualizer


if __name__ == '__main__':
    # Example usage
    print("This module is meant to be imported and used with analysis results.")
    print("\nExample usage:")
    print("  from skills_demand_visualization import create_skills_demand_visualizations")
    print("  from src.analysis.skills_demand_analyzer import run_skills_demand_analysis")
    print("")
    print("  report = run_skills_demand_analysis()")
    print("  visualizer = create_skills_demand_visualizations(report)")
