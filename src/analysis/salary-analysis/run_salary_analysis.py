"""Runner script for Salary Intelligence Analysis.

This script executes the complete salary intelligence and compensation analysis.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from analysis.salary_intelligence import SalaryIntelligenceAnalyzer, run_salary_analysis
from utils.logger import get_logger


logger = get_logger(__name__)


def main():
    """Main execution function."""
    try:
        logger.info("="*80)
        logger.info("STARTING SALARY INTELLIGENCE ANALYSIS")
        logger.info("="*80)
        
        # Run complete analysis
        report = run_salary_analysis(export=True)
        
        # Print summary to console
        print("\n" + "="*80)
        print("SALARY INTELLIGENCE ANALYSIS SUMMARY")
        print("="*80)
        
        print("\n1. OVERALL STATISTICS:")
        stats = report['overall_statistics']
        print(f"   Average Salary: ${stats['mean']:,.2f}")
        print(f"   Median Salary: ${stats['median']:,.2f}")
        print(f"   Salary Range: ${stats['min']:,.2f} - ${stats['max']:,.2f}")
        print(f"   Total Jobs Analyzed: {stats['count']:,}")
        print(f"   Standard Deviation: ${stats['std']:,.2f}")
        print(f"   25th Percentile: ${stats['q25']:,.2f}")
        print(f"   75th Percentile: ${stats['q75']:,.2f}")
        
        print("\n2. TOP 10 HIGHEST PAYING SKILLS:")
        top_skills = report['skill_premium'].head(10)
        print(f"   {'Rank':<6} {'Skill':<25} {'Premium':<15} {'% Premium':<12} {'Significant'}")
        print(f"   {'-'*6} {'-'*25} {'-'*15} {'-'*12} {'-'*10}")
        for idx, (_, row) in enumerate(top_skills.iterrows(), 1):
            sig = "Yes" if row['is_significant'] else "No"
            print(f"   {idx:<6} {row['skill_name']:<25} ${row['salary_premium']:>12,.0f}  "
                  f"{row['premium_percentage']:>10.1f}%  {sig}")
        
        print("\n3. CLOUD PLATFORM COMPARISON:")
        if 'cloud_platforms' in report['tech_stack_roi']:
            cloud = report['tech_stack_roi']['cloud_platforms']
            for _, row in cloud.iterrows():
                print(f"   {row['skill_name']:<15} Premium: ${row['salary_premium']:>10,.0f} "
                      f"({row['premium_percentage']:>5.1f}%)")
        
        print("\n4. ML FRAMEWORK COMPARISON:")
        if 'ml_frameworks' in report['tech_stack_roi']:
            ml = report['tech_stack_roi']['ml_frameworks']
            for _, row in ml.iterrows():
                print(f"   {row['skill_name']:<25} Premium: ${row['salary_premium']:>10,.0f} "
                      f"({row['premium_percentage']:>5.1f}%)")
        
        print("\n5. EXPERIENCE LEVEL IMPACT:")
        exp_impact = report['experience_impact']
        for _, row in exp_impact.iterrows():
            pct = f"+{row['pct_increase']:.1f}%" if 'pct_increase' in row and pd.notna(row['pct_increase']) else "Base"
            print(f"   {row['experience_level']:<12} ${row['mean']:>12,.2f} "
                  f"(n={row['count']:>4}, {pct:>8})")
        
        print("\n6. GEOGRAPHIC SALARY GAPS:")
        geo = report['geographic_gaps']
        for _, row in geo.iterrows():
            print(f"   {row['location_region']:<15} Avg: ${row['mean']:>10,.0f}  "
                  f"Gap: ${row['gap_from_max']:>10,.0f} ({row['gap_percentage']:.1f}%)")
        
        print("\n7. INDUSTRY COMPARISON (Top 5):")
        industry = report['industry_comparison'].head(5)
        for _, row in industry.iterrows():
            print(f"   {row['industry']:<20} ${row['mean']:>12,.2f} "
                  f"({row['premium_percentage']:>+6.1f}% vs avg)")
        
        print("\n8. COMPANY SIZE IMPACT:")
        company = report['company_size_impact']
        for _, row in company.iterrows():
            print(f"   {row['company_size']:<12} ${row['mean']:>12,.2f} (n={row['count']})")
        
        print("\n9. TOP 5 SKILL COMBINATIONS:")
        combos = report['top_skill_combinations'].head(5)
        for idx, row in combos.iterrows():
            skills = row['skill_combination'][:60] + "..." if len(row['skill_combination']) > 60 else row['skill_combination']
            print(f"   {skills}")
            print(f"      → Avg: ${row['mean_salary']:,.0f}, "
                  f"Skills: {row['num_skills']}, "
                  f"$/Skill: ${row['salary_per_skill']:,.0f}")
        
        print("\n" + "="*80)
        print("Analysis complete! Results exported to output/analysis/")
        print("="*80 + "\n")
        
        logger.info("ANALYSIS COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        raise


if __name__ == "__main__":
    import pandas as pd
    main()
