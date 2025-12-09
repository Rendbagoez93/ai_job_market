"""Enumerations for analysis categories and types."""

from enum import Enum
from typing import List


class AnalysisType(Enum):
    """Types of analysis operations."""
    SKILL_PREMIUM = "skill_premium"
    TECH_STACK_ROI = "tech_stack_roi"
    EXPERIENCE_IMPACT = "experience_impact"
    GEOGRAPHIC_GAP = "geographic_gap"
    SALARY_PER_SKILL = "salary_per_skill"
    INDUSTRY_COMPARISON = "industry_comparison"
    COMPANY_SIZE_IMPACT = "company_size_impact"
    SKILL_COMBINATION = "skill_combination"


class SalaryMetric(Enum):
    """Salary metrics for analysis."""
    AVERAGE = "salary_avg"
    MINIMUM = "salary_min"
    MAXIMUM = "salary_max"
    MEDIAN = "salary_median"
    PER_SKILL = "salary_per_skill"


class GroupingDimension(Enum):
    """Dimensions for grouping analysis."""
    SKILL = "skill"
    EXPERIENCE_LEVEL = "experience_level"
    INDUSTRY = "industry"
    LOCATION_REGION = "location_region"
    LOCATION_STATE = "location_state"
    COMPANY_SIZE = "company_size"
    JOB_TITLE = "job_title"
    EMPLOYMENT_TYPE = "employment_type"


class SkillCategory(Enum):
    """Categories of skills."""
    PROGRAMMING_LANGUAGE = "programming_language"
    CLOUD_PLATFORM = "cloud_platform"
    ML_FRAMEWORK = "ml_framework"
    DATA_TOOL = "data_tool"
    ALL = "all"


class ComparisonType(Enum):
    """Types of comparisons."""
    USA_VS_INTERNATIONAL = "usa_vs_international"
    REMOTE_VS_ONSITE = "remote_vs_onsite"
    STARTUP_VS_LARGE = "startup_vs_large"
    TECH_VS_NON_TECH = "tech_vs_non_tech"
    ENTRY_VS_SENIOR = "entry_vs_senior"


def get_skill_columns() -> List[str]:
    """Get all skill column names."""
    return [
        'skill_tensorflow', 'skill_excel', 'skill_pandas', 'skill_fastapi',
        'skill_numpy', 'skill_reinforcement_learning', 'skill_azure', 'skill_sql',
        'skill_hugging_face', 'skill_keras', 'skill_power_bi', 'skill_aws',
        'skill_gcp', 'skill_python', 'skill_langchain', 'skill_pytorch',
        'skill_scikit-learn', 'skill_flask', 'skill_cuda', 'skill_r'
    ]


def get_tool_columns() -> List[str]:
    """Get all tool column names."""
    return [
        'tool_mlflow', 'tool_langchain', 'tool_fastapi', 'tool_kdbplus',
        'tool_bigquery', 'tool_tensorflow', 'tool_pytorch', 'tool_scikit-learn'
    ]


def get_cloud_platforms() -> List[str]:
    """Get cloud platform skill columns."""
    return ['skill_aws', 'skill_azure', 'skill_gcp']


def get_ml_frameworks() -> List[str]:
    """Get ML framework skill columns."""
    return [
        'skill_tensorflow', 'skill_pytorch', 'skill_keras', 
        'skill_scikit-learn', 'skill_hugging_face'
    ]


def get_programming_languages() -> List[str]:
    """Get programming language skill columns."""
    return ['skill_python', 'skill_r', 'skill_cuda']
