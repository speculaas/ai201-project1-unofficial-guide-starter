from __future__ import annotations

import argparse

from common import CHROMA_DIR, CHUNKS_DIR, read_jsonl


DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "ucberkeley_housing"


def build_vector_store(model_name: str = DEFAULT_MODEL, collection_name: str = COLLECTION_NAME) -> None:
    import chromadb
    from sentence_transformers import SentenceTransformer

    chunks = read_jsonl(CHUNKS_DIR / "chunks.jsonl")
    if not chunks:
        raise ValueError("No chunks found. Run python src/chunk.py first.")

    model = SentenceTransformer(model_name)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine", "embedding_model": model_name},
    )

    metadatas = []
    for chunk in chunks:
        metadatas.append(
            {
                key: value
                for key, value in chunk["metadata"].items()
                if isinstance(value, (str, int, float, bool)) and value is not None
            }
        )

    collection.add(
        ids=[chunk["id"] for chunk in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    print(f"Stored {len(chunks)} chunks in Chroma collection '{collection_name}' at {CHROMA_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed chunks and store them in ChromaDB.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--collection", default=COLLECTION_NAME)
    args = parser.parse_args()
    build_vector_store(model_name=args.model, collection_name=args.collection)


if __name__ == "__main__":
    main()
