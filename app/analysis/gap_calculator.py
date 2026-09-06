import sys
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# Configuration
# --------------------------------------------------

TARGET_ROLE = (
    sys.argv[1]
    if len(sys.argv) > 1
    else "Java Developer"
)

TARGET_LOCATION = (
    sys.argv[2]
    if len(sys.argv) > 2
    else "Maharashtra"
)

COURSE_FILE = (
    sys.argv[3]
    if len(sys.argv) > 3
    else "java_full_stack_curriculum.csv"
)


MARKET_FILE = Path(
    "data/processed/market_skill_demand.csv"
)

CURRICULUM_FILE = Path(
    "data/raw/courses"
) / COURSE_FILE

OUTPUT_FILE = Path(
    "data/processed/skill_gap_report.csv"
)


# --------------------------------------------------
# Display configuration
# --------------------------------------------------

print("\n========================================")
print("SKILL GAP ANALYSIS")
print("========================================")

print(f"Job Title : {TARGET_ROLE}")
print(f"Location  : {TARGET_LOCATION}")
print(f"Course    : {COURSE_FILE}")


# --------------------------------------------------
# Load data
# --------------------------------------------------

print("\nLoading market demand...")

market_df = pd.read_csv(MARKET_FILE)


# --------------------------------------------------
# Filter market data
# --------------------------------------------------

market_df = market_df[
    (market_df["role"].str.lower() == TARGET_ROLE.lower()) &
    (market_df["location"].str.lower() == TARGET_LOCATION.lower())
].copy()


if market_df.empty:

    print(
        f"\nNo market demand data found for "
        f"{TARGET_ROLE} in {TARGET_LOCATION}."
    )

    sys.exit(1)


print(
    f"Market records found: {len(market_df)}"
)


print("\nLoading curriculum...")

curriculum_df = pd.read_csv(
    CURRICULUM_FILE
)


# --------------------------------------------------
# Get curriculum skills
# --------------------------------------------------

course_skills = set(
    curriculum_df["skill"]
    .dropna()
    .str.strip()
)


# --------------------------------------------------
# Calculate skill gaps
# --------------------------------------------------

gap_rows = []

for _, row in market_df.iterrows():

    skill = row["skill"]

    covered = skill in course_skills

    gap_rows.append({
        "role": row["role"],
        "location": row["location"],
        "skill": skill,
        "job_count": row["job_count"],
        "demand_percentage": row["demand_percentage"],
        "course_covers_skill": covered,
        "gap": not covered,

        # V1 priority score:
        # Higher market demand = higher priority
        "gap_score": (
            row["demand_percentage"]
            if not covered
            else 0
        ),
    })


gap_df = pd.DataFrame(
    gap_rows
)


# --------------------------------------------------
# Priority classification
# --------------------------------------------------

def get_priority(score):

    if score >= 50:
        return "High"

    elif score >= 15:
        return "Medium"

    elif score > 0:
        return "Low"

    return "None"


gap_df["priority"] = gap_df[
    "gap_score"
].apply(get_priority)


# --------------------------------------------------
# Sort by gap score
# --------------------------------------------------

gap_df = gap_df.sort_values(
    by="gap_score",
    ascending=False
)


# --------------------------------------------------
# Save complete report
# --------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

gap_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# Display prioritized gaps
# --------------------------------------------------

missing_df = gap_df[
    gap_df["gap"]
].copy()


print("\n========== PRIORITIZED SKILL GAPS ==========")

if missing_df.empty:

    print("No skill gaps found.")

else:

    print(
        missing_df[
            [
                "skill",
                "job_count",
                "demand_percentage",
                "gap_score",
                "priority",
            ]
        ].to_string(index=False)
    )


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\n========== SUMMARY ==========")

print(
    f"Market skills: {len(gap_df)}"
)

print(
    f"Covered skills: "
    f"{(~gap_df['gap']).sum()}"
)

print(
    f"Missing skills: "
    f"{gap_df['gap'].sum()}"
)

print(
    f"High priority gaps: "
    f"{(gap_df['priority'] == 'High').sum()}"
)

print(
    f"Medium priority gaps: "
    f"{(gap_df['priority'] == 'Medium').sum()}"
)

print(
    f"Low priority gaps: "
    f"{(gap_df['priority'] == 'Low').sum()}"
)

print(
    f"\nSaved report to: {OUTPUT_FILE}"
)