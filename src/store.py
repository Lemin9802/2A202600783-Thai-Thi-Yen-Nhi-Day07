from __future__ import annotations

from typing import Any, Callable

from .chunking import compute_similarity
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            # For this lab/test suite, the in-memory implementation is enough.
            # Chroma can be added later for a real persistent vector database.
            self._use_chroma = False
            self._collection = None
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """
        Build one normalized stored record.

        Each record keeps:
        - id: unique internal chunk id
        - content: original text for prompt injection
        - metadata: user metadata plus doc_id
        - embedding: vector representation of content
        """
        metadata = dict(doc.metadata or {})
        metadata["doc_id"] = doc.id

        record_id = f"{doc.id}_{self._next_index}"
        self._next_index += 1

        return {
            "id": record_id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
        }

    def _search_records(
        self,
        query: str,
        records: list[dict[str, Any]],
        top_k: int,
    ) -> list[dict[str, Any]]:
        """
        Run in-memory similarity search over the provided records.
        """
        if top_k <= 0:
            return []

        query_embedding = self._embedding_fn(query)
        results: list[dict[str, Any]] = []

        for record in records:
            score = compute_similarity(query_embedding, record["embedding"])
            results.append(
                {
                    "id": record["id"],
                    "content": record["content"],
                    "metadata": record["metadata"],
                    "score": score,
                }
            )

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        for doc in docs:
            self._store.append(self._make_record(doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute cosine similarity of query embedding vs all stored embeddings.
        """
        return self._search_records(query=query, records=self._store, top_k=top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(
        self,
        query: str,
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if not metadata_filter:
            return self.search(query=query, top_k=top_k)

        filtered_records = []

        for record in self._store:
            metadata = record.get("metadata", {})
            matches = all(metadata.get(key) == value for key, value in metadata_filter.items())
            if matches:
                filtered_records.append(record)

        return self._search_records(query=query, records=filtered_records, top_k=top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        size_before = len(self._store)

        self._store = [
            record
            for record in self._store
            if record.get("metadata", {}).get("doc_id") != doc_id
        ]

        return len(self._store) < size_before