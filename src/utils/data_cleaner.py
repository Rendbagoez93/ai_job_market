import pandas as pd
from typing import Optional, List, Dict, Any
from .logger import get_logger


logger = get_logger(__name__)


class DataCleaner:
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.original_shape = df.shape
        self.cleaning_report = {
            'original_shape': self.original_shape,
            'operations': []
        }
    
    def remove_duplicates(self, subset: Optional[List[str]] = None, keep: str = 'first') -> 'DataCleaner':
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        removed = initial_rows - len(self.df)
        
        self.cleaning_report['operations'].append({
            'operation': 'remove_duplicates',
            'rows_removed': removed,
            'subset': subset,
            'keep': keep
        })
        
        logger.info(f"Removed {removed} duplicate rows")
        return self
    
    def handle_missing_values(
        self,
        strategy: str = 'drop',
        fill_value: Any = None,
        columns: Optional[List[str]] = None
    ) -> 'DataCleaner':
        missing_before = self.df.isnull().sum().sum()
        initial_rows = len(self.df)
        
        cols_to_process = columns if columns else self.df.columns.tolist()
        
        if strategy == 'drop':
            self.df = self.df.dropna(subset=cols_to_process)
        
        elif strategy == 'fill':
            for col in cols_to_process:
                if col in self.df.columns:
                    if pd.api.types.is_numeric_dtype(self.df[col]):
                        fill_val = fill_value if fill_value is not None else self.df[col].mean()
                        self.df[col] = self.df[col].fillna(fill_val)
                    else:
                        fill_val = fill_value if fill_value is not None else (
                            self.df[col].mode().iloc[0] if not self.df[col].mode().empty else 'Unknown'
                        )
                        self.df[col] = self.df[col].fillna(fill_val)
        
        elif strategy == 'interpolate':
            for col in cols_to_process:
                if col in self.df.columns and pd.api.types.is_numeric_dtype(self.df[col]):
                    self.df[col] = self.df[col].interpolate()
        
        missing_after = self.df.isnull().sum().sum()
        rows_removed = initial_rows - len(self.df)
        
        self.cleaning_report['operations'].append({
            'operation': 'handle_missing_values',
            'strategy': strategy,
            'missing_before': int(missing_before),
            'missing_after': int(missing_after),
            'rows_removed': rows_removed,
            'columns': cols_to_process
        })
        
        logger.info(f"Handled missing values with strategy '{strategy}': {missing_before} -> {missing_after}")
        return self
    
    def remove_columns(self, columns: List[str]) -> 'DataCleaner':
        existing_cols = [col for col in columns if col in self.df.columns]
        
        if existing_cols:
            self.df = self.df.drop(columns=existing_cols)
            
            self.cleaning_report['operations'].append({
                'operation': 'remove_columns',
                'columns_removed': existing_cols
            })
            
            logger.info(f"Removed columns: {existing_cols}")
        
        return self
    
    def filter_rows(self, condition: pd.Series, description: str = '') -> 'DataCleaner':
        initial_rows = len(self.df)
        self.df = self.df[condition]
        rows_removed = initial_rows - len(self.df)
        
        self.cleaning_report['operations'].append({
            'operation': 'filter_rows',
            'description': description,
            'rows_removed': rows_removed
        })
        
        logger.info(f"Filtered rows: {rows_removed} removed ({description})")
        return self
    
    def convert_data_types(self, type_mapping: Dict[str, str]) -> 'DataCleaner':
        converted = []
        
        for col, dtype in type_mapping.items():
            if col in self.df.columns:
                try:
                    self.df[col] = self.df[col].astype(dtype)
                    converted.append(col)
                except Exception as e:
                    logger.warning(f"Could not convert {col} to {dtype}: {e}")
        
        self.cleaning_report['operations'].append({
            'operation': 'convert_data_types',
            'columns_converted': converted,
            'type_mapping': type_mapping
        })
        
        logger.info(f"Converted data types for columns: {converted}")
        return self
    
    def standardize_text(
        self,
        columns: List[str],
        lowercase: bool = True,
        strip: bool = True,
        remove_extra_spaces: bool = True
    ) -> 'DataCleaner':
        
        for col in columns:
            if col in self.df.columns and self.df[col].dtype == 'object':
                if strip:
                    self.df[col] = self.df[col].str.strip()
                if lowercase:
                    self.df[col] = self.df[col].str.lower()
                if remove_extra_spaces:
                    self.df[col] = self.df[col].str.replace(r'\s+', ' ', regex=True)
        
        self.cleaning_report['operations'].append({
            'operation': 'standardize_text',
            'columns': columns,
            'lowercase': lowercase,
            'strip': strip,
            'remove_extra_spaces': remove_extra_spaces
        })
        
        logger.info(f"Standardized text in columns: {columns}")
        return self
    
    def get_cleaned_data(self) -> pd.DataFrame:
        return self.df
    
    def get_report(self) -> Dict[str, Any]:
        self.cleaning_report['final_shape'] = self.df.shape
        self.cleaning_report['total_rows_removed'] = self.original_shape[0] - self.df.shape[0]
        return self.cleaning_report
