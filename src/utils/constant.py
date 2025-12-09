from typing import List


PROGRAMMING_LANGUAGES: List[str] = [
    'Python', 'R', 'Java', 'C++', 'JavaScript', 'Julia', 
    'Scala', 'Go', 'C#', 'Ruby', 'PHP', 'Swift', 'Kotlin'
]

CLOUD_PLATFORMS: List[str] = [
    'AWS', 'Azure', 'GCP', 'Google Cloud', 'Amazon Web Services',
    'Microsoft Azure', 'IBM Cloud', 'Oracle Cloud'
]

ML_FRAMEWORKS: List[str] = [
    'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'XGBoost',
    'LightGBM', 'CatBoost', 'FastAI', 'JAX', 'MXNet'
]

DATA_TOOLS: List[str] = [
    'Pandas', 'NumPy', 'SQL', 'Spark', 'Hadoop', 'Tableau',
    'Power BI', 'Excel', 'Jupyter', 'Apache Airflow'
]

US_STATES: List[str] = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

EXPERIENCE_LEVELS: dict = {
    'Entry': 1,
    'Junior': 1,
    'Mid': 2,
    'Senior': 3,
    'Lead': 4,
    'Principal': 5
}

SALARY_BINS: List[int] = [0, 60000, 80000, 100000, 120000, 150000, 200000, float('inf')]

SALARY_LABELS: List[str] = [
    '<60K', '60-80K', '80-100K', '100-120K', 
    '120-150K', '150-200K', '200K+'
]

AGE_BINS: List[int] = [-1, 30, 90, 180, 365, float('inf')]

AGE_LABELS: List[str] = [
    'Recent (<30 days)', 
    'Fresh (30-90 days)', 
    'Active (90-180 days)',
    'Aging (180-365 days)', 
    'Old (>365 days)'
]

COMMON_COLUMNS: List[str] = ['job_id', 'company_name', 'industry', 'job_title']
