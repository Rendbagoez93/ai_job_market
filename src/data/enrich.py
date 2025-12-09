import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from datetime import datetime
from typing import Dict
from utils.config_loader import get_config_loader
from utils.file_handler import FileHandler
from utils.logger import get_logger
from utils.constant import COMMON_COLUMNS
from utils.enrichers import (
    SalaryEnricher, SkillsEnricher, ToolsEnricher,
    ExperienceEnricher, LocationEnricher, DateEnricher,
    AdditionalFeaturesEnricher
)


logger = get_logger(__name__)


class DataEnrichmentPipeline:
    
    def __init__(self):
        self.config = get_config_loader()
        self.file_handler = FileHandler()
        self.enrichment_metadata = {}
    
    def load_cleaned_data(self) -> pd.DataFrame:
        cleaned_path = self.config.get_path('paths.cleaned_data_file')
        logger.info(f"Loading cleaned data from: {cleaned_path}")
        return self.file_handler.load_csv(cleaned_path)
    
    def enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Starting data enrichment pipeline")
        
        print("\n1. Parsing and clustering salary ranges...")
        salary_enricher = SalaryEnricher(df)
        df = salary_enricher.enrich()
        
        print("2. Parsing and clustering skills...")
        skills_enricher = SkillsEnricher(df)
        df, skill_counts = skills_enricher.enrich()
        self.enrichment_metadata['skill_counts'] = skill_counts
        
        print("3. Parsing and clustering tools...")
        tools_enricher = ToolsEnricher(df)
        df, tool_counts = tools_enricher.enrich()
        self.enrichment_metadata['tool_counts'] = tool_counts
        
        print("4. Converting experience level to ordinal...")
        experience_enricher = ExperienceEnricher(df)
        df = experience_enricher.enrich()
        
        print("5. Parsing and clustering location...")
        location_enricher = LocationEnricher(df)
        df, state_counts = location_enricher.enrich()
        self.enrichment_metadata['state_counts'] = state_counts
        
        print("6. Parsing posted date and creating aging feature...")
        date_enricher = DateEnricher(df, reference_date=datetime(2025, 12, 9))
        df = date_enricher.enrich()
        
        print("7. Creating additional derived features...")
        additional_enricher = AdditionalFeaturesEnricher(df)
        df = additional_enricher.enrich()
        
        logger.info(f"Enrichment completed. Final shape: {df.shape}")
        return df
    
    def save_enriched_data(self, df: pd.DataFrame) -> None:
        enriched_dir = 'data/enriched'
        self.file_handler.ensure_directory(enriched_dir)
        
        print("\n8. Saving enriched data by category...")
        
        category_configs = self._get_category_configs(df)
        
        for category, columns in category_configs.items():
            df_category = df[columns]
            filepath = f"{enriched_dir}/{category}_enriched.csv"
            self.file_handler.save_csv(df_category, filepath)
            print(f"  - {category}_enriched.csv ({len(columns)} columns)")
        
        self._save_data_dictionaries()
        
        logger.info("All enriched data files saved successfully")
    
    def _get_category_configs(self, df: pd.DataFrame) -> Dict[str, list]:
        return {
            'salary': COMMON_COLUMNS + [
                'salary_range_usd', 'salary_min', 'salary_max', 'salary_avg',
                'salary_cluster', 'salary_per_skill'
            ],
            'skills': COMMON_COLUMNS + ['skills_required', 'skills_count',
                                        'has_programming_lang', 'has_cloud_platform', 
                                        'has_ml_framework'] + 
                      [col for col in df.columns if col.startswith('skill_')],
            'tools': COMMON_COLUMNS + ['tools_preferred', 'tools_count'] +
                     [col for col in df.columns if col.startswith('tool_')],
            'experience': COMMON_COLUMNS + ['experience_level', 'experience_level_ordinal'],
            'location': COMMON_COLUMNS + [
                'location', 'location_city', 'location_state',
                'location_cluster', 'location_region'
            ],
            'date': COMMON_COLUMNS + [
                'posted_date', 'posted_date_parsed', 'days_since_posted',
                'posted_year', 'posted_month', 'posted_quarter',
                'posted_day_of_week', 'posted_week_of_year',
                'aging_feature', 'date_cluster'
            ],
            'employment': COMMON_COLUMNS + [
                'employment_type', 'is_remote', 'is_fulltime',
                'is_contract', 'is_internship'
            ],
            'company': COMMON_COLUMNS + [
                'company_size', 'is_large_company', 'is_startup',
                'is_tech_industry', 'is_finance_industry', 'is_healthcare_industry'
            ]
        }
    
    def _save_data_dictionaries(self) -> None:
        dictionary_dir = 'data/dictionary'
        self.file_handler.ensure_directory(dictionary_dir)
        
        if 'skill_counts' in self.enrichment_metadata:
            self.enrichment_metadata['skill_counts'].to_csv(
                f'{dictionary_dir}/skill_frequency.csv',
                header=['count']
            )
        
        if 'tool_counts' in self.enrichment_metadata:
            self.enrichment_metadata['tool_counts'].to_csv(
                f'{dictionary_dir}/tool_frequency.csv',
                header=['count']
            )
        
        if 'state_counts' in self.enrichment_metadata:
            self.enrichment_metadata['state_counts'].to_csv(
                f'{dictionary_dir}/location_frequency.csv',
                header=['count']
            )
        
        from utils.constant import EXPERIENCE_LEVELS, SALARY_LABELS, AGE_LABELS
        
        mapping_data = {
            'experience_level_mapping': EXPERIENCE_LEVELS,
            'salary_clusters': SALARY_LABELS,
            'aging_categories': AGE_LABELS,
            'location_region': ['USA', 'International']
        }
        
        self.file_handler.save_json(
            mapping_data,
            f'{dictionary_dir}/column_mapping.json'
        )
        
        print(f"\nData dictionaries saved to: {dictionary_dir}")
    
    def print_summary(self, df: pd.DataFrame) -> None:
        print("\n" + "="*60)
        print("ENRICHMENT SUMMARY")
        print("="*60)
        
        skill_features = len([c for c in df.columns if c.startswith('skill_')])
        tool_features = len([c for c in df.columns if c.startswith('tool_')])
        
        print(f"✓ Salary Features: min, max, avg, cluster, per_skill")
        print(f"✓ Skills Features: {df['skills_count'].max()} max skills, {skill_features} binary features")
        print(f"✓ Tools Features: {df['tools_count'].max()} max tools, {tool_features} binary features")
        print(f"✓ Experience: Ordinal encoding (Entry=1, Mid=2, Senior=3)")
        print(f"✓ Location: City, state, cluster, region (USA/International)")
        print(f"✓ Date Features: Year, month, quarter, day_of_week, week, aging")
        print(f"✓ Employment: Type flags (remote, fulltime, contract, internship)")
        print(f"✓ Company: Size and industry flags")
        print("="*60)


def main():
    pipeline = DataEnrichmentPipeline()
    
    print("Loading cleaned data...")
    df = pipeline.load_cleaned_data()
    print(f"Original shape: {df.shape}")
    
    df_enriched = pipeline.enrich_data(df)
    pipeline.save_enriched_data(df_enriched)
    pipeline.print_summary(df_enriched)
    
    return df_enriched


if __name__ == "__main__":
    df_enriched = main()

