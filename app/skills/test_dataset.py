import pandas as pd

from extractor import extract_skills


FILE_PATH = r"C:\_Working Folder\Nallin\VS\Python\skillManagement-ai\data\raw\jobs\indian-job-market-dataset-2025.xlsx"

df = pd.read_csv(
    FILE_PATH,
    usecols=["Job Title", "Role", "skills"]
)

backend = df[
    df["Role"].astype(str).str.contains(
        "Backend Developer",
        case=False,
        na=False
    )
].head(100)

print("Testing on:", len(backend), "backend jobs\n")

for index, row in backend.iterrows():

    text = row["skills"]

    extracted = extract_skills(text)

    print(f"Job: {row['Job Title']}")
    print(f"Extracted: {extracted}")
    print("-" * 60)