import pandas as pd
from pathlib import Path

FILE_PATH = Path("data/raw/jobs/indian-job-market-dataset-2025.xlsx")

USE_COLS = [
    "title",
    "location",
    "tagsAndSkills",
    "jobDescription",
]


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

print("Loading dataset...")

df = pd.read_excel(
    FILE_PATH,
    usecols=USE_COLS,
    engine="openpyxl"
)

print("\n========== DATASET OVERVIEW ==========")

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print("\nColumns:")
print(df.columns.tolist())


# --------------------------------------------------
# Missing values
# --------------------------------------------------

print("\n========== MISSING VALUES ==========")

print(df.isnull().sum())


# --------------------------------------------------
# Job title distribution
# --------------------------------------------------

print("\n========== TOP JOB TITLES ==========")

print(
    df["title"]
    .value_counts()
    .head(30)
)


# --------------------------------------------------
# IT / Software jobs
# --------------------------------------------------

it_keywords = [
    "software",
    "developer",
    "engineer",
    "programmer",
    "backend",
    "frontend",
    "full stack",
    "fullstack",
    "devops",
    "cloud",
    "data",
    "machine learning",
    "artificial intelligence",
    "ai",
    "python",
    "java",
    "dotnet",
    ".net",
    "c#",
    "web developer",
]

pattern = "|".join(it_keywords)

it_jobs = df[
    df["title"]
    .fillna("")
    .str.lower()
    .str.contains(pattern, regex=True)
]

print("\n========== IT / SOFTWARE JOBS ==========")

print(f"IT-related jobs: {len(it_jobs):,}")


# --------------------------------------------------
# Maharashtra jobs
# --------------------------------------------------

maharashtra_locations = [
    "mumbai",
    "pune",
    "nagpur",
    "nashik",
    "aurangabad",
    "chhatrapati sambhaji nagar",
    "thane",
    "navi mumbai",
    "kolhapur",
    "solapur",
    "maharashtra",
]

mh_pattern = "|".join(maharashtra_locations)

mh_jobs = df[
    df["location"]
    .fillna("")
    .str.lower()
    .str.contains(mh_pattern, regex=True)
]

print("\n========== MAHARASHTRA JOBS ==========")

print(f"Maharashtra-related jobs: {len(mh_jobs):,}")


# --------------------------------------------------
# Maharashtra IT jobs
# --------------------------------------------------

mh_it_jobs = it_jobs[
    it_jobs["location"]
    .fillna("")
    .str.lower()
    .str.contains(mh_pattern, regex=True)
]

print("\n========== MAHARASHTRA IT ROLE DISTRIBUTION ==========")

mh_it = df[
    df["location"]
    .fillna("")
    .str.lower()
    .str.contains(mh_pattern, regex=True)
]

it_role_keywords = [
    "developer",
    "software",
    "engineer",
    "devops",
    "data",
    "cloud",
    "ai",
    "machine learning",
    "full stack",
    "frontend",
    "backend",
    "application",
    "technical lead",
]

it_role_pattern = "|".join(it_role_keywords)

mh_it_roles = mh_it[
    mh_it["title"]
    .fillna("")
    .str.lower()
    .str.contains(it_role_pattern, regex=True)
]

print(f"Maharashtra IT-role jobs: {len(mh_it_roles):,}")

print("\nTop IT roles in Maharashtra:")

print(
    mh_it_roles["title"]
    .value_counts()
    .head(50)
)