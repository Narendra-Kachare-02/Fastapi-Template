"""Question classification service: medical vs non-medical."""

from langchain_openai import ChatOpenAI

from app.config import OPENAI_API_KEY, RAG_LLM_MODEL
from app.prompts.classification import CLASSIFICATION_PROMPT_TEMPLATE
from app.utils.logging import get_logger

logger = get_logger(__name__)


def is_medical_question(question: str) -> bool:
    """Return True if the question is medical/SNOMED-related, else False.

    If classification fails or LLM is not configured, default to True so the
    main RAG flow still works.
    """
    api_key = OPENAI_API_KEY
    if not api_key:
        logger.warning("OPENAI_API_KEY not set; skipping medical/non-medical classification.")
        return True

    classifier = ChatOpenAI(model=RAG_LLM_MODEL, api_key=api_key)
    prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(question=question)
    try:
        result = classifier.invoke(prompt)
        content = result.content.strip().lower()
        return "medical" in content and "non-medical" not in content
    except Exception as e:
        logger.warning("Failed to classify question as medical/non-medical: %s", e)
        return True

