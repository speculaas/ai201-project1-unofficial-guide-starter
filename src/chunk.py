from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import CHUNKS_DIR, RAW_DIR, normalize_whitespace, write_jsonl


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_OVERLAP = 150
CONTENT_MARKER = "MANUAL_COLLECTION_SPACE:"
HEADER_FIELDS = {
    "TITLE": "title",
    "SOURCE": "source",
    "URL": "url",
    "URLS": "url",
    "DATE_ACCESSED": "date_accessed",
    "TOPIC": "topic",
    "DOCUMENT_TYPE": "document_type",
    "DOMAIN": "domain",
}


def parse_raw_file(path: Path) -> dict:
    raw_text = path.read_text(encoding="utf-8")
    metadata = {"source_file": path.name}

    before_marker, separator, after_marker = raw_text.partition(CONTENT_MARKER)
    if not separator:
        print(f"Warning: skipping {path.name}; missing {CONTENT_MARKER}")
        return {"id": path.stem, "text": "", "metadata": metadata}

    for line in before_marker.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        normalized_key = key.strip().upper()
        if normalized_key in HEADER_FIELDS:
            metadata[HEADER_FIELDS[normalized_key]] = value.strip()

    content = clean_content(after_marker)
    return {"id": path.stem, "text": content, "metadata": metadata}


def clean_content(text: str) -> str:
    text = text.replace(CONTENT_MARKER, "")
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if re.fullmatch(r"(Reply|Award|Share|Sort by|Upvote|Downvote)", stripped, flags=re.I):
            continue
        if re.fullmatch(r"\d+\s*(comments?|points?|votes?)", stripped, flags=re.I):
            continue
        lines.append(stripped)
    return normalize_whitespace("\n".join(lines))


def split_long_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    text = normalize_whitespace(text)
    if not text:
        return []
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

        chunk = normalize_whitespace(window)
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)

    return chunks


def chunk_document(document: dict, chunk_size: int, overlap: int) -> list[dict]:
    paragraphs = [
        normalize_whitespace(paragraph)
        for paragraph in document["text"].split("\n\n")
        if normalize_whitespace(paragraph)
    ]

    chunk_texts: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            if current:
                chunk_texts.extend(split_long_text(current, chunk_size, overlap))
                current = ""
            chunk_texts.extend(split_long_text(paragraph, chunk_size, overlap))
            continue

        candidate = normalize_whitespace(f"{current}\n\n{paragraph}" if current else paragraph)
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            chunk_texts.extend(split_long_text(current, chunk_size, overlap))
            current = paragraph

    if current:
        chunk_texts.extend(split_long_text(current, chunk_size, overlap))

    chunks: list[dict] = []
    for index, text in enumerate(chunk_texts):
        metadata = {
            "source_file": document["metadata"].get("source_file", ""),
            "title": document["metadata"].get("title", ""),
            "source": document["metadata"].get("source", ""),
            "url": document["metadata"].get("url", ""),
            "topic": document["metadata"].get("topic", ""),
            "chunk_index": index,
        }
        chunks.append(
            {
                "id": f"{document['id']}::chunk-{index:03d}",
                "text": text,
                "metadata": metadata,
            }
        )
    return chunks


def build_chunks(chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP) -> list[dict]:
    chunks: list[dict] = []
    for path in sorted(RAW_DIR.glob("*.txt")):
        document = parse_raw_file(path)
        if not document["text"]:
            continue
        chunks.extend(chunk_document(document, chunk_size=chunk_size, overlap=overlap))
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chunk MANUAL_COLLECTION_SPACE content from UC Berkeley housing raw documents."
    )
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument("--overlap", type=int, default=DEFAULT_OVERLAP)
    parser.add_argument("--preview", type=int, default=5)
    args = parser.parse_args()

    chunks = build_chunks(chunk_size=args.chunk_size, overlap=args.overlap)
    output_path = CHUNKS_DIR / "chunks.jsonl"
    write_jsonl(output_path, chunks)

    print(f"Total chunks written: {len(chunks)}")
    print(f"Output path: {output_path}")

    for chunk in chunks[: args.preview]:
        title = chunk["metadata"].get("title") or chunk["metadata"].get("source_file")
        print("\n---")
        print(f"{chunk['id']} | {title}")
        print(chunk["text"][:500])


if __name__ == "__main__":
    main()
