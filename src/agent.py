from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)

        if not results:
            return "Không có thông tin phù hợp trong knowledge base."

        context_blocks = []

        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata", {})
            source = metadata.get("source", metadata.get("doc_id", "unknown"))
            content = result.get("content", "")
            score = result.get("score", 0.0)

            context_blocks.append(
                f"[Source {index}: {source}, score={score:.4f}]\n{content}"
            )

        context = "\n\n---\n\n".join(context_blocks)

        prompt = f"""Dựa trên các nguồn sau, hãy trả lời câu hỏi một cách ngắn gọn và có căn cứ.
Nếu không tìm thấy thông tin trong nguồn, hãy nói rằng không có thông tin.

Nguồn:
{context}

Câu hỏi:
{question}

Câu trả lời:"""

        return self.llm_fn(prompt)