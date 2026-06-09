from __future__ import annotations

import argparse

from generate import answer_question
from retrieve import format_matches, search


def ask_once(question: str, top_k: int, retrieval_only: bool) -> None:
    if retrieval_only:
        print(format_matches(search(question, top_k=top_k)))
        return

    result = answer_question(question, top_k=top_k)
    print("\nAnswer:\n")
    print(result["answer"])
    print("\nRetrieved chunks:\n")
    print(format_matches(result["matches"]))


def interactive(top_k: int, retrieval_only: bool) -> None:
    print("UC Berkeley Housing RAG. Type 'quit' to exit.")
    while True:
        question = input("\nQuestion: ").strip()
        if question.lower() in {"q", "quit", "exit"}:
            break
        if question:
            ask_once(question, top_k=top_k, retrieval_only=retrieval_only)


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the UC Berkeley housing RAG system.")
    parser.add_argument("question", nargs="?", help="Question to ask. Omit for interactive mode.")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--retrieval-only",
        action="store_true",
        help="Show retrieved chunks without calling Groq.",
    )
    args = parser.parse_args()

    if args.question:
        ask_once(args.question, top_k=args.top_k, retrieval_only=args.retrieval_only)
    else:
        interactive(top_k=args.top_k, retrieval_only=args.retrieval_only)


if __name__ == "__main__":
    main()
