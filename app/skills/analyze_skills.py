
import sys
import pandas as pd
from pathlib import Path
from collections import Counter
from extractor import extract_skills

# --------------------------------------------------
# Configuration
# --------------------------------------------------

FILE_PATH = Path(
    "data/raw/jobs/indian-job-market-dataset-2025.xlsx"
)

TARGET_ROLE = sys.argv[1] if len(sys.argv) > 1 else "Java Developer"
TARGET_LOCATION = sys.argv[2] if len(sys.argv) > 2 else "Maharashtra"

LOCATION_PATTERNS = {
    "Maharashtra": (
        r"mumbai|pune|nagpur|nashik|aurangabad|"
        r"chhatrapati sambhaji nagar|thane|navi mumbai|"
        r"kolhapur|solapur|maharashtra"
    ),

    "Karnataka": (
        r"bengaluru|bangalore|mysuru|mangalore"
    ),

    "Telangana": (
        r"hyderabad"
    ),

    "Tamil Nadu": (
        r"chennai|coimbatore|madurai|salem|tiruchirappalli"
    ),

    "Delhi NCR": (
        r"gurugram|gurgaon|noida|delhi|faridabad|"
        r"ghaziabad"
    ),

    "Gujarat": (
        r"ahmedabad|vadodara|surat|rajkot"
    ),

}


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

print("Loading dataset...")

df = pd.read_excel(
    FILE_PATH,
    usecols=[
        "title",
        "location",
        "tagsAndSkills",
    ],
    engine="openpyxl",
)

print(f"Total jobs: {len(df):,}")


# --------------------------------------------------
# Filter 
# --------------------------------------------------

location_jobs = df[
    df["location"]
    .fillna("")
    .str.lower()
    .str.contains(
        LOCATION_PATTERNS[TARGET_LOCATION],
        regex=True,
        na=False
    )
].copy()


# --------------------------------------------------
# Filter target role
# --------------------------------------------------

role_jobs = location_jobs[
    location_jobs["title"]
    .fillna("")
    .str.lower()
    .eq(TARGET_ROLE.lower())
].copy()


print(
    f"{TARGET_LOCATION} {TARGET_ROLE} jobs: "
    f"{len(role_jobs):,}"
)

# --------------------------------------------------
# Extract normalized skills
# --------------------------------------------------

skill_counter = Counter()

jobs_with_skills = 0

for skills in role_jobs["tagsAndSkills"].dropna():

    extracted_skills = extract_skills(str(skills))

    if extracted_skills:
        jobs_with_skills += 1

    # One skill should count only once per job
    skill_counter.update(set(extracted_skills))


# --------------------------------------------------
# Calculate demand %
# --------------------------------------------------

print("\n========== NORMALIZED SKILL DEMAND ==========")

for skill, count in skill_counter.most_common():

    demand_percentage = (
        count / len(role_jobs)
    ) * 100

    print(
        f"{skill:<25} "
        f"{count:>3} jobs "
        f"({demand_percentage:>5.1f}%)"
    )


print("\n========== SUMMARY ==========")

print(f"Target jobs: {len(role_jobs):,}")
print(f"Jobs with recognized skills: {jobs_with_skills:,}")
print(f"Unique normalized skills: {len(skill_counter):,}")


# --------------------------------------------------
# Save market skill demand
# --------------------------------------------------

demand_data = []

for skill, count in skill_counter.most_common():

    demand_percentage = (
        count / len(role_jobs)
    ) * 100

    demand_data.append({
        "role": TARGET_ROLE,
        "location": TARGET_LOCATION,
        "skill": skill,
        "job_count": count,
        "demand_percentage": round(
            demand_percentage,
            2
        ),
    })


demand_df = pd.DataFrame(demand_data)


OUTPUT_PATH = Path(
    "data/processed/market_skill_demand.csv"
)

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

demand_df.to_csv(
    OUTPUT_PATH,
    index=False
)

print(
    f"\nSaved market skill demand to: "
    f"{OUTPUT_PATH}"
)