import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from typing import Dict, Any
from utils.config_loader import get_config_loader
from utils.data_validator import DataValidator
from utils.logger import get_logger


logger = get_logger(__name__)


class DataValidationPipeline:
    
    def __init__(self):
        self.config = get_config_loader()
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        main_config = self.config.load('config')
        
        logger.info("Starting data validation")
        
        validator = DataValidator(df)
        
        expected_columns = main_config['columns']['raw_columns']
        validation_results = validator.run_all_validations(
            expected_columns=expected_columns
        )
        
        self._print_validation_report(validation_results)
        
        return validation_results
    
    def _print_validation_report(self, results: Dict[str, Any]) -> None:
        print("\n" + "="*60)
        print("DATA VALIDATION REPORT")
        print("="*60)
        
        print(f"\nDataset Shape: {results['shape']}")
        
        validation = results['validation_results']
        
        if 'columns' in validation:
            col_result = validation['columns']
            print(f"\nColumn Validation: {'✓ PASSED' if col_result['valid'] else '✗ FAILED'}")
            if col_result['missing_columns']:
                print(f"  Missing: {col_result['missing_columns']}")
            if col_result['extra_columns']:
                print(f"  Extra: {col_result['extra_columns']}")
        
        if 'missing_values' in validation:
            mv_result = validation['missing_values']
            print(f"\nMissing Values: {mv_result['total_missing']}")
            if mv_result['columns_with_missing']:
                for col, info in mv_result['columns_with_missing'].items():
                    print(f"  {col}: {info['count']} ({info['percentage']:.2f}%)")
        
        if 'duplicates' in validation:
            dup_result = validation['duplicates']
            status = '✓ NONE' if not dup_result['has_duplicates'] else f"✗ {dup_result['count']}"
            print(f"\nDuplicates: {status}")
        
        print("="*60)


def validate_data(df: pd.DataFrame) -> Dict[str, Any]:
    pipeline = DataValidationPipeline()
    return pipeline.validate_data(df)


if __name__ == "__main__":
    from load_data import load_raw_data
    
    df = load_raw_data()
    results = validate_data(df)