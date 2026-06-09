from __future__ import annotations

from common import PROCESSED_DIR, RAW_DIR, ensure_dirs, parse_source_file, write_jsonl


def load_documents() -> list[dict]:
    ensure_dirs()
    files = sorted(RAW_DIR.glob("*.txt"))
    if not files:
        raise FileNotFoundError(f"No .txt documents found in {RAW_DIR}")

    documents = []
    for path in files:
        document = parse_source_file(path)
        if not document["text"]:
            raise ValueError(f"{path.name} did not produce any clean text")
        documents.append(document)
    return documents


def main() -> None:
    documents = load_documents()
    output_path = PROCESSED_DIR / "documents.jsonl"
    write_jsonl(output_path, documents)
    print(f"Wrote {len(documents)} cleaned documents to {output_path}")


if __name__ == "__main__":
    main()
