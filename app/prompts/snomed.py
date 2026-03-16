"""SNOMED-specific prompt fragments (for ingestion or search UX)."""

SNOMED_SEARCH_SYSTEM = (
    "You are a medical concept search assistant. Use SNOMED CT context to match user queries to concepts."
)

SNOMED_INGEST_SUMMARY = (
    "Document contains SNOMED CT concepts: PreferredName, synonyms (term), and definitions (Description)."
)
