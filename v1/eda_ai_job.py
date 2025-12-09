import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Load and inspect data structure
def load_data():
    df = pd.read_csv('data/ai_job_market.csv')
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Missing values: {df.isnull().sum().sum()}")
    return df

# Parse salary ranges into numeric min, max, and midpoint
def parse_salaries(df):
    salary_parts = df['salary_range_usd'].str.extract(r'(\d+)-(\d+)')
    df['salary_min'] = salary_parts[0].astype(int)
    df['salary_max'] = salary_parts[1].astype(int) 
    df['salary_mid'] = (df['salary_min'] + df['salary_max']) / 2
    return df

# Convert posted_date to datetime for time analysis
def parse_dates(df):
    df['posted_date'] = pd.to_datetime(df['posted_date'])
    df['posted_year'] = df['posted_date'].dt.year
    df['posted_month'] = df['posted_date'].dt.month
    return df

# Extract and count individual skills from comma-separated strings
def extract_skills(df):
    all_skills = []
    for skills_str in df['skills_required'].fillna(''):
        skills = [skill.strip() for skill in skills_str.split(',') if skill.strip()]
        all_skills.extend(skills)
    
    skill_counts = Counter(all_skills)
    return skill_counts

# Extract and count preferred tools
def extract_tools(df):
    all_tools = []
    for tools_str in df['tools_preferred'].fillna(''):
        tools = [tool.strip() for tool in tools_str.split(',') if tool.strip()]
        all_tools.extend(tools)
    
    tool_counts = Counter(all_tools)
    return tool_counts

# Visualize salary distributions by key categories
def plot_salary_analysis(df):
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Salary by job title
    sns.boxplot(data=df, x='job_title', y='salary_mid', ax=axes[0,0])
    axes[0,0].set_title('Salary by Job Title')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Salary by experience level
    sns.boxplot(data=df, x='experience_level', y='salary_mid', ax=axes[0,1])
    axes[0,1].set_title('Salary by Experience Level')
    
    # Salary by industry
    sns.boxplot(data=df, x='industry', y='salary_mid', ax=axes[1,0])
    axes[1,0].set_title('Salary by Industry')
    axes[1,0].tick_params(axis='x', rotation=45)
    
    # Salary by company size
    sns.boxplot(data=df, x='company_size', y='salary_mid', ax=axes[1,1])
    axes[1,1].set_title('Salary by Company Size')
    
    plt.tight_layout()
    plt.show()

# Analyze job posting trends over time
def plot_time_trends(df):
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Posts by year
    yearly_counts = df['posted_year'].value_counts().sort_index()
    yearly_counts.plot(kind='bar', ax=axes[0])
    axes[0].set_title('Job Posts by Year')
    axes[0].set_xlabel('Year')
    
    # Posts by month
    monthly_counts = df['posted_month'].value_counts().sort_index()
    monthly_counts.plot(kind='bar', ax=axes[1])
    axes[1].set_title('Job Posts by Month')
    axes[1].set_xlabel('Month')
    
    plt.tight_layout()
    plt.show()

# Visualize top skills and tools demand
def plot_skills_analysis(skill_counts, tool_counts):
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # Top 15 skills
    top_skills = dict(skill_counts.most_common(15))
    pd.Series(top_skills).plot(kind='barh', ax=axes[0])
    axes[0].set_title('Top 15 Required Skills')
    
    # Top 15 tools
    top_tools = dict(tool_counts.most_common(15))
    pd.Series(top_tools).plot(kind='barh', ax=axes[1])
    axes[1].set_title('Top 15 Preferred Tools')
    
    plt.tight_layout()
    plt.show()

# Create heatmap of job titles vs industries
def plot_job_industry_heatmap(df):
    job_industry_crosstab = pd.crosstab(df['job_title'], df['industry'])
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(job_industry_crosstab, annot=True, fmt='d', cmap='Blues')
    plt.title('Job Titles vs Industries Distribution')
    plt.tight_layout()
    plt.show()

# Analyze employment types and company sizes
def plot_employment_analysis(df):
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Employment type distribution
    df['employment_type'].value_counts().plot(kind='pie', ax=axes[0,0], autopct='%1.1f%%')
    axes[0,0].set_title('Employment Type Distribution')
    
    # Company size distribution  
    df['company_size'].value_counts().plot(kind='pie', ax=axes[0,1], autopct='%1.1f%%')
    axes[0,1].set_title('Company Size Distribution')
    
    # Experience level distribution
    df['experience_level'].value_counts().plot(kind='pie', ax=axes[1,0], autopct='%1.1f%%')
    axes[1,0].set_title('Experience Level Distribution')
    
    # Industry distribution
    df['industry'].value_counts().plot(kind='pie', ax=axes[1,1], autopct='%1.1f%%')
    axes[1,1].set_title('Industry Distribution')
    
    plt.tight_layout()
    plt.show()

# Generate summary statistics table
def generate_summary_stats(df):
    print("\n=== SALARY STATISTICS ===")
    print(f"Overall salary range: ${df['salary_min'].min():,} - ${df['salary_max'].max():,}")
    print(f"Average salary midpoint: ${df['salary_mid'].mean():,.0f}")
    print(f"Median salary midpoint: ${df['salary_mid'].median():,.0f}")
    
    print("\n=== SALARY BY EXPERIENCE ===")
    exp_salary = df.groupby('experience_level')['salary_mid'].agg(['mean', 'median', 'count'])
    print(exp_salary)
    
    print("\n=== SALARY BY JOB TITLE ===")
    job_salary = df.groupby('job_title')['salary_mid'].agg(['mean', 'median', 'count'])
    print(job_salary.sort_values('mean', ascending=False))
    
    print("\n=== TOP COMPANIES BY JOB COUNT ===")
    print(df['company_name'].value_counts().head(10))

def main():
    # Load and prepare data
    df = load_data()
    df = parse_salaries(df)
    df = parse_dates(df)
    
    # Extract skills and tools
    skill_counts = extract_skills(df)
    tool_counts = extract_tools(df)
    
    # Generate visualizations
    plot_salary_analysis(df)
    plot_time_trends(df)  
    plot_skills_analysis(skill_counts, tool_counts)
    plot_job_industry_heatmap(df)
    plot_employment_analysis(df)
    
    # Print summary statistics
    generate_summary_stats(df)
    
    print(f"\nTop 10 Skills: {[skill for skill, _ in skill_counts.most_common(10)]}")
    print(f"Top 10 Tools: {[tool for tool, _ in tool_counts.most_common(10)]}")

if __name__ == "__main__":
    main()
