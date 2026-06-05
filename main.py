from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.agent import KnowledgeBaseAgent
from src.chunking import RecursiveChunker
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    LocalEmbedder,
    OpenAIEmbedder,
    _mock_embed,
)
from src.models import Document
from src.store import EmbeddingStore


SAMPLE_FILES = [
    "data/python_intro.txt",
    "data/vector_store_notes.md",
    "data/rag_system_design.md",
    "data/customer_support_playbook.txt",
    "data/chunking_experiment_report.md",
    "data/vi_retrieval_notes.md",
]

HANDBOOK_DATA_DIR = Path("data/processed")

BENCHMARK_QUERIES = [
    {
        "query": "Học viên được phép nghỉ tối đa bao nhiêu buổi?",
        "gold": "Học viên được phép nghỉ tối đa 04 buổi, tính theo buổi sáng hoặc buổi chiều, trong giai đoạn 1 và 2 tại VinUni.",
        "expected_category": "attendance_policy",
    },
    {
        "query": "Chương trình có hỗ trợ học online không?",
        "gold": "Chương trình ưu tiên học trực tiếp và không hỗ trợ hình thức học online, trừ khi BTC có thông báo thay đổi.",
        "expected_category": "attendance_policy",
    },
    {
        "query": "Điều kiện để được công nhận hoàn thành chương trình là gì?",
        "gold": "Học viên cần đạt điểm tổng kết từ mức Pass trở lên, hoàn thành các thành phần đánh giá bắt buộc, tham gia đủ thời lượng và không vi phạm nghiêm trọng quy định.",
        "expected_category": "completion_policy",
    },
    {
        "query": "Học viên nhận trợ cấp trong điều kiện nào?",
        "gold": "Học viên cần tuân thủ thỏa thuận, duy trì chuyên cần, hoàn thành yêu cầu học tập/đánh giá, tuân thủ quy định học thuật, kỷ luật, đạo đức nghề nghiệp và bảo mật.",
        "expected_category": "stipend_policy",
    },
    {
        "query": "Học viên cần chuẩn bị laptop cấu hình tối thiểu như thế nào?",
        "gold": "Học viên nên có laptop CPU Intel Core i7 hoặc Apple M2 tương đương trở lên, RAM tối thiểu 16GB, SSD ít nhất 256GB, hệ điều hành Windows/macOS/Linux và mạng ổn định.",
        "expected_category": "faq",
    },
]


def load_documents_from_files(file_paths: list[str]) -> list[Document]:
    """Load documents from file paths for the manual demo."""
    allowed_extensions = {".md", ".txt"}
    documents: list[Document] = []

    for raw_path in file_paths:
        path = Path(raw_path)

        if path.suffix.lower() not in allowed_extensions:
            print(f"Skipping unsupported file type: {path} (allowed: .md, .txt)")
            continue

        if not path.exists() or not path.is_file():
            print(f"Skipping missing file: {path}")
            continue

        content = path.read_text(encoding="utf-8")
        documents.append(
            Document(
                id=path.stem,
                content=content,
                metadata={"source": str(path), "extension": path.suffix.lower()},
            )
        )

    return documents


def parse_frontmatter_markdown(path: Path) -> tuple[dict, str]:
    """
    Parse cleaned handbook markdown files.

    Each processed handbook file has YAML-style metadata at the top.
    This function extracts metadata and returns clean content separately.
    """
    text = path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        metadata = {
            "source": "20K-AI-Handbook-ver2.0-da-nen.pdf",
            "category": path.stem.replace("handbook_", ""),
            "doc_type": "handbook",
            "language": "vi",
            "version": "2.0",
            "section": path.stem,
        }
        return metadata, text.strip()

    parts = text.split("---", 2)
    raw_metadata = parts[1].strip()
    content = parts[2].strip()

    metadata = {}
    for line in raw_metadata.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")

    metadata.setdefault("source", "20K-AI-Handbook-ver2.0-da-nen.pdf")
    metadata.setdefault("category", path.stem.replace("handbook_", ""))
    metadata.setdefault("doc_type", "handbook")
    metadata.setdefault("language", "vi")
    metadata.setdefault("version", "2.0")
    metadata.setdefault("section", path.stem)

    return metadata, content


def load_handbook_chunks(chunk_size: int = 500) -> list[Document]:
    """
    Load cleaned handbook markdown files and split them with RecursiveChunker.

    This is the personal strategy for Nhi:
    RecursiveChunker(chunk_size=500)
    """
    chunker = RecursiveChunker(chunk_size=chunk_size)
    documents: list[Document] = []

    for path in sorted(HANDBOOK_DATA_DIR.glob("handbook_*.md")):
        base_metadata, content = parse_frontmatter_markdown(path)
        chunks = chunker.chunk(content)

        for index, chunk in enumerate(chunks):
            metadata = dict(base_metadata)
            metadata["file"] = path.name
            metadata["chunk_index"] = index
            metadata["chunking_strategy"] = "recursive"
            metadata["chunk_size"] = chunk_size

            documents.append(
                Document(
                    id=f"{path.stem}_chunk_{index}",
                    content=chunk,
                    metadata=metadata,
                )
            )

    return documents


def get_embedder():
    """
    Select embedding backend from .env.

    EMBEDDING_PROVIDER=openai uses OpenAIEmbedder.
    Otherwise, the code falls back to _mock_embed.
    """
    load_dotenv(override=False)

    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()

    if provider == "local":
        try:
            return LocalEmbedder(
                model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL)
            )
        except Exception as exc:
            print(f"Local embedder failed, falling back to mock. Reason: {exc}")
            return _mock_embed

    if provider == "openai":
        try:
            return OpenAIEmbedder(
                model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL)
            )
        except Exception as exc:
            print(f"OpenAI embedder failed, falling back to mock. Reason: {exc}")
            return _mock_embed

    return _mock_embed


def demo_llm(prompt: str) -> str:
    """A simple mock LLM for manual RAG testing."""
    preview = prompt[:400].replace("\n", " ")
    return f"[DEMO LLM] Generated answer from retrieved context preview: {preview}..."


def summarize(text: str, limit: int = 160) -> str:
    clean_text = " ".join(text.split())
    if len(clean_text) <= limit:
        return clean_text
    return clean_text[:limit] + "..."


def run_manual_demo(question: str | None = None, sample_files: list[str] | None = None) -> int:
    files = sample_files or SAMPLE_FILES
    query = question or "Summarize the key information from the loaded files."

    print("=== Manual File Test ===")
    print("Accepted file types: .md, .txt")
    print("Input file list:")
    for file_path in files:
        print(f"  - {file_path}")

    docs = load_documents_from_files(files)
    if not docs:
        print("\nNo valid input files were loaded.")
        print("Create files matching the sample paths above, then rerun:")
        print("  python main.py")
        return 1

    print(f"\nLoaded {len(docs)} documents")
    for doc in docs:
        print(f"  - {doc.id}: {doc.metadata['source']}")

    embedder = get_embedder()
    print(f"\nEmbedding backend: {getattr(embedder, '_backend_name', embedder.__class__.__name__)}")

    store = EmbeddingStore(collection_name="manual_test_store", embedding_fn=embedder)
    store.add_documents(docs)

    print(f"\nStored {store.get_collection_size()} documents in EmbeddingStore")
    print("\n=== EmbeddingStore Search Test ===")
    print(f"Query: {query}")

    search_results = store.search(query, top_k=3)
    for index, result in enumerate(search_results, start=1):
        print(f"{index}. score={result['score']:.3f} source={result['metadata'].get('source')}")
        print(f"   content preview: {result['content'][:120].replace(chr(10), ' ')}...")

    print("\n=== KnowledgeBaseAgent Test ===")
    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)
    print(f"Question: {query}")
    print("Agent answer:")
    print(agent.answer(query, top_k=3))
    return 0


def run_handbook_benchmark() -> int:
    """
    Run Lab 7 group benchmark for Nhi's strategy:
    RecursiveChunker + OpenAI text-embedding-3-small.
    """
    print("=== Lab 7 Handbook Benchmark ===")
    print("Strategy: RecursiveChunker(chunk_size=500)")
    print("Data path: data/processed/handbook_*.md")

    docs = load_handbook_chunks(chunk_size=500)
    if not docs:
        print("No handbook chunks found. Check data/processed/")
        return 1

    embedder = get_embedder()
    backend_name = getattr(embedder, "_backend_name", embedder.__class__.__name__)

    print(f"Embedding backend: {backend_name}")
    print(f"Total chunks indexed: {len(docs)}")

    store = EmbeddingStore(collection_name="handbook_recursive_benchmark", embedding_fn=embedder)
    store.add_documents(docs)

    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

    relevant_top3_count = 0

    for index, benchmark in enumerate(BENCHMARK_QUERIES, start=1):
        query = benchmark["query"]
        expected_category = benchmark["expected_category"]

        results = store.search(query, top_k=3)
        top1 = results[0]
        top3_categories = [item["metadata"].get("category") for item in results]

        relevant_in_top3 = expected_category in top3_categories
        if relevant_in_top3:
            relevant_top3_count += 1

        print()
        print("=" * 80)
        print(f"Query {index}: {query}")
        print(f"Gold answer: {benchmark['gold']}")
        print(f"Expected category: {expected_category}")
        print("-" * 80)

        for rank, result in enumerate(results, start=1):
            metadata = result["metadata"]
            print(
                f"{rank}. score={result['score']:.4f} | "
                f"file={metadata.get('file')} | "
                f"category={metadata.get('category')} | "
                f"chunk={metadata.get('chunk_index')}"
            )
            print(f"   {summarize(result['content'])}")

        print("-" * 80)
        print(f"Top-1 summary: {summarize(top1['content'])}")
        print(f"Top-1 score: {top1['score']:.4f}")
        print(f"Top-3 categories: {top3_categories}")
        print(f"Relevant in top-3? {'YES' if relevant_in_top3 else 'NO'}")
        print(f"Agent answer summary: {agent.answer(query, top_k=3)}")

    print()
    print("=" * 80)
    print(f"Top-3 relevant count: {relevant_top3_count} / {len(BENCHMARK_QUERIES)}")
    print(f"Retrieval score: {relevant_top3_count * 2} / 10")
    print("=" * 80)

    return 0


def main() -> int:
    args = sys.argv[1:]

    if args and args[0] == "--handbook-benchmark":
        return run_handbook_benchmark()

    question = " ".join(args).strip() if args else None
    return run_manual_demo(question=question)


if __name__ == "__main__":
    raise SystemExit(main())