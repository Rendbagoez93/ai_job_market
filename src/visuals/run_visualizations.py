"""Runner script for generating salary intelligence visualizations.

This script generates comprehensive visualizations for the salary intelligence analysis.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from visuals.salary_visualizer import visualize_salary_analysis
from utils.logger import get_logger


logger = get_logger(__name__)


def main():
    """Main execution function."""
    try:
        logger.info("="*80)
        logger.info("STARTING SALARY INTELLIGENCE VISUALIZATION")
        logger.info("="*80)
        
        # Generate all visualizations
        # This will run the analysis and create visualizations
        figures = visualize_salary_analysis(save=True, show=False)
        
        print("\n" + "="*80)
        print("VISUALIZATION GENERATION COMPLETE")
        print("="*80)
        print(f"\nGenerated {len(figures)} visualizations:")
        
        for name, fig in figures.items():
            if fig is not None:
                print(f"  ✓ {name}")
        
        print("\nAll visualizations saved to: output/visuals/")
        print("="*80 + "\n")
        
        logger.info("VISUALIZATION GENERATION COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        logger.error(f"Error during visualization: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        raise


if __name__ == "__main__":
    main()
