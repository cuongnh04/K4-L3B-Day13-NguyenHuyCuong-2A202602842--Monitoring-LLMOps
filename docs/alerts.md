# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1: HighLatencyP95 <a id="alert-1"></a>

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Latency P95 của `response_sent.latency_ms` (ngưỡng SLO <= 3000ms)
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` duy trì trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng bị phản hồi chậm, trải nghiệm hội thoại kém, nguy cơ timeout client.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel **Latency percentiles and TTFT** để xác nhận P50, P95, P99 và TTFT trong khung giờ xảy ra sự cố.
  2. Lọc file `data/logs.jsonl` tìm các log event `response_sent` có `latency_ms > 3000`, trích xuất `correlation_id` của request bất thường.
  3. Mở Langfuse tìm trace có cùng `correlation_id` để kiểm tra span tree (so sánh thời gian giữa span `retrieval` và `generation`).
- Mitigation tạm thời: Nếu do retrieval chậm (vector database nghẽn), restart/scale replica vector db hoặc rollback prompt; nếu do incident injection `rag_slow`, chạy `python scripts/inject_incident.py --disable`.
- Owner: `student-2A202602842`

## Alert 2: HighErrorRate <a id="alert-2"></a>

- Tên: `HighErrorRate`
- Severity: `critical`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Error rate phần trăm của API (ngưỡng guardrail error_rate <= 2%)
- Điều kiện và thời gian duy trì: `error_rate_pct > 2%` (tỷ lệ `request_failed` / `request_received`) kéo dài 5 phút
- Ảnh hưởng tới người dùng: Người dùng nhận mã lỗi 500/Internal Server Error, không nhận được câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel **Error rate and retrieval success** để xem biểu đồ lỗi và breakdown theo `error_type`.
  2. Lọc `data/logs.jsonl` theo `event == "request_failed"` để xác định `error_type` phổ biến và lấy `correlation_id` tương ứng.
  3. Mở trace trên Langfuse theo `correlation_id` để xem span nào ném exception và stack trace chi tiết.
- Mitigation tạm thời: Nếu do `tool_fail` (vector store timeout), chuyển sang chế độ fallback retrieval; kiểm tra kết nối downstream LLM provider; restart service nếu cần.
- Owner: `student-2A202602842`

## Alert 3: LowRetrievalSuccessRate <a id="alert-3"></a>

- Tên: `LowRetrievalSuccessRate`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Tỷ lệ retrieval thành công `retrieval_success_rate_pct` (ngưỡng guardrail >= 90%)
- Điều kiện và thời gian duy trì: `retrieval_success_rate_pct < 90%` trong vòng 5 phút
- Ảnh hưởng tới người dùng: RAG không tìm được context tài liệu, bot phải fallback sang kiến thức chung làm giảm độ chính xác và chất lượng câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra dashboard panel **Error rate and retrieval success** mục `tool_success_rate_pct`.
  2. Lọc log `response_sent` hoặc `request_failed` có `tool_name == "retrieval"` và `tool_success == false`.
  3. Mở trace tương ứng trên Langfuse, kiểm tra observation `retrieval` xem tài liệu trả về rỗng hay có exception vector store.
- Mitigation tạm thời: Kiểm tra sức khỏe vector store / ChromaDB / Pinecone; chuyển sang fallback keyword search nếu vector search fail; nạp lại index nếu dữ liệu bị corrupt.
- Owner: `student-2A202602842`
