import pandas as pd
from typing import List, Dict, Any, Optional
from .constant import (
    PROGRAMMING_LANGUAGES, CLOUD_PLATFORMS, ML_FRAMEWORKS,
    US_STATES, EXPERIENCE_LEVELS
)


def parse_list_column(series: pd.Series, delimiter: str = ',') -> pd.Series:
    return series.str.split(delimiter).apply(lambda x: [s.strip() for s in x] if isinstance(x, list) else [])


def create_binary_features(
    df: pd.DataFrame,
    source_column: str,
    feature_list: List[str],
    prefix: str = '',
    case_sensitive: bool = False
) -> pd.DataFrame:
    df_copy = df.copy()
    
    for item in feature_list:
        col_name = f"{prefix}{item.replace(' ', '_').replace('+', 'plus').replace('#', 'sharp').lower()}"
        df_copy[col_name] = df[source_column].str.contains(
            item, case=case_sensitive, na=False
        ).astype(int)
    
    return df_copy


def check_contains_any(text: str, items: List[str]) -> bool:
    if pd.isna(text):
        return False
    return any(item in text for item in items)


def get_top_items(series: pd.Series, n: int = 20, delimiter: str = ',') -> List[str]:
    all_items = []
    for item_str in series.dropna():
        items = [s.strip() for s in item_str.split(delimiter)]
        all_items.extend(items)
    
    return pd.Series(all_items).value_counts().head(n).index.tolist()


def safe_divide(numerator: pd.Series, denominator: pd.Series, fill_value: float = 0.0) -> pd.Series:
    result = numerator / denominator
    result = result.replace([float('inf'), float('-inf')], fill_value)
    return result.fillna(fill_value)


def create_aggregated_features(
    df: pd.DataFrame,
    group_by: List[str],
    agg_config: Dict[str, List[str]]
) -> pd.DataFrame:
    return df.groupby(group_by).agg(agg_config).reset_index()


def map_experience_to_ordinal(experience_series: pd.Series) -> pd.Series:
    return experience_series.map(EXPERIENCE_LEVELS)


def identify_region(state: str) -> str:
    if pd.isna(state):
        return 'Unknown'
    return 'USA' if state in US_STATES else 'International'


def extract_date_features(date_series: pd.Series, reference_date: Optional[pd.Timestamp] = None) -> pd.DataFrame:
    date_features = pd.DataFrame()
    
    date_features['year'] = date_series.dt.year
    date_features['month'] = date_series.dt.month
    date_features['quarter'] = date_series.dt.quarter
    date_features['day_of_week'] = date_series.dt.dayofweek
    date_features['week_of_year'] = date_series.dt.isocalendar().week
    date_features['is_weekend'] = date_features['day_of_week'].isin([5, 6]).astype(int)
    
    if reference_date is not None:
        date_features['days_since'] = (reference_date - date_series).dt.days
    
    return date_features


def clean_column_name(name: str) -> str:
    return name.strip().lower().replace(' ', '_').replace('-', '_').replace('.', '_')


def get_numeric_summary(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    cols = columns if columns else df.select_dtypes(include=['number']).columns
    return df[cols].describe()


def get_categorical_summary(df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Any]:
    cols = columns if columns else df.select_dtypes(include=['object']).columns
    summary = {}
    
    for col in cols:
        summary[col] = {
            'unique_count': df[col].nunique(),
            'top_values': df[col].value_counts().head(10).to_dict(),
            'missing_count': df[col].isnull().sum()
        }
    
    return summary
