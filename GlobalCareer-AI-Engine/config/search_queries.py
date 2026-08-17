"""
Search Query Matrix — GlobalCareer-AI-Engine
"""

DATA_ENGINEERING_QUERIES = [
    "Data Engineer Remote", "Senior Data Engineer", "Lead Data Engineer",
    "Staff Data Engineer", "Principal Data Engineer", "Databricks Engineer",
    "Databricks Developer", "dbt Developer", "dbt Engineer",
    "dbt Analytics Engineer", "ETL Developer Remote", "ELT Engineer",
    "Data Platform Engineer", "Analytics Engineer", "Data Warehouse Engineer",
    "Data Pipeline Engineer", "Big Data Engineer", "Cloud Data Engineer",
    "Azure Data Engineer", "AWS Data Engineer", "GCP Data Engineer",
    "Snowflake Developer", "Spark Developer", "PySpark Engineer",
]

BI_QLIK_QUERIES = [
    "Qlik Sense Developer", "QlikView Developer", "Qlik Developer",
    "Qlik Cloud Developer", "Qlik Sense Architect", "Qlik Specialist",
    "Qlik Consultant", "Qlik BI Developer", "Business Intelligence Engineer",
    "BI Developer Remote", "BI Engineer", "BI Architect",
    "Business Intelligence Developer", "BI Consultant Remote",
    "Analytics Developer", "Reporting Developer", "Enterprise BI Developer",
]

POWER_BI_TABLEAU_QUERIES = [
    "Power BI Developer", "Power BI Engineer", "Power BI Architect",
    "Tableau Developer", "Looker Developer", "MicroStrategy Developer",
]

DATA_MIGRATION_QUERIES = [
    "Data Migration Engineer", "Data Migration Specialist",
    "BI Migration Engineer", "Data Integration Engineer",
]

SQL_DATABASE_QUERIES = [
    "SQL Developer Remote", "Senior SQL Developer", "Database Engineer",
    "Data Analyst Remote", "Senior Data Analyst",
]

AI_ML_QUERIES = [
    "AI Engineer", "MLOps Engineer", "AI Data Engineer", "LLM Engineer",
]

ALL_SEARCH_QUERIES = (
    DATA_ENGINEERING_QUERIES + BI_QLIK_QUERIES + POWER_BI_TABLEAU_QUERIES +
    DATA_MIGRATION_QUERIES + SQL_DATABASE_QUERIES + AI_ML_QUERIES
)

COMPACT_QUERIES = [
    "Data Engineer Remote", "Databricks dbt Engineer",
    "Qlik Sense Developer", "Business Intelligence Engineer",
    "BI Developer Remote", "Data Migration Engineer",
    "Analytics Engineer Remote", "SQL Developer Remote",
    "Power BI Developer Remote", "ETL Developer Remote",
    "Senior Data Engineer", "AI Data Engineer",
]

CORE_SKILLS_KEYWORDS = [
    "qlik", "qlik sense", "qlikview", "qlik cloud", "qvd", "nprinting",
    "databricks", "dbt", "dbt core", "sql", "pyspark", "python",
    "power bi", "tableau", "looker", "etl", "elt", "data pipeline",
    "data warehouse", "data migration", "data engineering",
    "analytics engineering", "business intelligence", "bi developer",
    "star schema", "snowflake schema", "data modeling",
    "hadoop", "hive", "spark", "airflow", "data lake", "lakehouse",
]

PREMIUM_MATCH_KEYWORDS = [
    "qlik", "qlik sense", "qlikview", "databricks", "dbt",
    "data migration", "bi developer", "business intelligence engineer",
]
