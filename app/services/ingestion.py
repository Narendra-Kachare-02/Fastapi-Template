"""Ingestion service: store documents in vector store (embed and upload to pgvector)."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from typing import Callable

from langchain_core.documents import Document

from app.repositories import vector as vector_repository
from app.services.embedding import get_embedding_model
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Default batch size for progress logging (BGE encodes this many at a time per log line)
DEFAULT_INGEST_BATCH_SIZE = 100
# Default number of worker threads for parallel ingest
DEFAULT_INGEST_WORKERS = 10


def ingest_documents(
    documents: list[Document],
    batch_size: int = DEFAULT_INGEST_BATCH_SIZE,
    progress_callback: Callable[[int, int], None] | None = None,
) -> int:
    """Ingest documents into pgvector (create collection and add documents). Returns count ingested.

    If batch_size > 0, processes in batches and logs progress (and calls progress_callback if set).
    """
    if not documents:
        return 0
    embedding = get_embedding_model()
    total = len(documents)
    if batch_size <= 0:
        vector_repository.create_collection_from_documents(documents=documents, embedding=embedding)
        logger.info("Ingestion complete: %s documents", total)
        if progress_callback:
            progress_callback(total, total)
        return total
    ingested = 0
    for start in range(0, total, batch_size):
        batch = documents[start : start + batch_size]
        batch_num = (start // batch_size) + 1
        num_batches = (total + batch_size - 1) // batch_size
        logger.info(
            "BGE embedding + pgvector: batch %s/%s (docs %s-%s of %s)",
            batch_num,
            num_batches,
            start + 1,
            min(start + batch_size, total),
            total,
        )
        if ingested == 0:
            vector_repository.create_collection_from_documents(documents=batch, embedding=embedding)
        else:
            vector_repository.add_documents_to_store(documents=batch, embedding=embedding)
        ingested += len(batch)
        if progress_callback:
            progress_callback(ingested, total)
    logger.info("Ingestion complete: %s documents", ingested)
    return ingested


def ingest_documents_append(
    documents: list[Document],
    batch_size: int = DEFAULT_INGEST_BATCH_SIZE,
) -> int:
    """Append documents to existing vector store. Use when collection already exists."""
    if not documents:
        return 0
    embedding = get_embedding_model()
    vector_repository.add_documents_to_store(documents=documents, embedding=embedding)
    return len(documents)


def _embed_and_add_batch(
    batch: list[Document],
    batch_num: int,
    num_batches: int,
    embedding,
    store,  # shared PGVector store (single connection pool)
    progress_callback: Callable[[int, int], None] | None,
    total: int,
    done_lock: Lock,
    done_count: list[int],
) -> int:
    """Worker task: embed one batch and add to store. Updates done_count and calls progress_callback."""
    n = len(batch)
    logger.info("Batch %s/%s: embedding %s docs...", batch_num, num_batches, n)
    texts = [d.page_content for d in batch]
    metadatas = [d.metadata for d in batch]
    embeddings = embedding.embed_documents(texts)
    store.add_embeddings(
        texts=texts,
        embeddings=list(embeddings),
        metadatas=metadatas,
    )
    with done_lock:
        done_count[0] += n
        if progress_callback:
            progress_callback(done_count[0], total)
    logger.info("Batch %s/%s done (%s docs, total so far: %s/%s)", batch_num, num_batches, n, done_count[0], total)
    return n


def ingest_documents_parallel(
    documents: list[Document],
    batch_size: int = DEFAULT_INGEST_BATCH_SIZE,
    num_workers: int = DEFAULT_INGEST_WORKERS,
    progress_callback: Callable[[int, int], None] | None = None,
) -> int:
    """Ingest documents using multiple workers. Each worker embeds one batch and writes to pgvector.
    Workers run in parallel (do not wait for previous batch to finish before starting next).
    Main thread waits for all workers to finish before returning.
    """
    if not documents:
        return 0
    embedding = get_embedding_model()
    # Single shared store = single connection pool (avoids "too many clients" from Postgres)
    store = vector_repository.get_vector_store(embedding)
    total = len(documents)
    batches = [
        documents[start : start + batch_size]
        for start in range(0, total, batch_size)
    ]
    done_count: list[int] = [0]
    done_lock = Lock()
    logger.info(
        "Parallel ingest: %s docs in %s batches, %s workers (shared store)",
        total,
        len(batches),
        num_workers,
    )
    num_batches = len(batches)
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(
                _embed_and_add_batch,
                batch,
                i + 1,
                num_batches,
                embedding,
                store,
                progress_callback,
                total,
                done_lock,
                done_count,
            ): i
            for i, batch in enumerate(batches)
        }
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.exception("Worker failed: %s", e)
                raise
    logger.info("Ingestion complete: %s documents", done_count[0])
    return done_count[0]
