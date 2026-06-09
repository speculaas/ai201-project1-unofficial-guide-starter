from __future__ import annotations

import argparse

from common import CHUNKS_DIR, PROCESSED_DIR, normalize_whitespace, read_jsonl, write_jsonl


DEFAULT_CHUNK_SIZE = 900
DEFAULT_OVERLAP = 150


def split_long_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        window = text[start:end]

        if end < len(text):
            split_at = max(window.rfind("\n\n"), window.rfind(". "), window.rfind("; "))
            if split_at > chunk_size * 0.55:
                end = start + split_at + 1
                window = text[start:end]

        chunks.append(normalize_whitespace(window))
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [chunk for chunk in chunks if chunk]


def chunk_document(document: dict, chunk_size: int, overlap: int) -> list[dict]:
    paragraphs = [
        normalize_whitespace(paragraph)
        for paragraph in document["text"].split("\n\n")
        if normalize_whitespace(paragraph)
    ]

    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = normalize_whitespace(f"{current}\n\n{paragraph}" if current else paragraph)
        if len(candidate) <= chunk_size:
            current = candidate
            continue
        if current:
            chunks.extend(split_long_text(current, chunk_size, overlap))
        current = paragraph

    if current:
        chunks.extend(split_long_text(current, chunk_size, overlap))

    output: list[dict] = []
    for index, text in enumerate(chunks):
        metadata = dict(document["metadata"])
        metadata.update(
            {
                "source_id": document["id"],
                "chunk_index": index,
                "chunk_size": len(text),
            }
        )
        output.append(
            {
                "id": f"{document['id']}::chunk-{index:03d}",
                "text": text,
                "metadata": metadata,
            }
        )
    return output


def build_chunks(chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP) -> list[dict]:
    documents = read_jsonl(PROCESSED_DIR / "documents.jsonl")
    chunks: list[dict] = []
    for document in documents:
        chunks.extend(chunk_document(document, chunk_size=chunk_size, overlap=overlap))
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Chunk cleaned UC Berkeley housing documents.")
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument("--overlap", type=int, default=DEFAULT_OVERLAP)
    parser.add_argument("--preview", type=int, default=5)
    args = parser.parse_args()

    chunks = build_chunks(chunk_size=args.chunk_size, overlap=args.overlap)
    output_path = CHUNKS_DIR / "chunks.jsonl"
    write_jsonl(output_path, chunks)
    print(f"Wrote {len(chunks)} chunks to {output_path}")

    for chunk in chunks[: args.preview]:
        title = chunk["metadata"].get("title", chunk["metadata"].get("filename"))
        print("\n---")
        print(f"{chunk['id']} | {title}")
        print(chunk["text"][:500])


if __name__ == "__main__":
    main()
