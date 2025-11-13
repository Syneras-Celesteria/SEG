"""
Module 1: Web Crawling
Thu thập dữ liệu từ website Motchill - phim Việt Nam
ĐÃ CẬP NHẬT CHO MOTCHILLI.IO
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import sqlite3
from pathlib import Path
import os
import sys
import re

# Thêm path để import config
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import Config

class MotchillCrawler:
    """Crawler chuyên dụng cho website Motchilli.io (Đã cập nhật)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Cấu hình logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Khởi tạo database
        self.db_path = Config.DATABASE_PATH
        self.init_database()
        
        # Base URL cho Motchilli (ĐÃ CẬP NHẬT)
        self.base_url = "https://motchilli.io"
        
    def init_database(self):
        """Khởi tạo database để lưu dữ liệu phim"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tạo bảng lưu movies
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                original_title TEXT,
                url TEXT UNIQUE NOT NULL,
                description TEXT,
                year INTEGER,
                genre TEXT,
                country TEXT,
                director TEXT,
                cast TEXT,
                duration TEXT,
                quality TEXT,
                rating REAL,
                poster_url TEXT,
                trailer_url TEXT,
                episodes TEXT,
                status TEXT,
                source_website TEXT DEFAULT 'motchilli.io',
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def crawl_motchill_categories(self, max_pages: int = 10) -> List[Dict]:
        """Thu thập danh sách phim từ các category của Motchilli (ĐÃ CẬP NHẬT)"""
        
        # Cập nhật danh sách thể loại theo cấu trúc /the-loai/
        categories = [
            '/the-loai/co-trang',
            '/the-loai/chinh-kich',
            '/the-loai/bi-an',
            '/the-loai/gia-dinh',
            '/the-loai/hai-huoc',
            '/the-loai/hanh-dong',
            '/the-loai/hinh-su',
            '/the-loai/khoa-hoc',
            '/the-loai/kinh-di',
            '/the-loai/phieu-luu',
            '/the-loai/tam-ly',
            '/the-loai/tinh-cam',
            '/the-loai/vien-tuong',
            '/the-loai/vo-thuat',
            # Thêm các danh sách khác
            '/danh-sach/phim-chieu-rap',
            '/danh-sach/phim-bo',
            '/danh-sach/phim-le',
            '/quoc-gia/trung-quoc',
            '/quoc-gia/han-quoc',
            '/quoc-gia/thai-lan',
            '/quoc-gia/au-my'
        ]
        
        all_movies = []
        
        for category in categories:
            self.logger.info(f"Crawling category: {category}")
            # Giảm số trang crawl mỗi category để test nhanh hơn
            movies = self.crawl_category_pages(category, max_pages)
            all_movies.extend(movies)
            
        return all_movies
    
    def crawl_category_pages(self, category: str, max_pages: int) -> List[Dict]:
        """Thu thập phim từ một category cụ thể (ĐÃ CẬP NHẬT)"""
        movies = []
        
        for page in range(1, max_pages + 1):
            try:
                # Cấu trúc URL trang dường như không có /page-{page} mà dùng ?page={page}
                # Thử cả hai
                url_format_1 = f"{self.base_url}{category}?page={page}"
                url_format_2 = f"{self.base_url}{category}/page/{page}"
                
                # Thử format 1 trước
                response = self.session.get(url_format_1)
                self.logger.info(f"Crawling page {page}: {url_format_1}")
                
                if response.status_code != 200:
                    self.logger.info(f"Thử URL format 2: {url_format_2}")
                    response = self.session.get(url_format_2) # Thử format 2
                    response.raise_for_status() # Báo lỗi nếu thất bại

                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Sửa selector dựa trên HTML mới: Tìm 'li' có class 'item'
                movie_elements = soup.find_all('li', class_='item')

                if not movie_elements:
                    self.logger.info(f"Không tìm thấy phim ở trang {page}, dừng crawling category này")
                    break
                
                for element in movie_elements:
                    # Sửa logic tìm link: Tìm link chi tiết trong h3.name-title
                    movie_link_tag = element.find('h3', class_='name-title')
                    movie_link = None
                    
                    if movie_link_tag:
                        movie_link = movie_link_tag.find('a')
                    
                    if not movie_link:
                        movie_link = element.find('a') # Fallback

                    if movie_link:
                        movie_url = urljoin(self.base_url, movie_link.get('href'))
                        
                        # Bỏ qua nếu URL không hợp lệ
                        if not movie_url.startswith(self.base_url + '/phim/'):
                            continue

                        movie_data = self.crawl_movie_detail(movie_url)
                        
                        if movie_data:
                            movies.append(movie_data)
                            self.save_movie_to_db(movie_data)
                            
                        # Delay để tránh spam
                        time.sleep(Config.CRAWL_DELAY)
                        
                time.sleep(1)  # Delay giữa các trang
                
            except Exception as e:
                self.logger.error(f"Lỗi khi crawl trang {page} category {category}: {str(e)}")
                continue
                
        return movies
    
    def crawl_movie_detail(self, url: str) -> Optional[Dict]:
        """Thu thập chi tiết một bộ phim từ Motchill (ĐÃ CẬP NHẬT)"""
        try:
            self.logger.info(f"Crawling detail page: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # --- Trích xuất thông tin phim (selectors MỚI) ---
            
            # Tiêu đề
            title = self.safe_extract_text(soup.find('span', class_='title'))
            if not title:
                title = self.safe_extract_text(soup.find('h1')) # Fallback
            
            # Tiêu đề gốc
            original_title_span = soup.find('span', class_='real-name')
            original_title_text = self.safe_extract_text(original_title_span)
            original_title = re.sub(r'\(\d{4}\)', '', original_title_text).strip() # Loại bỏ năm (2025)
            
            # Mô tả phim
            description_elem = soup.find('div', class_='detail').find('div', class_='tab')
            description = self.safe_extract_text(description_elem)
            
            # Thông tin chi tiết (dùng helper mới)
            year = self.extract_year(soup)
            genre = self.extract_genre(soup)
            country = self.extract_country(soup)
            director = self.extract_director(soup)
            cast = self.extract_cast(soup)
            duration = self.extract_duration(soup)
            quality = self.extract_quality(soup)
            rating = self.extract_rating(soup)
            episodes = self.extract_episodes_info(soup)
            status = self.extract_status(soup)
            
            # Poster
            poster_elem = soup.find('div', class_='poster').find('img')
            poster_url = poster_elem.get('src') if poster_elem else None
            if poster_url and not poster_url.startswith('http'):
                poster_url = urljoin(self.base_url, poster_url)
            
            # Trailer (giữ logic cũ, có thể không tìm thấy)
            trailer_url = self.extract_trailer_url(soup)
            
            movie_data = {
                'title': title,
                'original_title': original_title,
                'url': url,
                'description': description,
                'year': year,
                'genre': genre,
                'country': country,
                'director': director,
                'cast': cast,
                'duration': duration,
                'quality': quality, # Ánh xạ sang "Ngôn ngữ"
                'rating': rating,
                'poster_url': poster_url,
                'trailer_url': trailer_url,
                'episodes': episodes, # Ánh xạ sang "Số tập"
                'status': status, # Ánh xạ sang "Trạng thái"
                'source_website': 'motchilli.io'
            }
            
            return movie_data
            
        except Exception as e:
            self.logger.error(f"Lỗi khi crawl movie {url}: {str(e)}")
            return None
    
    def safe_extract_text(self, element) -> str:
        """Trích xuất text an toàn từ element"""
        if element:
            return element.get_text().strip()
        return ""

    def _extract_info_from_list(self, soup, label_text: str, extract_links: bool = False) -> str:
        """Helper MỚI: trích xuất info từ <dl> list"""
        try:
            # Tìm <dt> (label)
            dt = soup.find('dt', text=re.compile(rf'^{label_text}$', re.I))
            if not dt:
                return ""
            
            # Tìm <dd> (value) ngay sau nó
            dd = dt.find_next_sibling('dd')
            if not dd:
                return ""
            
            # Nếu cần lấy text từ các link <a>
            if extract_links:
                links = dd.find_all('a')
                if links:
                    return ', '.join(self.safe_extract_text(link) for link in links)
            
            # Ngược lại, lấy text của <dd>
            return self.safe_extract_text(dd)
        except Exception as e:
            self.logger.warning(f"Lỗi khi trích xuất '{label_text}': {e}")
            return ""

    # --- CÁC HÀM EXTRACT ĐÃ VIẾT LẠI ---

    def extract_year(self, soup) -> Optional[int]:
        """Trích xuất năm phim (ĐÃ CẬP NHẬT)"""
        year_text = self._extract_info_from_list(soup, 'Năm sản xuất:')
        if year_text.isdigit():
            return int(year_text)
        
        # Fallback: Lấy từ tiêu đề gốc
        try:
            original_title_span = soup.find('span', class_='real-name')
            if original_title_span:
                year_match = re.search(r'\((\d{4})\)', self.safe_extract_text(original_title_span))
                if year_match:
                    return int(year_match.group(1))
        except Exception:
            pass # Bỏ qua nếu lỗi
            
        return None
    
    def extract_genre(self, soup) -> str:
        """Trích xuất thể loại phim (ĐÃ CẬP NHẬT)"""
        return self._extract_info_from_list(soup, 'Thể loại:', extract_links=True)
    
    def extract_country(self, soup) -> str:
        """Trích xuất quốc gia (ĐÃ CẬP NHẬT)"""
        return self._extract_info_from_list(soup, 'Quốc gia:', extract_links=True)
    
    def extract_director(self, soup) -> str:
        """Trích xuất đạo diễn (ĐÃ CẬP NHẬT)"""
        return self._extract_info_from_list(soup, 'Đạo diễn:', extract_links=True)
    
    def extract_cast(self, soup) -> str:
        """Trích xuất diễn viên (ĐÃ CẬP NHẬT)"""
        return self._extract_info_from_list(soup, 'Diễn viên:', extract_links=True)
    
    def extract_duration(self, soup) -> str:
        """Trích xuất thời lượng (ĐÃ CẬP NHẬT)"""
        return self._extract_info_from_list(soup, 'Thời lượng:')
    
    def extract_quality(self, soup) -> str:
        """Trích xuất chất lượng phim (ĐÃ CẬP NHẬT)
        Ánh xạ sang 'Ngôn ngữ'
        """
        return self._extract_info_from_list(soup, 'Ngôn ngữ:')
    
    def extract_rating(self, soup) -> Optional[float]:
        """Trích xuất rating (ĐÃ CẬP NHẬT)"""
        rating_elem = soup.find('span', class_='average', id='average')
        if rating_elem:
            rating_text = self.safe_extract_text(rating_elem)
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                try:
                    return float(rating_match.group(1))
                except ValueError:
                    return None
        return None
    
    def extract_trailer_url(self, soup) -> str:
        """Trích xuất URL trailer (Giữ nguyên, có thể không tìm thấy)"""
        trailer_elem = soup.find('a', text=re.compile(r'Trailer', re.I)) or \
                      soup.find('iframe', src=re.compile(r'youtube|youtu.be'))
        
        if trailer_elem:
            if trailer_elem.name == 'a':
                return trailer_elem.get('href', '')
            elif trailer_elem.name == 'iframe':
                return trailer_elem.get('src', '')
        return ""
    
    def extract_episodes_info(self, soup) -> str:
        """Trích xuất thông tin tập phim (ĐÃ CẬP NHẬT)
        Ánh xạ sang 'Số tập'
        """
        return self._extract_info_from_list(soup, 'Số tập:')
    
    def extract_status(self, soup) -> str:
        """Trích xuất trạng thái phim (ĐÃ CẬP NHẬT)
        Ánh xạ sang 'Trạng thái'
        """
        return self._extract_info_from_list(soup, 'Trạng thái:')
    
    def save_movie_to_db(self, movie_data: Dict):
        """Lưu thông tin phim vào database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO movies 
                (title, original_title, url, description, year, genre, country,
                 director, cast, duration, quality, rating, poster_url, 
                 trailer_url, episodes, status, source_website)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                movie_data.get('title'),
                movie_data.get('original_title'),
                movie_data.get('url'),
                movie_data.get('description'),
                movie_data.get('year'),
                movie_data.get('genre'),
                movie_data.get('country'),
                movie_data.get('director'),
                movie_data.get('cast'),
                movie_data.get('duration'),
                movie_data.get('quality'),
                movie_data.get('rating'),
                movie_data.get('poster_url'),
                movie_data.get('trailer_url'),
                movie_data.get('episodes'),
                movie_data.get('status'),
                movie_data.get('source_website')
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Đã lưu phim: {movie_data.get('title')}")
            
        except Exception as e:
            self.logger.error(f"Lỗi khi lưu phim '{movie_data.get('title')}': {str(e)}")
    
    def export_to_json(self, output_file: str):
        """Xuất dữ liệu ra file JSON"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM movies')
            rows = cursor.fetchall()
            
            # Lấy tên cột
            column_names = [description[0] for description in cursor.description]
            
            # Chuyển thành list of dict
            movies = []
            for row in rows:
                movie_dict = dict(zip(column_names, row))
                movies.append(movie_dict)
            
            # Lưu ra file JSON
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(movies, f, ensure_ascii=False, indent=2)
            
            conn.close()
            self.logger.info(f"Đã xuất {len(movies)} phim ra {output_file}")
            
        except Exception as e:
            self.logger.error(f"Lỗi khi xuất dữ liệu: {str(e)}")

def main():
    """Hàm main để chạy crawler"""
    crawler = MotchillCrawler()
    
    # Xóa DB cũ để crawl lại (QUAN TRỌNG)
    if os.path.exists(crawler.db_path):
        os.remove(crawler.db_path)
        print(f"Đã xóa database cũ: {crawler.db_path}")
        
    crawler.init_database() # Tạo lại database
    
    # Crawl dữ liệu
    print("Bắt đầu crawl dữ liệu từ Motchilli.io...")
    # Giảm max_pages xuống 1 hoặc 2 để test nhanh
    movies = crawler.crawl_motchill_categories(max_pages=2) 
    
    print(f"Đã crawl được {len(movies)} phim")
    
    # Xuất dữ liệu
    output_path = Config.RAW_DATA_PATH / 'movies.json'
    crawler.export_to_json(str(output_path))
    
    print(f"Dữ liệu đã được lưu tại: {output_path}")

if __name__ == "__main__":
    main()