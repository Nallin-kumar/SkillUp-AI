import sys
import json
import re
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# Configuration
# --------------------------------------------------
INPUT_FILE = Path(
    "data/raw/jobs/indian-job-market-dataset-2025.xlsx"
)

TARGET_ROLE = sys.argv[1] if len(sys.argv) > 1 else "Java Developer"
TARGET_LOCATION = sys.argv[2] if len(sys.argv) > 2 else "Maharashtra"


OUTPUT_FILE = Path(
    f"data/processed/"
    f"{TARGET_ROLE.lower().replace(' ', '_')}_"
    f"{TARGET_LOCATION.lower().replace(' ', '_')}.jsonl"
)


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
        r"gurugram|gurgaon|noida|delhi|faridabad|ghaziabad"
    ),

    "Gujarat": (
        r"ahmedabad|vadodara|surat|rajkot"
    ),
}


# --------------------------------------------------
# Helper: clean job description
# --------------------------------------------------

def clean_text(text):

    if pd.isna(text):
        return ""

    text = str(text)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Decode common HTML whitespace
    text = text.replace("&nbsp;", " ")

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

print("Loading dataset...")

df = pd.read_excel(
    INPUT_FILE,
    usecols=[
        "title",
        "location",
        "tagsAndSkills",
        "jobDescription",
    ],
    engine="openpyxl",
)

print(f"Total jobs loaded: {len(df):,}")


# --------------------------------------------------
# Filter 
# --------------------------------------------------

location_series = (
    df["location"]
    .fillna("")
    .astype(str)
    .str.lower()
)

mh_df = df[
    location_series.str.contains(
        LOCATION_PATTERNS[TARGET_LOCATION],
        regex=True,
        na=False,
    )
].copy()


# --------------------------------------------------
# Filter Java Developer
# --------------------------------------------------

title_series = (
    mh_df["title"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
)

java_df = mh_df[
    title_series.eq(
        TARGET_ROLE.lower()
    )
].copy()


print(
    f"{TARGET_ROLE} jobs: "
    f"{len(java_df):,}"
)


# --------------------------------------------------
# Save processed evidence
# --------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

document_count = 0
first_document = None

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8",
) as file:

    for index, (_, row) in enumerate(
        java_df.iterrows(),
        start=1,
    ):

        title = clean_text(
            row["title"]
        )

        location = clean_text(
            row["location"]
        )

        skills = clean_text(
            row["tagsAndSkills"]
        )

        description = clean_text(
            row["jobDescription"]
        )

        # Combine searchable information
        text = (
            f"Job Title: {title}\n"
            f"Location: {location}\n"
            f"Skills: {skills}\n"
            f"Job Description: {description}"
        )

        document = {
            "id": index,
            "text": text,
            "metadata": {
                "title": title,
                "location": location,
                "skills": skills,
                "role": TARGET_ROLE,
                "region": TARGET_LOCATION,
            },
        }

        file.write(
            json.dumps(
                document,
                ensure_ascii=False,
            )
            + "\n"
        )

        document_count += 1

        if first_document is None:
            first_document = document


# --------------------------------------------------
# Summary
# --------------------------------------------------

print(
    "\n========== EVIDENCE PREPARATION =========="
)

print(
    f"Documents created: {document_count}"
)

print(
    f"Output file: {OUTPUT_FILE}"
)


# --------------------------------------------------
# Show sample
# --------------------------------------------------

if first_document:

    print(
        "\n========== SAMPLE DOCUMENT =========="
    )

    print(
        json.dumps(
            first_document,
            indent=2,
            ensure_ascii=False,
        )
    )