import sys
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


# --------------------------------------------------
# Configuration
# --------------------------------------------------


TARGET_ROLE = sys.argv[1] if len(sys.argv) > 1 else "Java Developer"
TARGET_LOCATION = sys.argv[2] if len(sys.argv) > 2 else "Maharashtra"

INPUT_FILE = Path(
    f"data/processed/"
    f"{TARGET_ROLE.lower().replace(' ', '_')}_"
    f"{TARGET_LOCATION.lower().replace(' ', '_')}.jsonl"
)

DB_PATH = "data/processed/qdrant_db"

COLLECTION_NAME = (
    f"{TARGET_ROLE.lower().replace(' ', '_')}_"
    f"{TARGET_LOCATION.lower().replace(' ', '_')}"
)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# --------------------------------------------------
# Load documents
# --------------------------------------------------

print("Loading evidence documents...")

documents = []

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as file:

    for line in file:
        documents.append(
            json.loads(line)
        )

print(
    f"Documents loaded: {len(documents)}"
)


# --------------------------------------------------
# Load embedding model
# --------------------------------------------------

print("\nLoading embedding model...")

model = SentenceTransformer(
    EMBEDDING_MODEL
)

print("Embedding model loaded.")


# --------------------------------------------------
# Generate embeddings
# --------------------------------------------------

texts = [
    document["text"]
    for document in documents
]

print("\nGenerating embeddings...")

embeddings = model.encode(
    texts,
    show_progress_bar=True
)

print(
    f"Embeddings generated: {len(embeddings)}"
)

print(
    f"Vector dimensions: {embeddings.shape[1]}"
)


# --------------------------------------------------
# Create local Qdrant database
# --------------------------------------------------

print("\nCreating Qdrant database...")

client = QdrantClient(
    path=DB_PATH
)


# --------------------------------------------------
# Recreate collection
# --------------------------------------------------

if client.collection_exists(
    COLLECTION_NAME
):
    print(
        f"Collection '{COLLECTION_NAME}' already exists."
    )

    client.delete_collection(
        COLLECTION_NAME
    )


client.create_collection(
    collection_name=COLLECTION_NAME,

    vectors_config=VectorParams(
        size=embeddings.shape[1],
        distance=Distance.COSINE,
    ),
)


# --------------------------------------------------
# Create Qdrant points
# --------------------------------------------------

points = []

for document, embedding in zip(
    documents,
    embeddings
):

    points.append(
        PointStruct(
            id=document["id"],

            vector=embedding.tolist(),

            payload={
                "text": document["text"],
                "metadata": document["metadata"],
            },
        )
    )

# --------------------------------------------------
# Insert into Qdrant
# --------------------------------------------------

print("\nUploading vectors to Qdrant...")

client.upsert(
    collection_name=COLLECTION_NAME,
    points=points,
)


# --------------------------------------------------
# Verify
# --------------------------------------------------

collection_info = client.get_collection(
    COLLECTION_NAME
)

print("\n========== QDRANT INDEXING COMPLETE ==========")

print(
    f"Collection: {COLLECTION_NAME}"
)

print(
    f"Vectors stored: "
    f"{collection_info.points_count}"
)

print(
    f"Database path: {DB_PATH}"
)


# --------------------------------------------------
# Close Qdrant cleanly
# --------------------------------------------------

client.close()

print("\nQdrant client closed.")