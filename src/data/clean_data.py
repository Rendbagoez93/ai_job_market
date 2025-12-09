import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from utils.config_loader import get_config_loader
from utils.file_handler import FileHandler
from utils.data_cleaner import DataCleaner
from utils.data_validator import DataValidator
from utils.logger import get_logger


logger = get_logger(__name__)


class DataCleaningPipeline:
    
    def __init__(self):
        self.config = get_config_loader()
        self.file_handler = FileHandler()
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        paths_config = self.config.load('paths')
        cleaning_config = paths_config['data_processing']['cleaning']
        
        logger.info(f"Starting data cleaning process")
        print(f"\nOriginal dataset shape: {df.shape}")
        
        cleaner = DataCleaner(df)
        
        if cleaning_config['remove_duplicates']:
            cleaner.remove_duplicates()
        
        if cleaning_config['handle_missing_values']:
            strategy = cleaning_config['missing_strategy']
            fill_value = cleaning_config.get('fill_value')
            cleaner.handle_missing_values(strategy=strategy, fill_value=fill_value)
        
        df_cleaned = cleaner.get_cleaned_data()
        report = cleaner.get_report()
        
        print(f"\nCleaned dataset shape: {df_cleaned.shape}")
        print(f"Total rows removed: {report['total_rows_removed']}")
        
        print("\nFirst 5 rows of cleaned data:")
        print(df_cleaned.head())
        print("\nLast 5 rows of cleaned data:")
        print(df_cleaned.tail())
        
        validator = DataValidator(df_cleaned)
        missing_info = validator.check_missing_values()
        duplicate_info = validator.check_duplicates()
        
        print(f"\nMissing values after cleaning: {missing_info['total_missing']}")
        print(f"Duplicates after cleaning: {duplicate_info['count']}")
        
        logger.info(f"Data cleaning completed: {report}")
        return df_cleaned
    
    def save_cleaned_data(self, df: pd.DataFrame) -> None:
        cleaned_path = self.config.get_path('paths.cleaned_data_file')
        self.file_handler.save_csv(df, cleaned_path)
        print(f"\nCleaned data saved to: {cleaned_path}")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    pipeline = DataCleaningPipeline()
    return pipeline.clean_data(df)


def save_cleaned_data(df: pd.DataFrame) -> None:
    pipeline = DataCleaningPipeline()
    pipeline.save_cleaned_data(df)


if __name__ == "__main__":
    from load_data import load_raw_data
    
    df_raw = load_raw_data()
    df_cleaned = clean_data(df_raw)
    save_cleaned_data(df_cleaned)
    