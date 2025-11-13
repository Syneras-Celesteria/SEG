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
