import pandas as pd
from pathlib import Path


FILE_PATH = Path(
    "data/raw/jobs/indian-job-market-dataset-2025.xlsx"
)

TARGET_ROLES = ["Java Developer"]


MAHARASHTRA_PATTERN = (
    r"mumbai|pune|nagpur|nashik|aurangabad|"
    r"chhatrapati sambhaji nagar|thane|navi mumbai|"
    r"kolhapur|solapur|maharashtra"
)


df = pd.read_excel(
    FILE_PATH,
    usecols=[
        "title",
        "location",
        "tagsAndSkills",
        "jobDescription",
    ],
    engine="openpyxl",
)


# Maharashtra only
df = df[
    df["location"]
    .fillna("")
    .str.lower()
    .str.contains(
        MAHARASHTRA_PATTERN,
        regex=True
    )
]


for role in TARGET_ROLES:

    print("\n")
    print("=" * 70)
    print(f"ROLE: {role}")
    print("=" * 70)

    role_df = df[
        df["title"]
        .fillna("")
        .str.lower()
        .eq(role.lower())
    ]

    print(f"Total postings: {len(role_df)}")

    # Show first 5 postings
    for index, (_, row) in enumerate(
        role_df.head(5).iterrows(),
        start=1
    ):

        print(f"\n--- Posting {index} ---")

        print(f"Title: {row['title']}")
        print(f"Location: {row['location']}")

        print(
            f"Skills: "
            f"{row['tagsAndSkills']}"
        )

        description = str(row["jobDescription"])

        print(
            f"Description: "
            f"{description[:500]}"
        )