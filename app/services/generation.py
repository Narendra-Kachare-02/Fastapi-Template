"""Generation service: call LLM with context and question."""

from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from app.config import OPENAI_API_KEY, RAG_LLM_MODEL
from app.prompts.rag import RAG_PROMPT_TEMPLATE
from app.utils.logging import get_logger

logger = get_logger(__name__)


def format_docs(docs: list[Any]) -> str:
    """Format retrieved Langchain documents for prompt context."""
    return "\n\n".join(
        f"Concept ID: {d.metadata.get('conceptId', 'N/A')}\n"
        f"Preferred Name: {d.metadata.get('PreferredName', 'N/A')}\n"
        f"Content: {d.page_content}"
        for d in docs
    )


def build_rag_chain():
    """Build the RAG chain (retriever not included; inject in rag.py)."""
    api_key = OPENAI_API_KEY
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set. Set it in .env or config.")
    llm = ChatOpenAI(model=RAG_LLM_MODEL, api_key=api_key)
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    return prompt | llm | StrOutputParser()


def generate(context: str, question: str) -> str:
    """Generate LLM response given context and question."""
    chain = build_rag_chain()
    return chain.invoke({"context": context, "question": question})
