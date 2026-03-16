"""RAG pipeline service: combine retrieval, classification, and generation."""

import json

from app.services import classification, generation, retrieval
from app.utils.logging import get_logger

logger = get_logger(__name__)


def search(query: str, top_k: int | None = None) -> dict:
    """Full RAG pipeline: classify, then retrieve context, then generate LLM response.

    Returns dict with:
    - answer: JSON string from LLM (or fixed JSON for non-medical questions)
    - retrieved: list of SNOMED concepts (empty for non-medical questions)
    - context_used: raw context used when LLM is unavailable
    """
    # 1) First decide if the question is medical/SNOMED-related.
    is_medical = classification.is_medical_question(query)
    if not is_medical:
        fixed_answer = {
            "description": (
                "This question is not related to medical terms, so I cannot answer it. "
                "This information is not a diagnosis or medical advice. "
                "Please talk to a qualified doctor or other healthcare professional for a proper evaluation."
            ),
            "snomed_concepts": [],
        }
        return {
            "answer": json.dumps(fixed_answer),
            "retrieved": [],
            "context_used": None,
        }

    # 2) Normal RAG flow for medical questions.
    docs = retrieval.retrieve(query=query, top_k=top_k)
    context = generation.format_docs(docs)
    try:
        answer = generation.generate(context=context, question=query)
    except ValueError as e:
        logger.warning("LLM not available: %s. Returning retrieved docs only.", e)
        answer = None

    snomed_concepts = []
    for d in docs:
        raw_concept_id = d.metadata.get("conceptId")
        concept_id_str = str(raw_concept_id) if raw_concept_id is not None else None
        snomed_concepts.append(
            {
                "conceptId": concept_id_str,
                "PreferredName": d.metadata.get("PreferredName"),
            }
        )

    return {
        "answer": answer,
        "retrieved": snomed_concepts,
        "context_used": context if not answer else None,
    }
