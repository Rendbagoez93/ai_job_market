"""Main entry point for AI Job Market Salary Intelligence Analysis.

This script provides a unified command-line interface to run salary analysis
and generate visualizations.

Usage:
    python main.py --analysis          # Run salary analysis only
    python main.py --visualize         # Generate visualizations only
    python main.py --all               # Run both analysis and visualizations
    python main.py                     # Default: run both
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.analysis.salary_intelligence import run_salary_analysis
from src.visuals.salary_visualizer import visualize_salary_analysis
from src.utils.logger import get_logger


logger = get_logger(__name__)


def run_analysis(export: bool = True) -> dict:
    """Run salary intelligence analysis.
    
    Args:
        export: Whether to export results to CSV files
    
    Returns:
        Dictionary containing analysis results
    """
    logger.info("="*80)
    logger.info("RUNNING SALARY INTELLIGENCE ANALYSIS")
    logger.info("="*80)
    
    print("\n" + "="*80)
    print("SALARY INTELLIGENCE ANALYSIS")
    print("="*80)
    print("Starting analysis...")
    
    report = run_salary_analysis(export=export)
    
    print("\n✓ Analysis completed successfully!")
    print(f"  - Analyzed {report['overall_statistics']['count']:,} job postings")
    print(f"  - Average Salary: ${report['overall_statistics']['mean']:,.2f}")
    print(f"  - Median Salary: ${report['overall_statistics']['median']:,.2f}")
    
    if export:
        print("  - Results exported to: output/analysis/")
    
    return report


def run_visualizations(report_data: dict = None) -> dict:
    """Generate salary visualizations.
    
    Args:
        report_data: Pre-loaded report data (optional)
    
    Returns:
        Dictionary of generated figures
    """
    logger.info("="*80)
    logger.info("GENERATING VISUALIZATIONS")
    logger.info("="*80)
    
    print("\n" + "="*80)
    print("VISUALIZATION GENERATION")
    print("="*80)
    print("Creating visualizations...")
    
    figures = visualize_salary_analysis(
        report_data=report_data,
        save=True,
        show=False
    )
    
    print("\n✓ Visualizations generated successfully!")
    print(f"  - Created {len(figures)} visualizations:")
    
    viz_names = {
        'overall_stats': 'Overall Statistics',
        'skill_premium': 'Skill Premium Analysis',
        'tech_stack': 'Tech Stack Comparison',
        'experience': 'Experience Level Impact',
        'geographic': 'Geographic Salary Gaps',
        'industry': 'Industry Comparison',
        'company_size': 'Company Size Impact',
        'skill_combos': 'Skill Combinations'
    }
    
    for name, fig in figures.items():
        if fig is not None:
            display_name = viz_names.get(name, name)
            print(f"    • {display_name}")
    
    print("  - Saved to: output/visuals/")
    
    return figures


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='AI Job Market Salary Intelligence Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    Run both analysis and visualizations
  python main.py --all              Run both analysis and visualizations
  python main.py --analysis         Run analysis only
  python main.py --visualize        Generate visualizations only
  python main.py --no-export        Run without exporting CSV files
        """
    )
    
    parser.add_argument(
        '--analysis',
        action='store_true',
        help='Run salary analysis only'
    )
    
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Generate visualizations only'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run both analysis and visualizations (default)'
    )
    
    parser.add_argument(
        '--no-export',
        action='store_true',
        help='Skip exporting CSV files (faster execution)'
    )
    
    args = parser.parse_args()
    
    try:
        print("\n" + "="*80)
        print("AI JOB MARKET SALARY INTELLIGENCE")
        print("="*80)
        
        # Determine what to run
        run_both = args.all or (not args.analysis and not args.visualize)
        do_analysis = args.analysis or run_both
        do_visualize = args.visualize or run_both
        export_results = not args.no_export
        
        report_data = None
        
        # Run analysis
        if do_analysis:
            report_data = run_analysis(export=export_results)
        
        # Generate visualizations
        if do_visualize:
            run_visualizations(report_data=report_data)
        
        # Final summary
        print("\n" + "="*80)
        print("EXECUTION COMPLETE")
        print("="*80)
        
        if do_analysis and export_results:
            print("✓ Analysis results: output/analysis/")
        
        if do_visualize:
            print("✓ Visualizations: output/visuals/")
        
        print("\nAll tasks completed successfully!")
        print("="*80 + "\n")
        
        logger.info("All tasks completed successfully")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        logger.warning("Operation cancelled by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\nERROR: {e}")
        logger.error(f"Error during execution: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
