import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from utils.config_loader import get_config_loader
from utils.file_handler import FileHandler
from utils.data_validator import DataValidator
from utils.logger import get_logger


logger = get_logger(__name__)


class DataLoader:
    
    def __init__(self):
        self.config = get_config_loader()
        self.file_handler = FileHandler()
    
    def load_raw_data(self) -> pd.DataFrame:
        paths_config = self.config.load('paths')
        main_config = self.config.load('config')
        
        raw_data_path = paths_config['paths']['raw_data_file']
        loading_config = paths_config['data_processing']['loading']
        
        logger.info(f"Loading raw data from: {raw_data_path}")
        
        df = self.file_handler.load_csv(
            raw_data_path,
            encoding=loading_config['encoding'],
            delimiter=loading_config['delimiter'],
            skiprows=loading_config['skip_rows']
        )
        
        print(f"\nData loaded successfully!")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst 5 rows:")
        print(df.head())
        
        expected_columns = main_config['columns']['raw_columns']
        validator = DataValidator(df)
        validation_result = validator.validate_columns(expected_columns)
        
        if not validation_result['valid']:
            logger.warning(f"Column validation issues found")
        
        print("\nBasic statistics:")
        print(df.describe(include='all'))
        
        return df
    
    def load_cleaned_data(self) -> pd.DataFrame:
        cleaned_path = self.config.get_path('paths.cleaned_data_file')
        logger.info(f"Loading cleaned data from: {cleaned_path}")
        return self.file_handler.load_csv(cleaned_path)
    
    def load_enriched_data(self, category: str = None) -> pd.DataFrame:
        enriched_dir = 'data/enriched'
        
        if category:
            filepath = f"{enriched_dir}/{category}_enriched.csv"
        else:
            filepath = self.config.get_path('paths.enriched_data_file')
        
        logger.info(f"Loading enriched data from: {filepath}")
        return self.file_handler.load_csv(filepath)


def load_raw_data() -> pd.DataFrame:
    loader = DataLoader()
    return loader.load_raw_data()


def load_cleaned_data() -> pd.DataFrame:
    loader = DataLoader()
    return loader.load_cleaned_data()


if __name__ == "__main__":
    df = load_raw_data()