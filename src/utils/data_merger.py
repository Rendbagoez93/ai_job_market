"""Utility for merging enriched datasets."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from typing import List, Optional, Dict
from utils.file_handler import FileHandler
from utils.logger import get_logger


logger = get_logger(__name__)


class DataMerger:
    """Merge enriched datasets into master dataset."""
    
    def __init__(self):
        self.file_handler = FileHandler()
        self.enriched_dir = Path('data/enriched')
    
    def load_enriched_dataset(self, category: str) -> pd.DataFrame:
        """Load a specific enriched dataset.
        
        Args:
            category: Category name (e.g., 'salary', 'skills', 'tools')
        
        Returns:
            DataFrame with enriched data
        """
        filepath = self.enriched_dir / f"{category}_enriched.csv"
        logger.info(f"Loading {category} enriched data from {filepath}")
        return self.file_handler.load_csv(filepath)
    
    def merge_datasets(
        self, 
        categories: Optional[List[str]] = None,
        on: str = 'job_id',
        how: str = 'inner'
    ) -> pd.DataFrame:
        """Merge multiple enriched datasets.
        
        Args:
            categories: List of categories to merge. If None, merges all.
            on: Column to merge on (default: 'job_id')
            how: Type of merge (default: 'inner')
        
        Returns:
            Merged DataFrame
        """
        if categories is None:
            categories = [
                'salary', 'skills', 'tools', 'location', 
                'date', 'experience', 'employment', 'company'
            ]
        
        logger.info(f"Merging {len(categories)} datasets: {categories}")
        
        # Load first dataset
        master_df = self.load_enriched_dataset(categories[0])
        logger.info(f"Base dataset shape: {master_df.shape}")
        
        # Merge remaining datasets
        for category in categories[1:]:
            df = self.load_enriched_dataset(category)
            
            # Get columns to merge (excluding common columns already in master)
            common_cols = ['job_id', 'company_name', 'industry', 'job_title']
            cols_to_keep = [col for col in df.columns if col not in master_df.columns or col == on]
            df_to_merge = df[cols_to_keep]
            
            master_df = master_df.merge(df_to_merge, on=on, how=how)
            logger.info(f"After merging {category}: {master_df.shape}")
        
        logger.info(f"Final merged dataset shape: {master_df.shape}")
        logger.info(f"Total columns: {len(master_df.columns)}")
        
        return master_df
    
    def create_analysis_dataset(
        self,
        categories: List[str],
        filters: Optional[Dict] = None
    ) -> pd.DataFrame:
        """Create a filtered dataset for specific analysis.
        
        Args:
            categories: List of categories to include
            filters: Dictionary of filters to apply
        
        Returns:
            Filtered DataFrame ready for analysis
        """
        df = self.merge_datasets(categories)
        
        if filters:
            for column, value in filters.items():
                if isinstance(value, list):
                    df = df[df[column].isin(value)]
                else:
                    df = df[df[column] == value]
                logger.info(f"Applied filter {column}={value}, remaining rows: {len(df)}")
        
        return df
    
    def save_master_dataset(self, df: pd.DataFrame, filepath: str = 'data/master_dataset.csv') -> None:
        """Save merged master dataset.
        
        Args:
            df: DataFrame to save
            filepath: Path to save file
        """
        self.file_handler.save_csv(df, filepath)
        logger.info(f"Master dataset saved to {filepath}")


def create_master_dataset(save: bool = True) -> pd.DataFrame:
    """Convenience function to create master dataset.
    
    Args:
        save: Whether to save the master dataset
    
    Returns:
        Master DataFrame
    """
    merger = DataMerger()
    master_df = merger.merge_datasets()
    
    if save:
        merger.save_master_dataset(master_df)
    
    return master_df


if __name__ == "__main__":
    df = create_master_dataset(save=True)
    print(f"\nMaster dataset created successfully!")
    print(f"Shape: {df.shape}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head())
