"""Runner script for Skills Demand Visualization.

This script generates comprehensive visualizations for skills demand analysis.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Add skills-demand-analysis directory to path
skills_analysis_dir = Path(__file__).parent.parent / 'analysis' / 'skills-demand-analysis'
sys.path.append(str(skills_analysis_dir))

from skills_demand_analyzer import run_skills_demand_analysis
from skills_demand_visualization import create_skills_demand_visualizations
from src.utils.logger import get_logger


logger = get_logger(__name__)


def main():
    """Main execution function."""
    try:
        logger.info("="*80)
        logger.info("SKILLS DEMAND VISUALIZATION RUNNER")
        logger.info("="*80)
        
        # Step 1: Run analysis (or load existing results)
        print("\n📊 Step 1: Running Skills Demand Analysis...")
        report = run_skills_demand_analysis(export=True)
        
        # Step 2: Generate visualizations
        print("\n🎨 Step 2: Generating Visualizations...")
        visualizer = create_skills_demand_visualizations(
            report_data=report,
            output_dir='output/visuals',
            top_n=15
        )
        
        print("\n" + "="*80)
        print("✅ VISUALIZATION GENERATION COMPLETE!")
        print("="*80)
        print(f"\n📁 Visualizations saved to: output/visuals/")
        print("\nGenerated visualizations:")
        print("  1. skills_demand_ranking.png")
        print("  2. skills_correlation_heatmap.png")
        print("  3. skills_cooccurrence_network.png")
        print("  4. skills_high_value.png")
        print("  5. skills_talent_gap_analysis.png")
        print("  6. skills_recommendations.png")
        print("  7. skills_by_job_title.png")
        print("  8. skills_demand_vs_premium_quadrant.png")
        
        logger.info("Skills demand visualization completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in visualization generation: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
