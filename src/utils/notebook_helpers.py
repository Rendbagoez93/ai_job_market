"""
Notebook Helper Utilities

Centralized data loading and utility functions for Jupyter notebooks.
Eliminates code duplication across cleaning.ipynb, exploration.ipynb, and salary_intelligence_analysis.ipynb.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import warnings


class NotebookDataLoader:
    """
    Centralized data loader for notebooks with Kaggle and local environment support.
    
    Features:
    - Auto-detects Kaggle vs local environment
    - Configurable data paths
    - Supports raw, cleaned, and enriched datasets
    - Validation and error handling
    - Merge multiple enriched datasets
    """
    
    def __init__(self, kaggle_dataset_name: str = 'ai-job-market-insights'):
        """
        Initialize the data loader.
        
        Args:
            kaggle_dataset_name: Name of the Kaggle dataset
        """
        self.is_kaggle = os.path.exists('/kaggle/input')
        self.kaggle_dataset_name = kaggle_dataset_name
        
        # Configure paths based on environment
        if self.is_kaggle:
            self.base_path = Path('/kaggle/input') / kaggle_dataset_name
        else:
            self.base_path = Path('..') / 'data'
        
        self.raw_path = self.base_path if self.is_kaggle else self.base_path / 'raw'
        self.cleaned_path = self.base_path if self.is_kaggle else self.base_path / 'cleaned'
        self.enriched_path = self.base_path if self.is_kaggle else self.base_path / 'enriched'
    
    def get_environment(self) -> Dict[str, Union[str, Path]]:
        """Get current environment information."""
        return {
            'environment': 'Kaggle' if self.is_kaggle else 'Local',
            'base_path': self.base_path,
            'raw_path': self.raw_path,
            'cleaned_path': self.cleaned_path,
            'enriched_path': self.enriched_path
        }
    
    def load_raw_data(self, filename: str = 'ai_job_market.csv', **kwargs) -> pd.DataFrame:
        """
        Load raw data from Kaggle or local filesystem.
        
        Args:
            filename: Name of the raw data file
            **kwargs: Additional arguments for pd.read_csv()
            
        Returns:
            DataFrame with raw data
            
        Raises:
            FileNotFoundError: If data file not found
        """
        file_path = self.raw_path / filename
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"Raw data file not found: {file_path}\n"
                f"Expected location: {file_path}\n"
                f"Please ensure the dataset is available."
            )
        
        print(f"📊 Loading raw data from: {file_path}")
        df = pd.read_csv(file_path, **kwargs)
        print(f"✓ Loaded {len(df):,} rows × {len(df.columns)} columns")
        
        return df
    
    def load_cleaned_data(self, filename: str = 'ai_job_market_cleaned.csv', **kwargs) -> pd.DataFrame:
        """
        Load cleaned data.
        
        Args:
            filename: Name of the cleaned data file
            **kwargs: Additional arguments for pd.read_csv()
            
        Returns:
            DataFrame with cleaned data
            
        Raises:
            FileNotFoundError: If cleaned data not found
        """
        file_path = self.cleaned_path / filename
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"Cleaned data file not found: {file_path}\n"
                f"Please run 'cleaning.ipynb' first to generate cleaned data."
            )
        
        print(f"📊 Loading cleaned data from: {file_path}")
        df = pd.read_csv(file_path, **kwargs)
        print(f"✓ Loaded {len(df):,} rows × {len(df.columns)} columns")
        
        return df
    
    def load_enriched_data(
        self,
        files: Optional[List[str]] = None,
        merge_on: str = 'job_id',
        validate: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load and merge multiple enriched datasets.
        
        Args:
            files: List of enriched file names. If None, loads all standard enriched files.
            merge_on: Column to merge on (default: 'job_id')
            validate: Whether to validate files exist before loading
            **kwargs: Additional arguments for pd.read_csv()
            
        Returns:
            DataFrame with merged enriched data
            
        Raises:
            FileNotFoundError: If critical files are missing
        """
        # Default enriched files
        if files is None:
            files = [
                'salary_enriched.csv',
                'skills_enriched.csv',
                'tools_enriched.csv',
                'location_enriched.csv',
                'experience_enriched.csv',
                'employment_enriched.csv',
                'company_enriched.csv',
                'date_enriched.csv'
            ]
        
        # Validate files exist
        if validate:
            missing_files = [f for f in files if not (self.enriched_path / f).exists()]
            if missing_files:
                raise FileNotFoundError(
                    f"Missing enriched files: {missing_files}\n"
                    f"Expected path: {self.enriched_path}/\n"
                    f"Please run 'cleaning.ipynb' first to generate enriched datasets."
                )
        
        # Filter to only existing files
        available_files = [f for f in files if (self.enriched_path / f).exists()]
        
        if not available_files:
            raise FileNotFoundError(f"No enriched files found in {self.enriched_path}")
        
        print(f"📊 Loading {len(available_files)} enriched datasets from: {self.enriched_path}")
        
        # Load base file (typically salary_enriched.csv)
        base_file = available_files[0]
        df = pd.read_csv(self.enriched_path / base_file, **kwargs)
        print(f"  ✓ Base: {base_file:<30} ({len(df):,} rows)")
        
        # Merge other files
        for file in available_files[1:]:
            temp_df = pd.read_csv(self.enriched_path / file, **kwargs)
            original_cols = len(df.columns)
            
            # Merge with left join
            df = df.merge(temp_df, on=merge_on, how='left', suffixes=('', '_drop'))
            
            # Drop duplicate columns
            df = df.loc[:, ~df.columns.str.endswith('_drop')]
            
            new_cols = len(df.columns) - original_cols
            print(f"  ✓ Merged: {file:<28} (+{new_cols:>2} features)")
        
        print(f"\n✅ Successfully loaded {len(df):,} records with {df.shape[1]} features")
        
        return df
    
    def load_data_auto(
        self,
        prefer: str = 'cleaned',
        fallback: bool = True,
        **kwargs
    ) -> Tuple[pd.DataFrame, str]:
        """
        Automatically load data with intelligent fallback.
        
        Args:
            prefer: Preferred data type ('raw', 'cleaned', or 'enriched')
            fallback: Whether to fallback to other data types if preferred not found
            **kwargs: Additional arguments for pd.read_csv()
            
        Returns:
            Tuple of (DataFrame, data_type_loaded)
            
        Raises:
            FileNotFoundError: If no data can be loaded
        """
        load_order = {
            'enriched': ['enriched', 'cleaned', 'raw'],
            'cleaned': ['cleaned', 'raw'],
            'raw': ['raw']
        }
        
        order = load_order.get(prefer, ['cleaned', 'raw'])
        
        if not fallback:
            order = [prefer]
        
        for data_type in order:
            try:
                if data_type == 'enriched':
                    df = self.load_enriched_data(validate=False, **kwargs)
                    return df, 'enriched'
                elif data_type == 'cleaned':
                    df = self.load_cleaned_data(**kwargs)
                    return df, 'cleaned'
                elif data_type == 'raw':
                    df = self.load_raw_data(**kwargs)
                    return df, 'raw'
            except FileNotFoundError:
                continue
        
        raise FileNotFoundError(
            "No data found in any location. Please check your data directory structure."
        )


class CheckpointManager:
    """
    Manages checkpoints for long-running notebook processes.
    
    Features:
    - Save/load intermediate results
    - Resume from last checkpoint
    - Clear checkpoints
    - Progress tracking
    """
    
    def __init__(self, checkpoint_dir: Union[str, Path] = '../data/checkpoints'):
        """
        Initialize checkpoint manager.
        
        Args:
            checkpoint_dir: Directory to store checkpoint files
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def save_checkpoint(
        self,
        data: pd.DataFrame,
        checkpoint_name: str,
        metadata: Optional[Dict] = None
    ) -> Path:
        """
        Save a checkpoint.
        
        Args:
            data: DataFrame to save
            checkpoint_name: Name for the checkpoint
            metadata: Optional metadata to save with checkpoint
            
        Returns:
            Path to saved checkpoint file
        """
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_name}.pkl"
        
        # Save data
        data.to_pickle(checkpoint_file)
        
        # Save metadata if provided
        if metadata:
            import json
            metadata_file = self.checkpoint_dir / f"{checkpoint_name}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
        
        file_size = checkpoint_file.stat().st_size / (1024 * 1024)
        print(f"💾 Checkpoint saved: {checkpoint_name} ({file_size:.2f} MB)")
        
        return checkpoint_file
    
    def load_checkpoint(
        self,
        checkpoint_name: str,
        load_metadata: bool = False
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, Dict]]:
        """
        Load a checkpoint.
        
        Args:
            checkpoint_name: Name of the checkpoint to load
            load_metadata: Whether to also load metadata
            
        Returns:
            DataFrame or tuple of (DataFrame, metadata)
            
        Raises:
            FileNotFoundError: If checkpoint doesn't exist
        """
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_name}.pkl"
        
        if not checkpoint_file.exists():
            raise FileNotFoundError(
                f"Checkpoint not found: {checkpoint_name}\n"
                f"Expected location: {checkpoint_file}"
            )
        
        # Load data
        data = pd.read_pickle(checkpoint_file)
        file_size = checkpoint_file.stat().st_size / (1024 * 1024)
        print(f"📂 Checkpoint loaded: {checkpoint_name} ({file_size:.2f} MB)")
        
        if load_metadata:
            import json
            metadata_file = self.checkpoint_dir / f"{checkpoint_name}_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                return data, metadata
            else:
                warnings.warn(f"No metadata found for checkpoint: {checkpoint_name}")
                return data, {}
        
        return data
    
    def checkpoint_exists(self, checkpoint_name: str) -> bool:
        """Check if a checkpoint exists."""
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_name}.pkl"
        return checkpoint_file.exists()
    
    def list_checkpoints(self) -> List[Dict[str, Union[str, float]]]:
        """
        List all available checkpoints.
        
        Returns:
            List of checkpoint information dictionaries
        """
        checkpoints = []
        
        for file in self.checkpoint_dir.glob("*.pkl"):
            file_size = file.stat().st_size / (1024 * 1024)
            checkpoints.append({
                'name': file.stem,
                'size_mb': round(file_size, 2),
                'path': str(file)
            })
        
        return sorted(checkpoints, key=lambda x: x['name'])
    
    def clear_checkpoint(self, checkpoint_name: str) -> bool:
        """
        Delete a specific checkpoint.
        
        Args:
            checkpoint_name: Name of checkpoint to delete
            
        Returns:
            True if deleted, False if not found
        """
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_name}.pkl"
        metadata_file = self.checkpoint_dir / f"{checkpoint_name}_metadata.json"
        
        deleted = False
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            deleted = True
            print(f"🗑️  Deleted checkpoint: {checkpoint_name}")
        
        if metadata_file.exists():
            metadata_file.unlink()
        
        return deleted
    
    def clear_all_checkpoints(self) -> int:
        """
        Clear all checkpoints.
        
        Returns:
            Number of checkpoints deleted
        """
        count = 0
        for file in self.checkpoint_dir.glob("*.pkl"):
            file.unlink()
            count += 1
        
        for file in self.checkpoint_dir.glob("*.json"):
            file.unlink()
        
        if count > 0:
            print(f"🗑️  Cleared {count} checkpoint(s)")
        
        return count


# Convenience functions for direct import
def get_data_loader(kaggle_dataset_name: str = 'ai-job-market-insights') -> NotebookDataLoader:
    """Get a configured data loader instance."""
    return NotebookDataLoader(kaggle_dataset_name)


def get_checkpoint_manager(checkpoint_dir: Union[str, Path] = '../data/checkpoints') -> CheckpointManager:
    """Get a configured checkpoint manager instance."""
    return CheckpointManager(checkpoint_dir)
