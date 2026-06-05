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

**Domain:** AI Handbook / policy / FAQ cho chương trình 20K AI.

**Tại sao nhóm chọn domain này?**  
Nhóm chọn bộ dữ liệu handbook vì đây là knowledge data dạng policy/FAQ rất phù hợp để kiểm thử semantic search, metadata filtering và RAG answer function. Nội dung có nhiều loại câu hỏi thực tế như chuyên cần, học online, điều kiện hoàn thành, trợ cấp, laptop và liên hệ, nên dễ thiết kế benchmark queries có gold answer rõ ràng. Dataset cũng có cấu trúc theo section, heading và bullet list, phù hợp để so sánh các chunking strategies như FixedSizeChunker, SentenceChunker và RecursiveChunker.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | `handbook_overview.md` | 20K-AI-Handbook-ver2.0-da-nen.pdf | 1402 | category=overview, doc_type=handbook, language=vi, version=2.0, section=tong_quan_chuong_trinh |
| 2 | `handbook_program_structure.md` | 20K-AI-Handbook-ver2.0-da-nen.pdf | 1571 | category=program_structure, doc_type=handbook, language=vi, version=2.0, section=cau_truc_chuong_trinh |
| 3 | `handbook_schedule.md` | 20K-AI-Handbook-ver2.0-da-nen.pdf | 1271 | category=schedule, doc_type=handbook, language=vi, version=2.0, section=thoi_khoa_bieu |
| 4 | `handbook_assessment_lms.md` | 20K-AI-Handbook-ver2.0-da-nen.pdf | 1100 | category=assessment, doc_type=handbook, language=vi, version=2.0, section=danh_gia_va_lms |
| 5 | `handbook_facilities.md` | 20K-AI-Handbook-ver2.0-da-nen.pdf | 1709 | category=facilities, doc_type=handbook, language=vi, version=2.0, section=dich_vu_tien_ich |
| 6 | `handbook_attendance_policy.md` | 20K-AI-Handbook-ver2.0-da-nen.pdf | 870 | category=attendance_policy, doc_type=handbook, language=vi, version=2.0, section=quy_dinh_chuyen_can |
| 7 | `handbook_deferral_policy.md` | 20K-AI-Handbook-ver2.0-da-nen.pdf | 1373 | category=deferral_policy, doc_type=handbook, language=vi, version=2.0, section=bao_luu_ket_qua_hoc_tap |
| 8 | `handbook_completion_policy.md` | 20K-AI-Handbook-ver2.0-da-nen.pdf | 1171 | category=completion_policy, doc_type=handbook, language=vi, version=2.0, section=dieu_kien_cong_nhan_hoan_thanh |
| 9 | `handbook_stipend_policy.md` | 20K-AI-Handbook-ver2.0-da-nen.pdf | 1331 | category=stipend_policy, doc_type=handbook, language=vi, version=2.0, section=chinh_sach_tro_cap |
| 10 | `handbook_faq.md` | 20K-AI-Handbook-ver2.0-da-nen.pdf | 3092 | category=faq, doc_type=handbook, language=vi, version=2.0, section=cau_hoi_thuong_gap |
| 11 | `handbook_career.md` | 20K-AI-Handbook-ver2.0-da-nen.pdf | 1073 | category=career, doc_type=handbook, language=vi, version=2.0, section=co_hoi_nghe_nghiep |
| 12 | `handbook_contact.md` | 20K-AI-Handbook-ver2.0-da-nen.pdf | 693 | category=contact, doc_type=handbook, language=vi, version=2.0, section=lien_he |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| source | string | 20K-AI-Handbook-ver2.0-da-nen.pdf | Cho biết tài liệu gốc để trace lại nguồn thông tin. |
| category | string | attendance_policy, stipend_policy, faq, schedule | Dùng để filter theo loại nội dung, ví dụ chỉ tìm trong policy hoặc FAQ. |
| doc_type | string | handbook | Phân biệt handbook với các loại dữ liệu khác nếu knowledge base mở rộng. |
| language | string | vi | Hữu ích khi hệ thống có dữ liệu đa ngôn ngữ. |
| version | string | 2.0 | Giúp kiểm soát phiên bản tài liệu và tránh lấy nhầm chính sách cũ. |
| section | string | quy_dinh_chuyen_can | Chỉ rõ section cụ thể để giải thích hoặc dẫn nguồn khi agent trả lời. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu handbook với `chunk_size=500`:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| handbook_attendance_policy.md | FixedSizeChunker (`fixed_size`) | 2 | 460.0 | Trung bình: giữ overlap nhưng có thể cắt ngang heading/câu. |
| handbook_attendance_policy.md | SentenceChunker (`by_sentences`) | 2 | 432.5 | Tốt: giữ câu hoàn chỉnh. |
| handbook_attendance_policy.md | RecursiveChunker (`recursive`) | 3 | 288.3 | Tốt: ưu tiên tách theo đoạn/section. |
| handbook_completion_policy.md | FixedSizeChunker (`fixed_size`) | 3 | 423.7 | Trung bình: chunk đủ dài nhưng có thể lẫn nhiều ý. |
| handbook_completion_policy.md | SentenceChunker (`by_sentences`) | 4 | 291.0 | Tốt: câu rõ nhưng chunk nhỏ hơn. |
| handbook_completion_policy.md | RecursiveChunker (`recursive`) | 3 | 388.7 | Tốt: cân bằng giữa độ dài và ranh giới nội dung. |
| handbook_faq.md | FixedSizeChunker (`fixed_size`) | 7 | 484.6 | Trung bình: phù hợp size nhưng có thể cắt giữa Q&A. |
| handbook_faq.md | SentenceChunker (`by_sentences`) | 15 | 203.3 | Khá tốt: câu rõ, nhưng Q&A có thể bị tách nhỏ. |
| handbook_faq.md | RecursiveChunker (`recursive`) | 8 | 384.6 | Tốt nhất cho FAQ vì ưu tiên heading và đoạn. |

### Strategy Của Tôi

**Loại:** RecursiveChunker (`chunk_size=500`)

**Mô tả cách hoạt động:**  
Strategy của tôi dùng `RecursiveChunker` để chia văn bản theo thứ tự separator từ lớn đến nhỏ: đoạn văn (`\n\n`), dòng (`\n`), câu (`. `), từ (` `), và cuối cùng mới cắt theo ký tự nếu cần. Cách này ưu tiên giữ cấu trúc tự nhiên của tài liệu, thay vì cắt cứng theo số ký tự. Với mỗi file handbook, tôi chunk nội dung thành các đoạn nhỏ, sau đó lưu từng chunk vào `EmbeddingStore` cùng metadata như `source`, `category`, `section`, `file`, `chunk_index`.

**Tại sao tôi chọn strategy này cho domain nhóm?**  
Dataset handbook có cấu trúc rõ theo heading, section, đoạn văn và bullet list. Vì vậy `RecursiveChunker` phù hợp hơn fixed-size chunking vì nó cố gắng giữ các section hoặc đoạn liên quan trong cùng một chunk. Điều này đặc biệt hữu ích với các nội dung như quy định chuyên cần, điều kiện hoàn thành, trợ cấp và FAQ, vì các câu trả lời thường nằm trong cùng một section.

**Code snippet (nếu custom):**
```python
from src import RecursiveChunker

chunker = RecursiveChunker(chunk_size=500)
chunks = chunker.chunk(document_text)
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| handbook_attendance_policy.md | FixedSizeChunker baseline | 2 | 460.0 | Ít chunk, context rộng, nhưng có thể cắt ngang heading/câu. |
| handbook_attendance_policy.md | SentenceChunker baseline | 2 | 432.5 | Giữ câu hoàn chỉnh nhưng chunk dài, có thể gom nhiều ý. |
| handbook_attendance_policy.md | **của tôi: RecursiveChunker** | 3 | 288.3 | Giữ section/đoạn tốt hơn, phù hợp hỏi về chuyên cần. |
| handbook_completion_policy.md | FixedSizeChunker baseline | 3 | 423.7 | Bao phủ tốt nhưng có thể trộn nhiều điều kiện trong một chunk. |
| handbook_completion_policy.md | SentenceChunker baseline | 4 | 291.0 | Giữ câu rõ, nhưng có thể tách các bullet điều kiện. |
| handbook_completion_policy.md | **của tôi: RecursiveChunker** | 3 | 388.7 | Cân bằng giữa độ dài và cấu trúc section, retrieve tốt điều kiện hoàn thành. |
| handbook_faq.md | FixedSizeChunker baseline | 7 | 484.6 | Số chunk ít, nhưng có nguy cơ cắt giữa câu hỏi và câu trả lời. |
| handbook_faq.md | SentenceChunker baseline | 15 | 203.3 | Câu rõ nhưng FAQ bị tách nhỏ, dễ mất cặp hỏi-đáp. |
| handbook_faq.md | **của tôi: RecursiveChunker** | 8 | 384.6 | Phù hợp nhất với FAQ vì ưu tiên heading, đoạn và cấu trúc hỏi-đáp. |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nhi | RecursiveChunker, `chunk_size=500`, OpenAI `text-embedding-3-small` | 10/10 theo top-3 relevant | Giữ heading/section tốt, phù hợp handbook có cấu trúc đoạn và FAQ; top-3 có relevant chunk cho 5/5 queries. | Một số query vẫn cần top-2 để có đủ chi tiết, ví dụ query laptop top-2 mới chứa cấu hình CPU/RAM/SSD. |
| Huy | FixedSizeChunker, `chunk_size=500`, `overlap=50`, OpenAI `text-embedding-3-small` | 10/10 theo top-3 relevant | Đơn giản, có overlap, chunk đủ dài nên nhiều query vẫn retrieve đúng trong top-3. | Có nguy cơ cắt ngang heading/Q&A; một số query top-1 chưa đúng nhất dù top-3 có relevant chunk. |
| Nghĩa | SentenceChunker, `max_sentences_per_chunk=3`, OpenAI `text-embedding-3-small` | 6-8/10 tùy strict/partial relevance | Giữ câu hoàn chỉnh, dễ đọc, phù hợp policy viết theo câu rõ ràng. | Có thể tách câu hỏi và câu trả lời hoặc tách bullet list thành các chunk khác nhau; query laptop bị ảnh hưởng rõ. |

**Strategy nào tốt nhất cho domain này? Tại sao?**  
Với dataset handbook, `RecursiveChunker` phù hợp nhất vì tài liệu có nhiều heading, section, paragraph và bullet list. Strategy này giữ cấu trúc tự nhiên của tài liệu tốt hơn fixed-size chunking và ít làm tách rời ý hơn sentence chunking trong các phần FAQ hoặc danh sách điều kiện. Tuy nhiên, kết quả cũng cho thấy embedding backend rất quan trọng: khi dùng OpenAI `text-embedding-3-small`, cả FixedSizeChunker và RecursiveChunker đều đạt top-3 relevant 5/5.

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

Các điểm actual được tính bằng `compute_similarity(_mock_embed(sentence_a), _mock_embed(sentence_b))`. Mục này dùng `_mock_embed` để kiểm tra logic cosine similarity và quan sát hành vi của mock embedding trong môi trường test. Vì `_mock_embed` là embedding giả lập deterministic, điểm số không nhất thiết phản ánh semantic similarity thật.

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python is a programming language. | Python is used to write software applications. | high | 0.0799 | Một phần |
| 2 | Vector databases store embeddings for similarity search. | A vector store retrieves documents using embedding similarity. | high | 0.1639 | Một phần |
| 3 | Customer support agents answer product questions. | The recipe needs fresh tomatoes and basil. | low | -0.0469 | Đúng |
| 4 | A refund policy explains when customers can get money back. | Return rules describe how buyers can receive refunds. | high | -0.2276 | Sai |
| 5 | Neural networks learn patterns from data. | The train arrived at the station at noon. | low | -0.0593 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**  
Pair 4 bất ngờ nhất vì hai câu gần nghĩa nhưng điểm actual lại âm. Nguyên nhân là phần này dùng `_mock_embed`, embedding giả lập deterministic bằng hash nên không thật sự hiểu ngữ nghĩa. Điều này cho thấy cosine similarity chỉ phản ánh semantic similarity tốt khi embedding model được dùng cũng biểu diễn semantic meaning tốt.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Học viên được phép nghỉ tối đa bao nhiêu buổi? | Học viên được phép nghỉ tối đa 04 buổi, tính theo buổi sáng hoặc buổi chiều, trong giai đoạn 1 và 2 tại VinUni. |
| 2 | Chương trình có hỗ trợ học online không? | Chương trình ưu tiên học trực tiếp và không hỗ trợ hình thức học online, trừ khi BTC có thông báo thay đổi. |
| 3 | Điều kiện để được công nhận hoàn thành chương trình là gì? | Học viên cần đạt điểm tổng kết từ mức Pass trở lên, hoàn thành các thành phần đánh giá bắt buộc, tham gia đủ thời lượng và không vi phạm nghiêm trọng quy định. |
| 4 | Học viên nhận trợ cấp trong điều kiện nào? | Học viên cần tuân thủ thỏa thuận, duy trì chuyên cần, hoàn thành yêu cầu học tập/đánh giá, tuân thủ quy định học thuật, kỷ luật, đạo đức nghề nghiệp và bảo mật. |
| 5 | Học viên cần chuẩn bị laptop cấu hình tối thiểu như thế nào? | Học viên nên có laptop CPU Intel Core i7 hoặc Apple M2 tương đương trở lên, RAM tối thiểu 16GB, SSD ít nhất 256GB, hệ điều hành Windows/macOS/Linux và mạng ổn định. |

### Kết Quả Của Tôi

Benchmark dưới đây dùng strategy cá nhân `RecursiveChunker(chunk_size=500)` trên 42 chunks từ `data/processed/`. Khác với phần Similarity Predictions dùng `_mock_embed`, phần retrieval benchmark này dùng OpenAI `text-embedding-3-small` để đánh giá semantic search thực tế và đồng bộ với kết quả benchmark của các thành viên trong nhóm.

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Học viên được phép nghỉ tối đa bao nhiêu buổi? | Top-1 thuộc `handbook_attendance_policy.md`, chứa quy định học viên được nghỉ tối đa 4 buổi trong giai đoạn 1 và 2. | 0.6340 | Có | Học viên được phép nghỉ tối đa 4 buổi, tính theo buổi sáng hoặc buổi chiều. |
| 2 | Chương trình có hỗ trợ học online không? | Top-1 thuộc `handbook_attendance_policy.md`, nêu rõ chương trình ưu tiên học trực tiếp và không hỗ trợ học online. | 0.6891 | Có | Chương trình không hỗ trợ hình thức học online; học viên học trực tiếp theo kế hoạch, trừ khi BTC thông báo thay đổi. |
| 3 | Điều kiện để được công nhận hoàn thành chương trình là gì? | Top-1 thuộc `handbook_completion_policy.md`, chứa section điều kiện công nhận hoàn thành chương trình. | 0.8099 | Có | Học viên cần đạt mức Pass trở lên, hoàn thành các đánh giá bắt buộc, tham gia đủ thời lượng và không vi phạm nghiêm trọng. |
| 4 | Học viên nhận trợ cấp trong điều kiện nào? | Top-1 thuộc `handbook_stipend_policy.md`, chứa chính sách trợ cấp và điều kiện liên quan. | 0.6384 | Có | Học viên cần tuân thủ thỏa thuận, duy trì chuyên cần, hoàn thành yêu cầu học tập/đánh giá và không vi phạm kỷ luật/bảo mật. |
| 5 | Học viên cần chuẩn bị laptop cấu hình tối thiểu như thế nào? | Top-1 thuộc `handbook_faq.md`, nói về việc học viên cần tự chuẩn bị laptop; top-2 chứa chi tiết CPU, RAM, SSD, OS và mạng. | 0.6405 | Có | Học viên nên chuẩn bị laptop có CPU Intel Core i7 hoặc Apple M2 trở lên, RAM tối thiểu 16GB, SSD ít nhất 256GB, OS phù hợp và mạng ổn định. |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**  
Từ kết quả của Huy, tôi học được rằng một baseline đơn giản như FixedSizeChunker vẫn có thể đạt kết quả tốt nếu dùng embedding model semantic mạnh như OpenAI `text-embedding-3-small` và chunk_size đủ lớn. Tuy nhiên, fixed-size vẫn có điểm yếu là đôi khi top-1 chưa phải chunk đúng nhất vì nó không hiểu heading hoặc ranh giới Q&A.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**  
Phần này sẽ được bổ sung sau demo liên nhóm. Hiện tại, tôi chưa có đủ thông tin từ nhóm khác để ghi nhận xét chính xác.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**  
Nếu làm lại, tôi sẽ tiếp tục dùng `RecursiveChunker` nhưng tối ưu thêm theo từng loại tài liệu. Với FAQ, tôi sẽ chunk theo từng cặp câu hỏi-câu trả lời để tránh trường hợp câu hỏi laptop nằm ở top-1 nhưng chi tiết cấu hình CPU/RAM/SSD lại nằm ở top-2. Tôi cũng sẽ kết hợp metadata filter theo `category` cho các query rõ domain như `attendance_policy`, `completion_policy`, `stipend_policy` và `faq` để giảm nhiễu trong retrieval.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 14 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 10 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | Chưa chấm |
| **Tổng** | | **84 / 95 + Demo** |