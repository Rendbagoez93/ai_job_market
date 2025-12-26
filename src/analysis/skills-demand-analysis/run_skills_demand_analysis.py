"""Runner script for Skills Demand & Talent Gap Analysis.

This script executes the complete skills demand and talent gap analysis.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from skills_demand_analyzer import SkillsDemandAnalyzer, run_skills_demand_analysis
from src.utils.logger import get_logger


logger = get_logger(__name__)


def main():
    """Main execution function."""
    try:
        logger.info("="*80)
        logger.info("STARTING SKILLS DEMAND & TALENT GAP ANALYSIS")
        logger.info("="*80)
        
        # Run complete analysis
        report = run_skills_demand_analysis(export=True)
        
        # Print summary to console
        print("\n" + "="*80)
        print("SKILLS DEMAND & TALENT GAP ANALYSIS SUMMARY")
        print("="*80)
        
        # 1. Overall skill demand statistics
        print("\n1. TOP 10 MOST IN-DEMAND SKILLS:")
        demand_ranking = report['skill_demand_ranking'].head(10)
        print(f"   {'Rank':<6} {'Skill':<30} {'Count':<10} {'Demand %':<12} {'Level'}")
        print(f"   {'-'*6} {'-'*30} {'-'*10} {'-'*12} {'-'*10}")
        for idx, row in demand_ranking.iterrows():
            print(f"   {row['rank']:<6} {row['skill_name']:<30} {row['count']:<10} "
                  f"{row['demand_percentage']:>10.1f}%  {row['demand_level']}")
        
        # 2. High-value skills
        print("\n2. TOP 10 HIGH-VALUE SKILLS (Salary Premium + Demand):")
        high_value = report['high_value_skills'].head(10)
        print(f"   {'Rank':<6} {'Skill':<25} {'Premium %':<12} {'Demand %':<12} {'Value Score':<12} {'Tier'}")
        print(f"   {'-'*6} {'-'*25} {'-'*12} {'-'*12} {'-'*12} {'-'*10}")
        for idx, row in high_value.iterrows():
            print(f"   {idx+1:<6} {row['skill_name']:<25} {row['premium_percentage']:>10.1f}%  "
                  f"{row['demand_percentage']:>10.1f}%  {row['value_score']:>10.1f}  {row['value_tier']}")
        
        # 3. Skill co-occurrence insights
        print("\n3. TOP 10 SKILL COMBINATIONS (Strongest Correlations):")
        if not report['skill_cooccurrence'].empty:
            cooccurrence = report['skill_cooccurrence'].head(10)
            print(f"   {'Rank':<6} {'Skill 1':<25} {'Skill 2':<25} {'Correlation':<12} {'Strength'}")
            print(f"   {'-'*6} {'-'*25} {'-'*25} {'-'*12} {'-'*10}")
            for idx, row in cooccurrence.iterrows():
                print(f"   {idx+1:<6} {row['skill_1']:<25} {row['skill_2']:<25} "
                      f"{row['correlation']:>10.3f}  {row['strength']}")
        else:
            print("   No significant skill correlations found")
        
        # 4. Talent gap insights
        print("\n4. TALENT GAP ANALYSIS:")
        talent_gap = report['talent_gap']
        
        print("\n   A. CRITICAL SKILLS (High Demand + High Premium):")
        critical = talent_gap['critical_skills']
        if not critical.empty:
            print(f"      Found {len(critical)} critical skills")
            for idx, row in critical.head(5).iterrows():
                print(f"      - {row['skill_name']}: {row['premium_percentage']:.1f}% premium, "
                      f"{row['demand_percentage']:.1f}% demand")
        else:
            print("      No critical skills identified")
        
        print("\n   B. EMERGING OPPORTUNITIES (Medium Demand + Very High Premium):")
        emerging = talent_gap['emerging_opportunities']
        if not emerging.empty:
            print(f"      Found {len(emerging)} emerging opportunities")
            for idx, row in emerging.head(5).iterrows():
                print(f"      - {row['skill_name']}: {row['premium_percentage']:.1f}% premium, "
                      f"{row['demand_percentage']:.1f}% demand")
        else:
            print("      No emerging opportunities identified")
        
        print("\n   C. OVERSUPPLIED SKILLS (High Demand + Low Premium):")
        oversupplied = talent_gap['oversupplied_skills']
        if not oversupplied.empty:
            print(f"      Found {len(oversupplied)} oversupplied skills")
            for idx, row in oversupplied.head(5).iterrows():
                print(f"      - {row['skill_name']}: {row['premium_percentage']:.1f}% premium, "
                      f"{row['demand_percentage']:.1f}% demand")
        else:
            print("      No oversupplied skills identified")
        
        print("\n   D. UNDERVALUED GEMS (Low Demand + High Premium):")
        undervalued = talent_gap['undervalued_gems']
        if not undervalued.empty:
            print(f"      Found {len(undervalued)} undervalued gems")
            for idx, row in undervalued.head(5).iterrows():
                print(f"      - {row['skill_name']}: {row['premium_percentage']:.1f}% premium, "
                      f"{row['demand_percentage']:.1f}% demand")
        else:
            print("      No undervalued gems identified")
        
        # 5. Top skill recommendations
        print("\n5. TOP 10 SKILL LEARNING RECOMMENDATIONS:")
        recommendations = report['recommendations'].head(10)
        print(f"   {'Rank':<6} {'Skill':<25} {'Value Score':<12} {'Learning ROI':<12} {'Priority'}")
        print(f"   {'-'*6} {'-'*25} {'-'*12} {'-'*12} {'-'*10}")
        for idx, row in recommendations.iterrows():
            print(f"   {idx+1:<6} {row['skill_name']:<25} {row['value_score']:>10.1f}  "
                  f"{row['learning_roi']:>10.1f}  {row['priority']}")
        
        # 6. Job title insights
        print("\n6. JOB TITLE ANALYSIS:")
        top_skills_by_job = report['top_skills_by_job']
        if not top_skills_by_job.empty:
            unique_titles = top_skills_by_job['job_title'].unique()[:3]
            for title in unique_titles:
                print(f"\n   {title}:")
                title_skills = top_skills_by_job[top_skills_by_job['job_title'] == title].head(5)
                for _, row in title_skills.iterrows():
                    print(f"      {row['rank']}. {row['skill']}: {row['prevalence_rate']:.1f}% prevalence")
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)
        print("\nDetailed results exported to: output/analysis/")
        print("\nExported files:")
        print("  - skills_demand_ranking.csv")
        print("  - skills_correlation_matrix.csv")
        print("  - skills_cooccurrence.csv")
        print("  - skills_prevalence_by_job_title.csv")
        print("  - skills_top_by_job_title.csv")
        print("  - skills_high_value.csv")
        print("  - skills_talent_gap_*.csv (4 files)")
        print("  - skills_recommendations.csv")
        
        logger.info("Skills demand analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in skills demand analysis: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
