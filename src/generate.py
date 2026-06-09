from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq

from retrieve import search


MODEL_NAME = "llama-3.3-70b-versatile"


SYSTEM_PROMPT = """You answer questions for a UC Berkeley student housing unofficial guide.
Use only the retrieved source excerpts provided in the user message.
If the excerpts do not contain enough evidence, say you do not have enough information.
Treat Reddit material as subjective student advice, not verified fact.
Include a short Sources section that lists the source numbers you used."""


def build_context(matches: list[dict[str, Any]]) -> str:
    sections: list[str] = []
    for index, match in enumerate(matches, start=1):
        metadata = match["metadata"]
        title = metadata.get("title") or metadata.get("filename") or "Untitled source"
        url = metadata.get("url", "")
        topic = metadata.get("topic", "")
        sections.append(
            f"[Source {index}]\n"
            f"Title: {title}\n"
            f"URL: {url}\n"
            f"Topic: {topic}\n"
            f"Excerpt:\n{match['text']}"
        )
    return "\n\n".join(sections)


def answer_question(question: str, top_k: int = 5) -> dict[str, Any]:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_key_here":
        raise RuntimeError("Set GROQ_API_KEY in .env before running generation.")

    matches = search(question, top_k=top_k)
    context = build_context(matches)

    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Question: {question}\n\nRetrieved excerpts:\n{context}",
            },
        ],
        temperature=0.1,
    )

    return {
        "question": question,
        "answer": completion.choices[0].message.content,
        "matches": matches,
    }
