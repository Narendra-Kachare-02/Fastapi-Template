"""Prompt templates for question classification (medical vs non-medical)."""

CLASSIFICATION_PROMPT_TEMPLATE = """
You are a strict classifier. Decide if the following user question is about
medicine, health, symptoms, diagnoses, treatments, anatomy, physiology,
clinical findings, or SNOMED CT concepts.

Question:
{question}

Respond with EXACTLY one word, either 'medical' or 'non-medical', and nothing else.
"""

