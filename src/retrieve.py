from __future__ import annotations

import argparse
from typing import Any

from embed import COLLECTION_NAME, DEFAULT_MODEL
from common import CHROMA_DIR, source_label


def search(query: str, top_k: int = 5, model_name: str = DEFAULT_MODEL) -> list[dict[str, Any]]:
    import chromadb
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    query_embedding = model.encode([query], normalize_embeddings=True).tolist()[0]

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection(COLLECTION_NAME)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    matches: list[dict[str, Any]] = []
    for index, chunk_id in enumerate(results["ids"][0]):
        metadata = results["metadatas"][0][index]
        matches.append(
            {
                "id": chunk_id,
                "text": results["documents"][0][index],
                "metadata": metadata,
                "distance": results["distances"][0][index],
                "source": source_label(metadata),
            }
        )
    return matches


def format_matches(matches: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for rank, match in enumerate(matches, start=1):
        lines.append(f"[{rank}] {match['source']}")
        lines.append(f"chunk_id: {match['id']} | distance: {match['distance']:.4f}")
        lines.append(match["text"])
        lines.append("")
    return "\n".join(lines).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieve relevant UC Berkeley housing chunks.")
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    print(format_matches(search(args.query, top_k=args.top_k)))


if __name__ == "__main__":
    main()
