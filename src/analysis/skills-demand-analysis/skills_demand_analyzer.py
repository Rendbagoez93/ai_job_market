"""Skills Demand & Talent Gap Analyzer.

This module analyzes skill demand patterns, correlations, and identifies high-value skills
in the AI job market.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
import warnings

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.utils.logger import get_logger
from src.utils.file_handler import FileHandler

warnings.filterwarnings('ignore')
logger = get_logger(__name__)


class SkillsDemandAnalyzer:
    """Analyzer for skills demand and talent gap analysis."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.file_handler = FileHandler()
        self.skills_data = None
        self.salary_data = None
        self.skill_frequency = None
        self.merged_data = None
        
        logger.info("SkillsDemandAnalyzer initialized")
    
    def load_data(self) -> None:
        """Load required datasets."""
        logger.info("Loading data for skills demand analysis...")
        
        try:
            # Load skills enriched data
            skills_path = project_root / 'data' / 'enriched' / 'skills_enriched.csv'
            self.skills_data = pd.read_csv(skills_path)
            logger.info(f"Loaded skills data: {self.skills_data.shape}")
            
            # Load salary data
            salary_path = project_root / 'data' / 'enriched' / 'salary_enriched.csv'
            self.salary_data = pd.read_csv(salary_path)
            logger.info(f"Loaded salary data: {self.salary_data.shape}")
            
            # Load skill frequency
            freq_path = project_root / 'data' / 'dictionary' / 'skill_frequency.csv'
            self.skill_frequency = pd.read_csv(freq_path)
            logger.info(f"Loaded skill frequency: {self.skill_frequency.shape}")
            
            # Merge skills and salary data
            self.merged_data = pd.merge(
                self.skills_data,
                self.salary_data[['job_id', 'salary_avg', 'salary_cluster']],
                on='job_id',
                how='inner'
            )
            logger.info(f"Merged dataset shape: {self.merged_data.shape}")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def get_skill_demand_ranking(self) -> pd.DataFrame:
        """
        Analyze skill demand using skill_frequency.csv.
        
        Returns:
            DataFrame with skill demand metrics
        """
        logger.info("Analyzing skill demand ranking...")
        
        # Clean the skill frequency data
        df = self.skill_frequency.copy()
        
        # Handle unnamed columns if present
        if 'Unnamed: 0' in df.columns:
            df = df.rename(columns={'Unnamed: 0': 'skill_name'})
        
        # Calculate demand metrics
        total_jobs = self.merged_data['job_id'].nunique()
        df['demand_percentage'] = (df['count'] / total_jobs * 100).round(2)
        df['rank'] = range(1, len(df) + 1)
        
        # Categorize demand levels
        df['demand_level'] = pd.cut(
            df['demand_percentage'],
            bins=[0, 10, 20, 30, 100],
            labels=['Low', 'Medium', 'High', 'Very High']
        )
        
        logger.info(f"Skill demand ranking completed for {len(df)} skills")
        return df
    
    def create_skill_correlation_matrix(self) -> pd.DataFrame:
        """
        Create correlation matrix of skill binary features.
        
        Returns:
            Correlation matrix DataFrame
        """
        logger.info("Creating skill correlation matrix...")
        
        # Get all skill binary columns (they start with 'skill_')
        skill_columns = [col for col in self.merged_data.columns 
                        if col.startswith('skill_') and col != 'skills']
        
        if not skill_columns:
            logger.warning("No skill binary columns found")
            return pd.DataFrame()
        
        # Calculate correlation matrix
        correlation_matrix = self.merged_data[skill_columns].corr()
        
        # Clean column names for better readability
        correlation_matrix.columns = [col.replace('skill_', '').replace('_', ' ').title() 
                                      for col in correlation_matrix.columns]
        correlation_matrix.index = [idx.replace('skill_', '').replace('_', ' ').title() 
                                   for idx in correlation_matrix.index]
        
        logger.info(f"Correlation matrix created: {correlation_matrix.shape}")
        return correlation_matrix
    
    def analyze_skill_cooccurrence(self, min_correlation: float = 0.3) -> pd.DataFrame:
        """
        Analyze skill co-occurrence patterns.
        
        Args:
            min_correlation: Minimum correlation threshold
            
        Returns:
            DataFrame with skill pairs and their correlation
        """
        logger.info("Analyzing skill co-occurrence patterns...")
        
        # Get correlation matrix
        corr_matrix = self.create_skill_correlation_matrix()
        
        # Extract upper triangle to avoid duplicates
        skill_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                skill_1 = corr_matrix.columns[i]
                skill_2 = corr_matrix.columns[j]
                correlation = corr_matrix.iloc[i, j]
                
                if correlation >= min_correlation:
                    skill_pairs.append({
                        'skill_1': skill_1,
                        'skill_2': skill_2,
                        'correlation': correlation,
                        'strength': 'Strong' if correlation >= 0.6 else 'Moderate'
                    })
        
        df = pd.DataFrame(skill_pairs)
        if not df.empty:
            df = df.sort_values('correlation', ascending=False).reset_index(drop=True)
        
        logger.info(f"Found {len(df)} skill pairs with correlation >= {min_correlation}")
        return df
    
    def calculate_skill_prevalence_by_job_title(self) -> pd.DataFrame:
        """
        Group by job_title and calculate skill prevalence rates.
        
        Returns:
            DataFrame with skill prevalence by job title
        """
        logger.info("Calculating skill prevalence by job title...")
        
        # Get skill binary columns
        skill_columns = [col for col in self.merged_data.columns 
                        if col.startswith('skill_') and col != 'skills']
        
        if 'job_title' not in self.merged_data.columns:
            logger.warning("job_title column not found in data")
            return pd.DataFrame()
        
        # Group by job title and calculate mean (prevalence rate)
        prevalence = self.merged_data.groupby('job_title')[skill_columns].mean() * 100
        
        # Add job count
        job_counts = self.merged_data.groupby('job_title').size()
        prevalence['job_count'] = job_counts
        
        # Clean column names
        prevalence.columns = [col.replace('skill_', '').replace('_', ' ').title() 
                             if col != 'job_count' else col
                             for col in prevalence.columns]
        
        # Sort by job count
        prevalence = prevalence.sort_values('job_count', ascending=False)
        
        logger.info(f"Skill prevalence calculated for {len(prevalence)} job titles")
        return prevalence
    
    def identify_top_skills_by_job_title(self, top_n: int = 5) -> pd.DataFrame:
        """
        Identify top N skills for each job title.
        
        Args:
            top_n: Number of top skills to identify
            
        Returns:
            DataFrame with top skills per job title
        """
        logger.info(f"Identifying top {top_n} skills by job title...")
        
        prevalence = self.calculate_skill_prevalence_by_job_title()
        
        if prevalence.empty:
            return pd.DataFrame()
        
        # Exclude job_count column
        skill_cols = [col for col in prevalence.columns if col != 'job_count']
        
        results = []
        for job_title in prevalence.index:
            skills = prevalence.loc[job_title, skill_cols].sort_values(ascending=False)
            top_skills = skills.head(top_n)
            
            for rank, (skill, prevalence_rate) in enumerate(top_skills.items(), 1):
                results.append({
                    'job_title': job_title,
                    'rank': rank,
                    'skill': skill,
                    'prevalence_rate': round(prevalence_rate, 2),
                    'job_count': prevalence.loc[job_title, 'job_count']
                })
        
        df = pd.DataFrame(results)
        logger.info(f"Identified top skills for {df['job_title'].nunique()} job titles")
        return df
    
    def identify_high_value_skills(self) -> pd.DataFrame:
        """
        Cross-reference skills with salary data to identify high-value skills.
        
        Returns:
            DataFrame with high-value skills analysis
        """
        logger.info("Identifying high-value skills...")
        
        # Get skill binary columns
        skill_columns = [col for col in self.merged_data.columns 
                        if col.startswith('skill_') and col != 'skills']
        
        results = []
        overall_avg_salary = self.merged_data['salary_avg'].mean()
        
        for skill_col in skill_columns:
            # Get jobs with and without this skill
            with_skill = self.merged_data[self.merged_data[skill_col] == 1]['salary_avg']
            without_skill = self.merged_data[self.merged_data[skill_col] == 0]['salary_avg']
            
            if len(with_skill) < 2 or len(without_skill) < 2:
                continue
            
            # Calculate statistics
            avg_salary_with = with_skill.mean()
            avg_salary_without = without_skill.mean()
            salary_premium = avg_salary_with - overall_avg_salary
            premium_pct = ((avg_salary_with / overall_avg_salary) - 1) * 100
            
            # Perform t-test
            t_stat, p_value = stats.ttest_ind(with_skill, without_skill)
            is_significant = p_value < 0.05
            
            # Get demand count
            demand_count = with_skill.count()
            demand_pct = (demand_count / len(self.merged_data)) * 100
            
            skill_name = skill_col.replace('skill_', '').replace('_', ' ').title()
            
            results.append({
                'skill_name': skill_name,
                'avg_salary_with_skill': round(avg_salary_with, 2),
                'avg_salary_without_skill': round(avg_salary_without, 2),
                'salary_premium': round(salary_premium, 2),
                'premium_percentage': round(premium_pct, 2),
                'demand_count': int(demand_count),
                'demand_percentage': round(demand_pct, 2),
                'p_value': round(p_value, 4),
                'is_significant': is_significant,
                't_statistic': round(t_stat, 4)
            })
        
        df = pd.DataFrame(results)
        
        if not df.empty:
            # Calculate value score (combination of premium and demand)
            df['value_score'] = (
                (df['premium_percentage'] / df['premium_percentage'].max()) * 0.5 +
                (df['demand_percentage'] / df['demand_percentage'].max()) * 0.5
            ) * 100
            df['value_score'] = df['value_score'].round(2)
            
            # Sort by value score
            df = df.sort_values('value_score', ascending=False).reset_index(drop=True)
            
            # Add value tier
            df['value_tier'] = pd.cut(
                df['value_score'],
                bins=[0, 33, 66, 100],
                labels=['Standard', 'High-Value', 'Premium']
            )
        
        logger.info(f"High-value skills analysis completed for {len(df)} skills")
        return df
    
    def analyze_talent_gap(self) -> Dict[str, pd.DataFrame]:
        """
        Identify talent gaps: high-demand + high-salary skills to prioritize.
        
        Returns:
            Dictionary with talent gap analysis results
        """
        logger.info("Analyzing talent gaps...")
        
        high_value_skills = self.identify_high_value_skills()
        
        # Critical skills: High demand (>20%) AND high premium (>10%) AND significant
        critical_skills = high_value_skills[
            (high_value_skills['demand_percentage'] > 20) &
            (high_value_skills['premium_percentage'] > 10) &
            (high_value_skills['is_significant'])
        ].copy()
        
        # Emerging opportunities: Medium demand (10-20%) AND very high premium (>20%)
        emerging_skills = high_value_skills[
            (high_value_skills['demand_percentage'].between(10, 20)) &
            (high_value_skills['premium_percentage'] > 20) &
            (high_value_skills['is_significant'])
        ].copy()
        
        # Oversupplied: High demand (>20%) AND low/negative premium (<5%)
        oversupplied_skills = high_value_skills[
            (high_value_skills['demand_percentage'] > 20) &
            (high_value_skills['premium_percentage'] < 5)
        ].copy()
        
        # Undervalued gems: Low demand (<15%) AND high premium (>15%)
        undervalued_skills = high_value_skills[
            (high_value_skills['demand_percentage'] < 15) &
            (high_value_skills['premium_percentage'] > 15) &
            (high_value_skills['is_significant'])
        ].copy()
        
        results = {
            'critical_skills': critical_skills,
            'emerging_opportunities': emerging_skills,
            'oversupplied_skills': oversupplied_skills,
            'undervalued_gems': undervalued_skills
        }
        
        logger.info(f"Talent gap analysis completed:")
        logger.info(f"  - Critical skills: {len(critical_skills)}")
        logger.info(f"  - Emerging opportunities: {len(emerging_skills)}")
        logger.info(f"  - Oversupplied skills: {len(oversupplied_skills)}")
        logger.info(f"  - Undervalued gems: {len(undervalued_skills)}")
        
        return results
    
    def generate_skill_recommendations(self, current_skills: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Generate skill acquisition recommendations.
        
        Args:
            current_skills: List of skills already possessed (optional)
            
        Returns:
            DataFrame with skill recommendations
        """
        logger.info("Generating skill recommendations...")
        
        high_value_skills = self.identify_high_value_skills()
        
        # Filter out current skills if provided
        if current_skills:
            current_skills_clean = [s.lower() for s in current_skills]
            high_value_skills = high_value_skills[
                ~high_value_skills['skill_name'].str.lower().isin(current_skills_clean)
            ]
        
        # Prioritize based on value score and significance
        recommendations = high_value_skills[
            high_value_skills['is_significant']
        ].copy()
        
        # Add recommendation priority
        recommendations['priority'] = pd.cut(
            recommendations['value_score'],
            bins=[0, 50, 75, 100],
            labels=['Medium', 'High', 'Critical']
        )
        
        # Add learning ROI estimate (premium * demand)
        recommendations['learning_roi'] = (
            recommendations['premium_percentage'] * 
            recommendations['demand_percentage'] / 100
        ).round(2)
        
        recommendations = recommendations.sort_values(
            ['value_score', 'learning_roi'], 
            ascending=[False, False]
        ).reset_index(drop=True)
        
        logger.info(f"Generated {len(recommendations)} skill recommendations")
        return recommendations
    
    def export_results(self, output_dir: Optional[Path] = None) -> None:
        """
        Export analysis results to CSV files.
        
        Args:
            output_dir: Directory to save results (default: output/analysis/)
        """
        if output_dir is None:
            output_dir = project_root / 'output' / 'analysis'
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Exporting results to {output_dir}...")
        
        try:
            # 1. Skill demand ranking
            demand_ranking = self.get_skill_demand_ranking()
            demand_path = output_dir / 'skills_demand_ranking.csv'
            demand_ranking.to_csv(demand_path, index=False)
            logger.info(f"Exported: {demand_path}")
            
            # 2. Skill correlation matrix
            correlation_matrix = self.create_skill_correlation_matrix()
            corr_path = output_dir / 'skills_correlation_matrix.csv'
            correlation_matrix.to_csv(corr_path)
            logger.info(f"Exported: {corr_path}")
            
            # 3. Skill co-occurrence
            cooccurrence = self.analyze_skill_cooccurrence()
            cooc_path = output_dir / 'skills_cooccurrence.csv'
            cooccurrence.to_csv(cooc_path, index=False)
            logger.info(f"Exported: {cooc_path}")
            
            # 4. Skill prevalence by job title
            prevalence = self.calculate_skill_prevalence_by_job_title()
            prev_path = output_dir / 'skills_prevalence_by_job_title.csv'
            prevalence.to_csv(prev_path)
            logger.info(f"Exported: {prev_path}")
            
            # 5. Top skills by job title
            top_skills = self.identify_top_skills_by_job_title()
            top_path = output_dir / 'skills_top_by_job_title.csv'
            top_skills.to_csv(top_path, index=False)
            logger.info(f"Exported: {top_path}")
            
            # 6. High-value skills
            high_value = self.identify_high_value_skills()
            value_path = output_dir / 'skills_high_value.csv'
            high_value.to_csv(value_path, index=False)
            logger.info(f"Exported: {value_path}")
            
            # 7. Talent gap analysis
            talent_gap = self.analyze_talent_gap()
            for category, df in talent_gap.items():
                gap_path = output_dir / f'skills_talent_gap_{category}.csv'
                df.to_csv(gap_path, index=False)
                logger.info(f"Exported: {gap_path}")
            
            # 8. Skill recommendations
            recommendations = self.generate_skill_recommendations()
            rec_path = output_dir / 'skills_recommendations.csv'
            recommendations.to_csv(rec_path, index=False)
            logger.info(f"Exported: {rec_path}")
            
            logger.info("All results exported successfully!")
            
        except Exception as e:
            logger.error(f"Error exporting results: {str(e)}")
            raise
    
    def run_complete_analysis(self, export: bool = True) -> Dict:
        """
        Run complete skills demand and talent gap analysis.
        
        Args:
            export: Whether to export results to CSV
            
        Returns:
            Dictionary with all analysis results
        """
        logger.info("="*80)
        logger.info("STARTING SKILLS DEMAND & TALENT GAP ANALYSIS")
        logger.info("="*80)
        
        # Load data
        self.load_data()
        
        # Run all analyses
        results = {
            'skill_demand_ranking': self.get_skill_demand_ranking(),
            'correlation_matrix': self.create_skill_correlation_matrix(),
            'skill_cooccurrence': self.analyze_skill_cooccurrence(),
            'skill_prevalence_by_job': self.calculate_skill_prevalence_by_job_title(),
            'top_skills_by_job': self.identify_top_skills_by_job_title(),
            'high_value_skills': self.identify_high_value_skills(),
            'talent_gap': self.analyze_talent_gap(),
            'recommendations': self.generate_skill_recommendations()
        }
        
        # Export if requested
        if export:
            self.export_results()
        
        logger.info("="*80)
        logger.info("SKILLS DEMAND ANALYSIS COMPLETED")
        logger.info("="*80)
        
        return results


def run_skills_demand_analysis(export: bool = True) -> Dict:
    """
    Convenience function to run skills demand analysis.
    
    Args:
        export: Whether to export results to CSV
        
    Returns:
        Dictionary with all analysis results
    """
    analyzer = SkillsDemandAnalyzer()
    return analyzer.run_complete_analysis(export=export)


if __name__ == '__main__':
    # Run the analysis
    report = run_skills_demand_analysis(export=True)
    
    print("\nAnalysis completed! Check output/analysis/ for detailed results.")
