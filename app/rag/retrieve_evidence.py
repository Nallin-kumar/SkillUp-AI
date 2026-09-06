import pandas as pd

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

# =========================
# Configuration
# =========================

import sys

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

DB_PATH = "data/processed/qdrant_db"

COLLECTION_NAME = (
    f"{TARGET_ROLE.lower().replace(' ', '_')}_"
    f"{TARGET_LOCATION.lower().replace(' ', '_')}"
)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

GAP_REPORT = "data/processed/skill_gap_report.csv"

TOP_K = 3


# =========================
# Load model and database
# =========================

model = SentenceTransformer(EMBEDDING_MODEL)

client = QdrantClient(path=DB_PATH)


# =========================
# Retrieve evidence
# =========================

def retrieve_evidence(skill: str, top_k: int = TOP_K):

    query = f"{TARGET_ROLE} experience with {skill}"

    query_embedding = model.encode(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding.tolist(),
        query_filter=Filter(
            must=[
                FieldCondition(
                key="metadata.role",
                match=MatchValue(value=TARGET_ROLE)
            ),
                FieldCondition(
                    key="metadata.region",
                    match=MatchValue(value=TARGET_LOCATION)
            ),
            ]
        ),
        limit=top_k,
    ).points

    return results


# =========================
# Main
# =========================

if __name__ == "__main__":

    gap_df = pd.read_csv(GAP_REPORT)

    # Keep only skills missing from the curriculum
    missing_skills = gap_df[gap_df["gap"]]

    print("\n========================================")
    print("SKILL GAP → EVIDENCE RETRIEVAL")
    print("========================================")

    print(f"\nMissing skills: {len(missing_skills)}")

    try:

        for _, row in missing_skills.iterrows():

            skill = row["skill"]
            demand = row["demand_percentage"]
            priority = row["priority"]

            print("\n\n========================================")
            print(f"SKILL: {skill}")
            print(f"Demand: {demand:.2f}%")
            print(f"Priority: {priority}")
            print("========================================")

            results = retrieve_evidence(skill)

            if not results:
                print("\nNo evidence found.")
                continue

            for rank, result in enumerate(results, start=1):

                metadata = result.payload["metadata"]

                print(f"\n--- Evidence {rank} ---")
                print(f"Similarity: {result.score:.4f}")
                print(f"Location: {metadata['location']}")
                print(f"Skills: {metadata['skills']}")

                print("\nJob Description:")
                print(result.payload["text"][:500])

    finally:

        # Explicitly close Qdrant
        client.close()