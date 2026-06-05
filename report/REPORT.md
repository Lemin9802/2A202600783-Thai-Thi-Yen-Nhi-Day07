# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Thái Thị Yến Nhi  
**Mã học viên:** 2A202600783  
**Nhóm:** 066  
**Ngày:** 05/06/2026  

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**  
High cosine similarity nghĩa là hai vector có hướng gần giống nhau trong không gian embedding. Với text embeddings, điều này thường cho thấy hai câu hoặc hai đoạn văn có ý nghĩa gần nhau, dù có thể không dùng chính xác cùng từ khóa.

**Ví dụ HIGH similarity:**
- Sentence A: Học viên được phép nghỉ tối đa 4 buổi trong chương trình.
- Sentence B: Quy định chuyên cần cho phép học viên vắng tối đa bốn buổi.
- Tại sao tương đồng: Hai câu cùng nói về giới hạn số buổi được nghỉ của học viên trong chương trình.

**Ví dụ LOW similarity:**
- Sentence A: Học viên được nhận trợ cấp 8 triệu đồng mỗi tháng.
- Sentence B: Vector store lưu embeddings để phục vụ semantic search.
- Tại sao khác: Hai câu thuộc hai chủ đề khác nhau; một câu nói về chính sách trợ cấp, câu còn lại nói về kỹ thuật vector store.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**  
Cosine similarity tập trung vào hướng của vector, nên phù hợp để đo mức độ gần nghĩa giữa các văn bản. Euclidean distance phụ thuộc nhiều hơn vào khoảng cách tuyệt đối và độ lớn vector, trong khi với text embeddings thì hướng biểu diễn ý nghĩa thường quan trọng hơn.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**  
Step size = chunk_size - overlap = 500 - 50 = 450.

Công thức:
`number_of_chunks = ceil((document_length - chunk_size) / step_size) + 1`

Thay số:
`ceil((10000 - 500) / 450) + 1 = ceil(9500 / 450) + 1 = 22 + 1 = 23`

**Đáp án:** 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**  
Khi overlap tăng lên 100, step size = 500 - 100 = 400.

`ceil((10000 - 500) / 400) + 1 = ceil(9500 / 400) + 1 = 24 + 1 = 25`

Vậy số chunk tăng từ 23 lên 25. Overlap nhiều hơn giúp giữ ngữ cảnh ở phần ranh giới giữa hai chunk, tránh mất ý khi một câu hoặc một đoạn bị chia cắt. Tuy nhiên overlap quá nhiều sẽ tạo nhiều nội dung trùng lặp hơn, tốn storage hơn và có thể làm retrieval bị nhiễu.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** [ví dụ: Customer support FAQ, Vietnamese law, cooking recipes, ...]

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:*

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Strategy Của Tôi

**Loại:** [FixedSizeChunker / SentenceChunker / RecursiveChunker / custom strategy]

**Mô tả cách hoạt động:**
> *Viết 3-4 câu: strategy chunk thế nào? Dựa trên dấu hiệu gì?*

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Viết 2-3 câu: domain có pattern gì mà strategy khai thác?*

**Code snippet (nếu custom):**
```python
# Paste implementation here
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| | best baseline | | | |
| | **của tôi** | | | |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | | | | |
| [Tên] | | | | |
| [Tên] | | | | |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> *Viết 2-3 câu:*

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:  
Tôi dùng regex `(?<=[.!?])\s+` để tách văn bản tại khoảng trắng đứng sau dấu chấm, dấu chấm than hoặc dấu hỏi. Sau khi tách, tôi loại bỏ khoảng trắng thừa và bỏ các câu rỗng. Các câu sau đó được gom lại theo `max_sentences_per_chunk` để mỗi chunk chứa tối đa số câu được cấu hình.

**`RecursiveChunker.chunk` / `_split`** — approach:  
Tôi implement recursive chunking bằng cách thử các separator theo thứ tự từ lớn đến nhỏ: `\n\n`, `\n`, `. `, ` `, và cuối cùng là chuỗi rỗng `""`. Nếu đoạn hiện tại đã ngắn hơn hoặc bằng `chunk_size`, hàm trả về đoạn đó ngay. Nếu đoạn vẫn quá dài, thuật toán tiếp tục tách bằng separator tiếp theo; trường hợp cuối cùng thì cắt theo ký tự để đảm bảo không bị lỗi.

### EmbeddingStore

**`add_documents` + `search`** — approach:  
Tôi dùng in-memory list để lưu vector store. Mỗi record gồm `id`, `content`, `metadata` và `embedding`. Khi thêm document, store gọi embedding function để tạo vector từ `doc.content`; khi search, query cũng được embed rồi so sánh với từng document bằng cosine similarity, sau đó sort theo score giảm dần và trả về top-k kết quả.

**`search_with_filter` + `delete_document`** — approach:  
Với `search_with_filter`, tôi lọc metadata trước rồi mới chạy similarity search trên các record còn lại. Cách này giúp giới hạn không gian tìm kiếm theo metadata như category, department hoặc language. Với `delete_document`, tôi xóa tất cả record có `metadata["doc_id"]` trùng với document id cần xóa và trả về `True` nếu có ít nhất một record bị xóa.

### KnowledgeBaseAgent

**`answer`** — approach:  
Agent nhận câu hỏi, gọi `store.search(question, top_k)` để lấy các chunks liên quan nhất, rồi ghép nội dung retrieved được thành context. Prompt được xây theo cấu trúc gồm phần nguồn, câu hỏi và yêu cầu trả lời dựa trên nguồn. Cuối cùng agent gọi `llm_fn(prompt)` để sinh câu trả lời dựa trên retrieved context thay vì trả lời không có dữ liệu.

### Test Results

```text
pytest tests/ -v

collected 42 items

42 passed in 0.06s
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | high / low | | |
| 2 | | | high / low | | |
| 3 | | | high / low | | |
| 4 | | | high / low | | |
| 5 | | | high / low | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:*

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu queries trả về chunk relevant trong top-3?** __ / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:*

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | / 5 |
| Document selection | Nhóm | / 10 |
| Chunking strategy | Nhóm | / 15 |
| My approach | Cá nhân | / 10 |
| Similarity predictions | Cá nhân | / 5 |
| Results | Cá nhân | / 10 |
| Core implementation (tests) | Cá nhân | / 30 |
| Demo | Nhóm | / 5 |
| **Tổng** | | **/ 100** |
