import pandas as pd
from typing import List, Optional, Dict, Any
from .logger import get_logger


logger = get_logger(__name__)


class DataValidator:
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.validation_results = {}
    
    def validate_columns(self, expected_columns: List[str]) -> Dict[str, Any]:
        actual_columns = set(self.df.columns)
        expected_set = set(expected_columns)
        
        missing = expected_set - actual_columns
        extra = actual_columns - expected_set
        
        result = {
            'valid': len(missing) == 0,
            'missing_columns': list(missing),
            'extra_columns': list(extra),
            'actual_columns': list(actual_columns)
        }
        
        if missing:
            logger.warning(f"Missing expected columns: {missing}")
        if extra:
            logger.info(f"Extra columns found: {extra}")
        
        self.validation_results['columns'] = result
        return result
    
    def validate_data_types(self, type_mapping: Dict[str, str]) -> Dict[str, Any]:
        mismatches = {}
        
        for col, expected_type in type_mapping.items():
            if col in self.df.columns:
                actual_type = str(self.df[col].dtype)
                if expected_type not in actual_type:
                    mismatches[col] = {
                        'expected': expected_type,
                        'actual': actual_type
                    }
        
        result = {
            'valid': len(mismatches) == 0,
            'mismatches': mismatches
        }
        
        if mismatches:
            logger.warning(f"Data type mismatches: {mismatches}")
        
        self.validation_results['data_types'] = result
        return result
    
    def check_missing_values(self) -> Dict[str, Any]:
        missing_counts = self.df.isnull().sum()
        missing_percentage = (missing_counts / len(self.df)) * 100
        
        columns_with_missing = missing_counts[missing_counts > 0]
        
        result = {
            'total_missing': int(missing_counts.sum()),
            'columns_with_missing': {
                col: {
                    'count': int(count),
                    'percentage': float(missing_percentage[col])
                }
                for col, count in columns_with_missing.items()
            }
        }
        
        if result['total_missing'] > 0:
            logger.info(f"Found {result['total_missing']} missing values across {len(columns_with_missing)} columns")
        
        self.validation_results['missing_values'] = result
        return result
    
    def check_duplicates(self) -> Dict[str, Any]:
        duplicate_count = self.df.duplicated().sum()
        
        result = {
            'has_duplicates': duplicate_count > 0,
            'count': int(duplicate_count),
            'percentage': float((duplicate_count / len(self.df)) * 100)
        }
        
        if duplicate_count > 0:
            logger.warning(f"Found {duplicate_count} duplicate rows ({result['percentage']:.2f}%)")
        
        self.validation_results['duplicates'] = result
        return result
    
    def validate_ranges(self, range_mapping: Dict[str, tuple]) -> Dict[str, Any]:
        out_of_range = {}
        
        for col, (min_val, max_val) in range_mapping.items():
            if col in self.df.columns:
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    below_min = (self.df[col] < min_val).sum()
                    above_max = (self.df[col] > max_val).sum()
                    
                    if below_min > 0 or above_max > 0:
                        out_of_range[col] = {
                            'below_min': int(below_min),
                            'above_max': int(above_max),
                            'range': (min_val, max_val)
                        }
        
        result = {
            'valid': len(out_of_range) == 0,
            'out_of_range': out_of_range
        }
        
        if out_of_range:
            logger.warning(f"Values out of range: {out_of_range}")
        
        self.validation_results['ranges'] = result
        return result
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            'shape': self.df.shape,
            'validation_results': self.validation_results
        }
    
    def run_all_validations(
        self,
        expected_columns: Optional[List[str]] = None,
        type_mapping: Optional[Dict[str, str]] = None,
        range_mapping: Optional[Dict[str, tuple]] = None
    ) -> Dict[str, Any]:
        
        if expected_columns:
            self.validate_columns(expected_columns)
        
        if type_mapping:
            self.validate_data_types(type_mapping)
        
        self.check_missing_values()
        self.check_duplicates()
        
        if range_mapping:
            self.validate_ranges(range_mapping)
        
        return self.get_summary()
