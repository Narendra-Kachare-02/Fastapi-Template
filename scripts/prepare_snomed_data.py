"""Prepare SNOMED data from raw description/definition TSVs and write final TSV.

Uses the same logic as the Langchain RAG prepare_snomed_data.py.
Reads: data/snomed_description.txt, data/snomed_definition.txt (or paths you pass).
Writes: data/snomed_final.txt (or path you pass).

Usage:
  uv run python scripts/prepare_snomed_data.py
  uv run python scripts/prepare_snomed_data.py --description data/desc.txt --definition data/def.txt --output data/snomed_final.txt
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

# Project root so paths work from repo root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def optimize_snomed_processing(
    description_path: Path,
    definition_path: Path,
) -> pd.DataFrame:
    """
    Optimized SNOMED CT data processing (from Langchain RAG prepare_snomed_data.py).
    Returns merged DataFrame with conceptId, PreferredName, term (list), Description (list).
    """
    dtype_dict = {
        "conceptId": "string",
        "active": "category",
        "typeId": "category",
        "term": "string",
    }
    desc_cols = ["conceptId", "active", "typeId", "term"]

    print("Loading description data...")
    description = pd.read_csv(
        description_path,
        sep="\t",
        dtype=dtype_dict,
        usecols=desc_cols,
        engine="c",
    )
    print(f"Description rows before filtering: {len(description):,}")

    active_mask = description["active"] == "1"
    description_active = description[active_mask].copy()
    print(f"Description rows after filtering: {len(description_active):,}")

    preferred_mask = description_active["typeId"] == "900000000000003001"
    synonym_mask = description_active["typeId"] == "900000000000013009"

    preferred = (
        description_active[preferred_mask][["conceptId", "term"]]
        .rename(columns={"term": "PreferredName"})
        .drop_duplicates(subset=["conceptId"])
        .reset_index(drop=True)
    )
    print(f"Preferred names: {len(preferred):,}")

    synonyms_data = description_active[synonym_mask][["conceptId", "term"]].drop_duplicates()
    if not synonyms_data.empty:
        synonyms = (
            synonyms_data.groupby("conceptId", as_index=False)
            .agg({"term": list})
            .rename(columns={"term": "term"})
        )
        print(f"Synonyms grouped: {len(synonyms):,}")
    else:
        synonyms = pd.DataFrame(columns=["conceptId", "term"])
        print("No synonyms found")

    if not synonyms.empty:
        merged = pd.merge(preferred, synonyms, on="conceptId", how="inner")
    else:
        merged = preferred.copy()
        merged["term"] = pd.Series(dtype=object)
    print(f"Merged preferred + synonyms: {len(merged):,}")

    def_dtype_dict = {
        "conceptId": "string",
        "active": "category",
        "term": "string",
    }
    def_cols = ["conceptId", "active", "term"]
    print("Loading definition data...")
    definition = pd.read_csv(
        definition_path,
        sep="\t",
        dtype=def_dtype_dict,
        usecols=def_cols,
        engine="c",
    )
    print(f"Definition rows before filtering: {len(definition):,}")

    definition_filtered = (
        definition[definition["active"] == "1"][["conceptId", "term"]]
        .drop_duplicates()
        .groupby("conceptId", as_index=False)
        .agg({"term": list})
        .rename(columns={"term": "Description"})
        .reset_index(drop=True)
    )
    print(f"Definition after filtering: {len(definition_filtered):,}")

    final = pd.merge(merged, definition_filtered, on="conceptId", how="inner")
    print(f"Final merged data: {len(final):,}")
    return final


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare SNOMED final TSV from description and definition files.")
    parser.add_argument(
        "--description",
        type=Path,
        default=PROJECT_ROOT / "data" / "snomed_description.txt",
        help="Path to snomed_description.txt (TSV)",
    )
    parser.add_argument(
        "--definition",
        type=Path,
        default=PROJECT_ROOT / "data" / "snomed_definition.txt",
        help="Path to snomed_definition.txt (TSV)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "snomed_final.txt",
        help="Path to write final TSV (snomed_final.txt)",
    )
    args = parser.parse_args()

    if not args.description.exists():
        print(f"Description file not found: {args.description}")
        sys.exit(1)
    if not args.definition.exists():
        print(f"Definition file not found: {args.definition}")
        sys.exit(1)

    final_data = optimize_snomed_processing(args.description, args.definition)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    final_data.to_csv(args.output, sep="\t", index=False)
    print(f"Wrote final TSV: {args.output}")


if __name__ == "__main__":
    main()
