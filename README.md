# Bài tập lớn HK242 - Xử lý ngôn ngữ tự nhiên

**Thông tin cá nhân**:
- Họ và tên: Trần Nguyên Huân
- MSSV: 2370692

**Mô tả dự án**:
Dự án xây dựng hệ thống hỏi đáp về các chuyến bay nội địa, đáp ứng yêu cầu bài tập lớn HK242. Hệ thống xử lý câu hỏi tiếng Việt, thực hiện các bước: phân đoạn từ, phân tích cú pháp phụ thuộc, tạo quan hệ văn phạm, dạng luận lý, dạng thủ tục, và truy vấn cơ sở dữ liệu để trả lời.

**Cấu trúc thư mục**:
- **Input/**: Chứa `query.txt` (20 câu hỏi), `database.txt` (dữ liệu chuyến bay) và `vietnamese-stopwords.txt` (danh sách các stopwords trong phạm vi đề bài).
- **Output/**: Chứa kết quả trung gian (`tokens.txt`, `dependencies.txt`, `grammatical.txt`, `logical.txt`, `procedural.txt`) và câu trả lời (`answers.txt`).
- **models/**: Chứa các module:
  - `parser.py`: Phân đoạn từ và phân tích cú pháp phụ thuộc (dùng pyvi).
  - `database.py`: Quản lý cơ sở dữ liệu chuyến bay.
  - `processor.py`: Chuyển đổi qua các bước từ văn phạm đến thủ tục.
- **main.py**: Điểm vào của chương trình.
- **README.md**: Tài liệu này.

**Hướng dẫn chạy**:
1. Cài đặt môi trường:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Trên Linux/MacOS
   venv\Scripts\activate     # Trên Windows
   pip install -r requirements.txt
   ```
2. Chạy chương trình:
   ```bash
   python main.py
   ```
3. Kết quả sẽ được lưu trong thư mục `Output/`.