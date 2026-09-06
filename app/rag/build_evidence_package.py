import sys
import json
import pandas as pd

from retrieve_evidence import retrieve_evidence


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

GAP_REPORT = "data/processed/skill_gap_report.csv"
OUTPUT_FILE = "data/processed/evidence_package.json"

TOP_K = 3


def build_evidence_package():

    gap_df = pd.read_csv(GAP_REPORT)

    missing_skills = gap_df[gap_df["gap"]]

    evidence_package = []

    for _, row in missing_skills.iterrows():

        skill = row["skill"]

        results = retrieve_evidence(
            skill=skill,
            top_k=TOP_K
        )

        evidence = []

        for result in results:

            metadata = result.payload["metadata"]

            evidence.append({
                "similarity": round(result.score, 4),
                "title": metadata["title"],
                "location": metadata["location"],
                "skills": metadata["skills"],
                "job_description": result.payload["text"]
            })

        evidence_package.append({
            "skill": skill,
            "demand_percentage": row["demand_percentage"],
            "priority": row["priority"],
            "evidence_count": len(evidence),
            "evidence": evidence
        })

    return evidence_package


if __name__ == "__main__":

    package = build_evidence_package()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            package,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\n========================================")
    print("EVIDENCE PACKAGE CREATED")
    print("========================================")

    print(f"\nSkills processed: {len(package)}")
    print(f"Output: {OUTPUT_FILE}")

    for item in package:
        print(
            f"\n{item['skill']}"
            f" | Demand: {item['demand_percentage']:.2f}%"
            f" | Priority: {item['priority']}"
            f" | Evidence: {item['evidence_count']}"
        )