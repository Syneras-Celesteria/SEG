# 🎬 Máy Tìm Kiếm Phim Chuyên Sâu (Vertical Search Engine)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![Status](https://img.shields.io/badge/Status-Completed-brightgreen.svg)]()

## 📖 Giới Thiệu

Đây là đồ án cuối kỳ môn **Máy Tìm Kiếm (Search Engine)**. Dự án xây dựng một hệ thống tìm kiếm chuyên sâu (Vertical Search Engine) tập trung vào lĩnh vực **Phim ảnh & Giải trí** tại thị trường Việt Nam.

Hệ thống tự động thu thập dữ liệu từ website nguồn (Motchilli), xử lý ngôn ngữ tự nhiên tiếng Việt, xây dựng chỉ mục và cung cấp giao diện tìm kiếm thông minh với khả năng xếp hạng kết quả dựa trên độ phù hợp (Relevance Ranking).

---

## 🚀 Tính Năng Nổi Bật

### 1. Thu Thập Dữ Liệu (Web Crawler)
* Tự động thu thập dữ liệu từ nhiều danh mục: Phim bộ, Phim lẻ, Hoạt hình, Phim chiếu rạp.
* Bóc tách chi tiết các trường: Tên phim, Năm phát hành, Quốc gia, Diễn viên, Đạo diễn, Poster, Mô tả.
* Cơ chế chống chặn (Anti-blocking) và xử lý lỗi mạng tự động.

### 2. Tìm Kiếm & Xếp Hạng (Ranking Core)
* **Xử lý Tiếng Việt:** Hỗ trợ tìm kiếm chính xác bất kể chữ hoa/thường và dấu câu.
* **Thuật toán Scoring (Tính điểm trọng số):**
    * **Exact Phrase Match (+100 điểm):** Ưu tiên tuyệt đối các phim khớp chính xác cụm từ (Ví dụ: "Hàn Quốc", "2025").
    * **Title Match (+50 điểm):** Ưu tiên từ khóa xuất hiện trong tiêu đề.
    * **Recency Boost:** Ưu tiên hiển thị các phim mới sản xuất (2024, 2025) lên đầu.

### 3. Giao Diện Người Dùng (Web UI)
* **Search Suggestions:** Gợi ý từ khóa tự động khi người dùng nhập liệu.
* **Movie Carousel:** Băng chuyền lướt xem phim phổ biến mượt mà.
* **Bộ lọc nhanh:** Tìm kiếm nhanh theo Quốc gia (Việt Nam, Trung Quốc, Hàn Quốc...) và Thể loại.
* **Responsive:** Giao diện tương thích tốt trên cả máy tính và điện thoại di động.

### 4. Đánh Giá Hệ Thống (Evaluation)
* Tự động sinh dữ liệu kiểm thử (Ground Truth) dựa trên cơ sở dữ liệu thực tế.
* Tính toán các chỉ số đánh giá học thuật: **Precision@10, Recall@10, MAP**.

---

## 📂 Cấu Trúc Dự Án

```text
MOVIE_SEARCH_ENGINE/
├── modules/                    # Source code chính của các phân hệ
│   ├── module1_crawler/       # Module 1: Thu thập dữ liệu
│   │   └── crawler.py          # Script crawl dữ liệu từ Motchilli
│   ├── module2_text_processing/# Module 2: Xử lý văn bản & Indexing
│   │   └── text_processor.py   # Tokenizer tiếng Việt & Inverted Index
│   ├── module3_search_ranking/ # Module 3: Lõi tìm kiếm
│   │   └── search_engine.py    # Xử lý truy vấn & Thuật toán xếp hạng
│   └── module5_evaluation/     # Module 5: Đánh giá hệ thống
│       └── evaluator.py        # Script tính điểm Precision/MAP
├── data/                       # Nơi lưu trữ dữ liệu
│   ├── raw/                    # Dữ liệu thô (JSON)
│   └── search_engine.db        # SQLite Database (Dữ liệu chính)
├── static/                     # Tài nguyên Frontend
│   ├── css/                    # Style giao diện (Custom CSS)
│   ├── js/                     # Script xử lý giao diện (AJAX, Carousel)
│   └── images/                 # Hình ảnh tĩnh
├── templates/                  # Giao diện HTML (Jinja2)
│   ├── index.html              # Trang chủ
│   ├── search_results.html     # Trang kết quả tìm kiếm
│   └── error.html              # Trang báo lỗi
├── config/
│   └── settings.py             # Cấu hình hệ thống (Đường dẫn, Tham số)
├── app.py                      # File chạy chính (Flask Server)
├── requirements.txt            # Các thư viện cần thiết
└── README.md                   # Tài liệu hướng dẫn
```

### 🛠️ Hướng Dẫn Cài Đặt (Cho Developer)
## 1️⃣. Yêu Cầu Hệ Thống

Python 3.8 trở lên

Kết nối Internet (để crawler hoạt động)

## 2️⃣. Cài Đặt Thư Viện
```
pip install flask requests beautifulsoup4 underthesea numpy
```

## 3️⃣. Thu Thập Dữ Liệu (Crawling)

Trước khi chạy web, cần thu thập dữ liệu phim và lưu vào database:
```
python modules/module1_crawling/crawler.py
```

⏳ Lưu ý: Quá trình này có thể mất vài phút để tải dữ liệu từ internet.

## 4️⃣. Khởi Chạy Website
```
python app.py
```

Sau khi server chạy, mở trình duyệt và truy cập:
👉 http://127.0.0.1:5000

### 📘 Hướng Dẫn Sử Dụng (Cho Người Dùng Cuối)
* 🔍 1. Tìm Kiếm Cơ Bản

Nhập từ khóa: tên phim (“Mai”, “Đào”), diễn viên (“Trấn Thành”), hoặc đạo diễn.

Gợi ý (suggestions) sẽ tự động hiển thị khi nhập từ 2 ký tự trở lên.

* 🧭 2. Tìm Kiếm Nâng Cao

* Hệ thống hỗ trợ các từ khóa đặc biệt:

Loại tìm kiếm	Ví dụ	Mô tả
Năm	2024, 2025	Xem phim mới nhất
Quốc gia	Hàn Quốc, Trung Quốc, Việt Nam	Lọc theo nước sản xuất
Thể loại	Hành động, Cổ trang, Tình cảm	Lọc theo thể loại phim
* 🌟 3. Khám Phá Nhanh

Phim Phổ Biến: Lướt carousel để xem các phim hot nhất.

Nút Bấm Nhanh:

Theo Thể Loại: click “Cổ Trang”, “Hành Động”, ...

Theo Quốc Gia: click 🇻🇳, 🇰🇷, 🇨🇳, ...

* 🎞️ 4. Xem Kết Quả

Kết quả hiển thị: Poster, Năm sản xuất, Rating (sao).

Từ khóa được Highlight (tô vàng) trong tiêu đề & mô tả.

Click “Xem phim” để mở trang nguồn xem phim.

### 📊 Đánh Giá Hệ Thống (Evaluation)

Chạy lệnh sau để xem báo cáo độ chính xác:
```
python modules/module5_evaluation/evaluator.py
```
### 🔎 Kết Quả Thực Nghiệm (Top-10)

| Truy vấn mẫu | Precision@10 | Đánh giá |
|---------------|---------------|----------|
| "2024", "2025" | 1.00 | Xuất sắc (Nhận diện chính xác phim mới) |
| "Hàn Quốc" | 1.00 | Xuất sắc (Nhờ thuật toán Scoring cụm từ) |
| "Cổ trang" | 1.00 | Xuất sắc |
| "Hành động" | 1.00 | Xuất sắc |
| **MAP Score** | ~1.00 | Độ chính xác trung bình rất cao |


### ⚙️ Công Nghệ Sử Dụng

| Thành phần | Công nghệ | Chi tiết |
|-------------|------------|----------|
| **Ngôn ngữ** | Python 3.x | Ngôn ngữ lập trình chính |
| **Backend** | Flask | Web Framework nhẹ và linh hoạt |
| **Database** | SQLite | Lưu trữ dữ liệu có cấu trúc |
| **Crawler** | Requests, BeautifulSoup4 | Thu thập và bóc tách dữ liệu HTML |
| **Frontend** | HTML5, CSS3, JS | Giao diện người dùng (Bootstrap 5) |
| **NLP** | Underthesea | Thư viện xử lý ngôn ngữ tiếng Việt |
### 👥 Thông Tin Tác Giả

Sinh viên thực hiện: Pham Nguyen Minh Phong, Nguyen Hoai My, Cao Tran Anh Khoa

Lớp: AI1909

Giảng viên hướng dẫn: Ha Anh Vu

📄 Bản Quyền (License)

Dự án được phát triển cho mục đích học tập và nghiên cứu tại trường Đại học.
Dữ liệu phim thuộc bản quyền của website nguồn Motchilli.io.