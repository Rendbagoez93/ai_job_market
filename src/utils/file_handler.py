import pandas as pd
import json
import os
from pathlib import Path
from typing import Union, Dict, Any, Optional
from .logger import get_logger


logger = get_logger(__name__)


class FileHandler:
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> None:
        path = Path(path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {path}")
    
    @staticmethod
    def load_csv(
        filepath: Union[str, Path],
        encoding: str = 'utf-8',
        delimiter: str = ',',
        skiprows: int = 0,
        **kwargs
    ) -> pd.DataFrame:
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        try:
            df = pd.read_csv(
                filepath,
                encoding=encoding,
                delimiter=delimiter,
                skiprows=skiprows,
                **kwargs
            )
            logger.info(f"Loaded CSV: {filepath} with shape {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV {filepath}: {e}")
            raise
    
    @staticmethod
    def save_csv(
        df: pd.DataFrame,
        filepath: Union[str, Path],
        index: bool = False,
        **kwargs
    ) -> None:
        filepath = Path(filepath)
        FileHandler.ensure_directory(filepath.parent)
        
        try:
            df.to_csv(filepath, index=index, **kwargs)
            logger.info(f"Saved CSV: {filepath} with shape {df.shape}")
        except Exception as e:
            logger.error(f"Error saving CSV {filepath}: {e}")
            raise
    
    @staticmethod
    def load_json(filepath: Union[str, Path]) -> Dict[str, Any]:
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"JSON file not found: {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded JSON: {filepath}")
            return data
        except Exception as e:
            logger.error(f"Error loading JSON {filepath}: {e}")
            raise
    
    @staticmethod
    def save_json(
        data: Dict[str, Any],
        filepath: Union[str, Path],
        indent: int = 2
    ) -> None:
        filepath = Path(filepath)
        FileHandler.ensure_directory(filepath.parent)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=indent)
            logger.info(f"Saved JSON: {filepath}")
        except Exception as e:
            logger.error(f"Error saving JSON {filepath}: {e}")
            raise
