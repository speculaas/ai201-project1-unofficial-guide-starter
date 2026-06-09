from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"


HEADER_FIELDS = {
    "TITLE",
    "SOURCE",
    "URL",
    "DATE_ACCESSED",
    "TOPIC",
    "DOCUMENT_TYPE",
    "COPYRIGHT_NOTE",
}


REDDIT_UI_NOISE = (
    "Reply",
    "Award",
    "Share",
    "Sort by",
    "Upvote",
    "Downvote",
    "View community ranking",
    "Log In",
    "Sign Up",
)


def ensure_dirs() -> None:
    for path in (RAW_DIR, PROCESSED_DIR, CHUNKS_DIR, CHROMA_DIR):
        path.mkdir(parents=True, exist_ok=True)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run the previous pipeline step first.")
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def strip_known_noise(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if stripped in REDDIT_UI_NOISE:
            continue
        if re.fullmatch(r"\d+\s*(comments?|points?|votes?)", stripped, flags=re.I):
            continue
        lines.append(stripped)
    return normalize_whitespace("\n".join(lines))


def parse_source_file(path: Path) -> dict[str, Any]:
    metadata: dict[str, str] = {"filename": path.name}
    body_lines: list[str] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().upper()
            if key in HEADER_FIELDS:
                metadata[key.lower()] = value.strip()
                continue
        body_lines.append(line)

    body = strip_known_noise("\n".join(body_lines))
    body = body.replace(
        "Paste selected relevant public post/comment text here if your course permits using it. "
        "Remove Reddit UI noise such as Reply, Award, Share, Sort by, and vote counts.",
        "",
    )
    body = normalize_whitespace(body)

    return {
        "id": path.stem,
        "text": body,
        "metadata": metadata,
    }


def source_label(metadata: dict[str, Any]) -> str:
    title = metadata.get("title") or metadata.get("filename") or "Untitled source"
    url = metadata.get("url") or ""
    return f"{title} ({url})" if url else str(title)
