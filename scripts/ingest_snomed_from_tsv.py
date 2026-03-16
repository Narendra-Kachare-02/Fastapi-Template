"""Ingest SNOMED data from TSV (snomed_final.txt) into pgvector.

Usage:
  uv run python scripts/ingest_snomed_from_tsv.py [path_to_tsv]
  uv run python scripts/ingest_snomed_from_tsv.py --limit 10          # test with 10 docs (quick)
  uv run python scripts/ingest_snomed_from_tsv.py --batch-size 100 --workers 10  # 10 parallel workers

TSV format: tab-separated with conceptId, PreferredName, term (repr list), Description (repr list).
Produced e.g. by prepare_snomed_data.py.
"""

import argparse
import ast
import sys
from pathlib import Path

import pandas as pd
from langchain_core.documents import Document

# Add project root so app is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.ingestion import ingest_documents, ingest_documents_parallel  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest SNOMED TSV into pgvector (BGE embeddings).")
    parser.add_argument(
        "tsv_path",
        nargs="?",
        default="data/snomed_final.txt",
        help="Path to snomed_final.txt (default: data/snomed_final.txt)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Ingest only first N documents (default: 0 = all). Use e.g. 10 to test BGE + DB quickly.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Documents per batch (default: 100). With --workers, each worker processes one batch.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of parallel workers (default: 10). Each worker embeds one batch and writes; main waits for all.",
    )
    args = parser.parse_args()

    tsv_path = Path(args.tsv_path)
    if not tsv_path.exists():
        print(f"TSV not found: {tsv_path}")
        sys.exit(1)

    print("Loading TSV...")
    df = pd.read_csv(tsv_path, sep="\t")
    if args.limit > 0:
        df = df.head(args.limit)
        print(f"Limited to first {len(df)} documents (--limit {args.limit}).")
    df["term"] = df["term"].apply(ast.literal_eval)
    df["Description"] = df["Description"].apply(ast.literal_eval)
    df["content"] = df.apply(
        lambda row: f"{row['PreferredName']}. {'; '.join(row['term'])}. {' '.join(row['Description'])}",
        axis=1,
    )
    documents = [
        Document(
            page_content=row["content"],
            metadata={"conceptId": row["conceptId"], "PreferredName": row["PreferredName"]},
        )
        for _, row in df.iterrows()
    ]
    total = len(documents)
    def progress(done: int, total_docs: int) -> None:
        print(f"  ... {done}/{total_docs} docs ingested", flush=True)

    if args.workers <= 1:
        print(f"Loaded {total} documents. Starting BGE embedding + pgvector ingest (batch_size={args.batch_size})...")
        count = ingest_documents(
            documents=documents,
            batch_size=args.batch_size,
            progress_callback=progress,
        )
    else:
        print(
            f"Loaded {total} documents. Starting parallel ingest: {args.workers} workers, "
            f"batch_size={args.batch_size} (workers do not wait for each other; main waits for all)..."
        )
        count = ingest_documents_parallel(
            documents=documents,
            batch_size=args.batch_size,
            num_workers=args.workers,
            progress_callback=progress,
        )
    print(f"Done. Ingested {count} documents into pgvector.")


if __name__ == "__main__":
    main()
