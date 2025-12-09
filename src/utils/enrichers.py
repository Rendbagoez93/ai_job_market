import pandas as pd
from typing import Tuple
from datetime import datetime
from .logger import get_logger
from .constant import (
    PROGRAMMING_LANGUAGES, CLOUD_PLATFORMS, ML_FRAMEWORKS,
    SALARY_BINS, SALARY_LABELS, AGE_BINS, AGE_LABELS,
)
from .helpers import (
    get_top_items, create_binary_features, check_contains_any,
    map_experience_to_ordinal, identify_region, extract_date_features
)


logger = get_logger(__name__)


class SalaryEnricher:
    
    def __init__(self, df: pd.DataFrame, salary_column: str = 'salary_range_usd'):
        self.df = df.copy()
        self.salary_column = salary_column
    
    def parse_salary_range(self) -> pd.DataFrame:
        self.df['salary_min'] = self.df[self.salary_column].str.split('-').str[0].astype(int)
        self.df['salary_max'] = self.df[self.salary_column].str.split('-').str[1].astype(int)
        self.df['salary_avg'] = (self.df['salary_min'] + self.df['salary_max']) / 2
        
        logger.info("Parsed salary ranges into min, max, and avg")
        return self.df
    
    def create_salary_clusters(self) -> pd.DataFrame:
        self.df['salary_cluster'] = pd.cut(
            self.df['salary_avg'],
            bins=SALARY_BINS,
            labels=SALARY_LABELS
        )
        
        logger.info(f"Created salary clusters with {len(SALARY_LABELS)} categories")
        return self.df
    
    def enrich(self) -> pd.DataFrame:
        self.parse_salary_range()
        self.create_salary_clusters()
        return self.df


class SkillsEnricher:
    
    def __init__(
        self,
        df: pd.DataFrame,
        skills_column: str = 'skills_required',
        top_n: int = 20
    ):
        self.df = df.copy()
        self.skills_column = skills_column
        self.top_n = top_n
        self.skill_counts = None
    
    def parse_skills(self) -> Tuple[pd.DataFrame, pd.Series]:
        top_skills = get_top_items(self.df[self.skills_column], n=self.top_n)
        
        self.df = create_binary_features(
            self.df,
            self.skills_column,
            top_skills,
            prefix='skill_'
        )
        
        self.df['skills_count'] = self.df[self.skills_column].str.split(',').str.len()
        
        all_skills = []
        for skills_str in self.df[self.skills_column]:
            skills = [s.strip() for s in skills_str.split(',')]
            all_skills.extend(skills)
        
        self.skill_counts = pd.Series(all_skills).value_counts()
        
        logger.info(f"Parsed {len(top_skills)} top skills as binary features")
        return self.df, self.skill_counts
    
    def create_category_flags(self) -> pd.DataFrame:
        self.df['has_programming_lang'] = self.df[self.skills_column].apply(
            lambda x: check_contains_any(x, PROGRAMMING_LANGUAGES)
        ).astype(int)
        
        self.df['has_cloud_platform'] = self.df[self.skills_column].apply(
            lambda x: check_contains_any(x, CLOUD_PLATFORMS)
        ).astype(int)
        
        self.df['has_ml_framework'] = self.df[self.skills_column].apply(
            lambda x: check_contains_any(x, ML_FRAMEWORKS)
        ).astype(int)
        
        logger.info("Created skill category flags")
        return self.df
    
    def enrich(self) -> Tuple[pd.DataFrame, pd.Series]:
        self.parse_skills()
        self.create_category_flags()
        return self.df, self.skill_counts


class ToolsEnricher:
    
    def __init__(
        self,
        df: pd.DataFrame,
        tools_column: str = 'tools_preferred',
        top_n: int = 15
    ):
        self.df = df.copy()
        self.tools_column = tools_column
        self.top_n = top_n
        self.tool_counts = None
    
    def parse_tools(self) -> Tuple[pd.DataFrame, pd.Series]:
        top_tools = get_top_items(self.df[self.tools_column], n=self.top_n)
        
        self.df = create_binary_features(
            self.df,
            self.tools_column,
            top_tools,
            prefix='tool_'
        )
        
        self.df['tools_count'] = self.df[self.tools_column].str.split(',').str.len()
        
        all_tools = []
        for tools_str in self.df[self.tools_column]:
            tools = [t.strip() for t in tools_str.split(',')]
            all_tools.extend(tools)
        
        self.tool_counts = pd.Series(all_tools).value_counts()
        
        logger.info(f"Parsed {len(top_tools)} top tools as binary features")
        return self.df, self.tool_counts
    
    def enrich(self) -> Tuple[pd.DataFrame, pd.Series]:
        return self.parse_tools()


class ExperienceEnricher:
    
    def __init__(self, df: pd.DataFrame, experience_column: str = 'experience_level'):
        self.df = df.copy()
        self.experience_column = experience_column
    
    def create_ordinal_encoding(self) -> pd.DataFrame:
        self.df['experience_level_ordinal'] = map_experience_to_ordinal(
            self.df[self.experience_column]
        )
        
        logger.info("Created ordinal encoding for experience levels")
        return self.df
    
    def enrich(self) -> pd.DataFrame:
        return self.create_ordinal_encoding()


class LocationEnricher:
    
    def __init__(
        self,
        df: pd.DataFrame,
        location_column: str = 'location',
        top_n: int = 10
    ):
        self.df = df.copy()
        self.location_column = location_column
        self.top_n = top_n
        self.state_counts = None
    
    def parse_location(self) -> Tuple[pd.DataFrame, pd.Series]:
        self.df['location_city'] = self.df[self.location_column].str.split(',').str[0].str.strip()
        self.df['location_state'] = self.df[self.location_column].str.split(',').str[1].str.strip()
        
        self.state_counts = self.df['location_state'].value_counts()
        top_states = self.state_counts.head(self.top_n).index.tolist()
        
        self.df['location_cluster'] = self.df['location_state'].apply(
            lambda x: x if x in top_states else 'Other'
        )
        
        self.df['location_region'] = self.df['location_state'].apply(identify_region)
        
        logger.info(f"Parsed location into city, state, cluster, and region")
        return self.df, self.state_counts
    
    def enrich(self) -> Tuple[pd.DataFrame, pd.Series]:
        return self.parse_location()


class DateEnricher:
    
    def __init__(
        self,
        df: pd.DataFrame,
        date_column: str = 'posted_date',
        reference_date: datetime = None
    ):
        self.df = df.copy()
        self.date_column = date_column
        self.reference_date = reference_date or datetime.now()
    
    def parse_dates(self) -> pd.DataFrame:
        self.df['posted_date_parsed'] = pd.to_datetime(self.df[self.date_column])
        
        self.df['days_since_posted'] = (
            self.reference_date - self.df['posted_date_parsed']
        ).dt.days
        
        date_features = extract_date_features(
            self.df['posted_date_parsed'],
            self.reference_date
        )
        
        for col in date_features.columns:
            if col != 'days_since':
                self.df[f'posted_{col}'] = date_features[col]
        
        logger.info("Extracted date features")
        return self.df
    
    def create_aging_feature(self) -> pd.DataFrame:
        self.df['aging_feature'] = pd.cut(
            self.df['days_since_posted'],
            bins=AGE_BINS,
            labels=AGE_LABELS
        )
        
        logger.info("Created aging feature categories")
        return self.df
    
    def create_date_cluster(self) -> pd.DataFrame:
        self.df['date_cluster'] = self.df['posted_date_parsed'].dt.to_period('M').astype(str)
        
        logger.info("Created monthly date clusters")
        return self.df
    
    def enrich(self) -> pd.DataFrame:
        self.parse_dates()
        self.create_aging_feature()
        self.create_date_cluster()
        return self.df


class AdditionalFeaturesEnricher:
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
    
    def create_salary_features(self) -> pd.DataFrame:
        if 'salary_avg' in self.df.columns and 'skills_count' in self.df.columns:
            self.df['salary_per_skill'] = self.df['salary_avg'] / self.df['skills_count']
        
        return self.df
    
    def create_employment_flags(self) -> pd.DataFrame:
        if 'employment_type' in self.df.columns:
            self.df['is_remote'] = (self.df['employment_type'] == 'Remote').astype(int)
            self.df['is_fulltime'] = (self.df['employment_type'] == 'Full-time').astype(int)
            self.df['is_contract'] = (self.df['employment_type'] == 'Contract').astype(int)
            self.df['is_internship'] = (self.df['employment_type'] == 'Internship').astype(int)
        
        return self.df
    
    def create_industry_flags(self) -> pd.DataFrame:
        if 'industry' in self.df.columns:
            self.df['is_tech_industry'] = (self.df['industry'] == 'Tech').astype(int)
            self.df['is_finance_industry'] = (self.df['industry'] == 'Finance').astype(int)
            self.df['is_healthcare_industry'] = (self.df['industry'] == 'Healthcare').astype(int)
        
        return self.df
    
    def create_company_flags(self) -> pd.DataFrame:
        if 'company_size' in self.df.columns:
            self.df['is_large_company'] = (self.df['company_size'] == 'Large').astype(int)
            self.df['is_startup'] = (self.df['company_size'] == 'Startup').astype(int)
        
        return self.df
    
    def enrich(self) -> pd.DataFrame:
        self.create_salary_features()
        self.create_employment_flags()
        self.create_industry_flags()
        self.create_company_flags()
        
        logger.info("Created additional derived features")
        return self.df
