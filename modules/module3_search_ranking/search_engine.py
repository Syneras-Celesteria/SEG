"""
Module 3: Search Engine & Ranking
Xử lý truy vấn và xếp hạng kết quả tìm kiếm
ĐÃ CẬP NHẬT: SCORING (TÍNH ĐIỂM) ĐỂ ƯU TIÊN CỤM TỪ CHÍNH XÁC
"""

import sqlite3
import json
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import Config
from modules.module2_text_processing.text_processor import MovieIndexBuilder

class SearchEngine:
    """Search Engine chính cho việc tìm kiếm phim"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_path = Config.DATABASE_PATH
        self.index_builder = MovieIndexBuilder()
    
    def search(self, query: str, page: int = 1, per_page: int = None) -> Tuple[List[Dict], int]:
        if per_page is None:
            per_page = Config.RESULTS_PER_PAGE
        
        if not query or not query.strip():
            return [], 0
        
        try:
            results, total = self._search_simple(query, page, per_page)
            return results, total
        except Exception as e:
            self.logger.error(f"Lỗi khi tìm kiếm: {e}")
            return [], 0
    
    def _search_simple(self, query: str, page: int, per_page: int) -> Tuple[List[Dict], int]:
        """
        Tìm kiếm với thuật toán Scoring (Tính điểm):
        - Khớp từ khóa rời rạc: Điểm thấp
        - Khớp cụm từ chính xác (Exact Phrase): Điểm cao
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM movies')
            all_movies = cursor.fetchall()
            conn.close()

            query_lower = query.lower().strip()
            query_terms = query_lower.split() 
            
            matched_movies = []

            for movie in all_movies:
                # Gom tất cả thông tin lại
                title = str(movie['title'] or '').lower()
                full_text = " ".join([
                    title,
                    str(movie['original_title'] or ''),
                    str(movie['genre'] or ''),
                    str(movie['cast'] or ''),
                    str(movie['director'] or ''),
                    str(movie['country'] or ''),
                    str(movie['year'] or '')
                ]).lower()
                
                # 1. Lọc cơ bản: Phải chứa đủ các từ khóa (Logic AND)
                is_match = True
                for term in query_terms:
                    if term not in full_text:
                        is_match = False
                        break
                
                if is_match:
                    movie_dict = dict(movie)
                    
                    # --- [NÂNG CẤP] HỆ THỐNG TÍNH ĐIỂM ---
                    score = 0.0
                    
                    # Tiêu chí 1: Khớp cụm từ chính xác (QUAN TRỌNG NHẤT)
                    # Ví dụ: "Hàn Quốc" dính liền trong text
                    if query_lower in full_text:
                        score += 100.0
                    
                    # Tiêu chí 2: Từ khóa nằm trong Tiêu đề (Title)
                    if query_lower in title:
                        score += 50.0
                        
                    # Tiêu chí 3: Từ khóa rời rạc (Cơ bản)
                    score += 10.0
                    
                    movie_dict['relevance_score'] = score
                    
                    # Highlight
                    movie_dict['highlighted_title'] = self._highlight_text(
                        movie_dict.get('title', ''), query
                    )
                    movie_dict['highlighted_description'] = self._highlight_text(
                        movie_dict.get('description', ''), query, max_length=200
                    )
                    matched_movies.append(movie_dict)

            # [QUAN TRỌNG] Sắp xếp: 
            # Ưu tiên 1: Điểm cao (relevance_score)
            # Ưu tiên 2: Năm mới nhất (year)
            matched_movies.sort(key=lambda x: (x['relevance_score'], x.get('year') or 0), reverse=True)

            total_results = len(matched_movies)
            
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            page_results = matched_movies[start_idx:end_idx]
            
            return page_results, total_results
            
        except Exception as e:
            self.logger.error(f"Lỗi tìm kiếm simple: {e}")
            return [], 0

    def _get_movie_by_id(self, movie_id: int) -> Optional[Dict]:
        """Lấy thông tin chi tiết phim theo ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                col_names = [description[0] for description in cursor.description]
                return dict(zip(col_names, result))
            return None
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy movie {movie_id}: {e}")
            return None
    
    def _highlight_text(self, text: str, query: str, max_length: int = None) -> str:
        """Highlight từ khóa trong text"""
        if not text or not query:
            return text
        
        if max_length and len(text) > max_length:
            text = text[:max_length] + "..."
        
        highlighted_text = text
        query_terms = query.lower().split()
        query_terms.sort(key=len, reverse=True)
        
        for term in query_terms:
            if len(term) > 1:
                import re
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                highlighted_text = pattern.sub(f'<mark>\\g<0></mark>', highlighted_text)
        
        return highlighted_text
    
    def get_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """Lấy gợi ý tìm kiếm"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT title FROM movies 
                WHERE LOWER(title) LIKE ? 
                LIMIT ?
            ''', (f'%{query.lower()}%', limit))
            suggestions = [row[0] for row in cursor.fetchall()]
            conn.close()
            return suggestions
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy suggestions: {e}")
            return []
    
    def get_popular_movies(self, limit: int = 10) -> List[Dict]:
        """Lấy danh sách phim phổ biến"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM movies 
                WHERE rating IS NOT NULL
                ORDER BY rating DESC, year DESC
                LIMIT ?
            ''', (limit,))
            results = cursor.fetchall()
            conn.close()
            return [dict(row) for row in results]
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy popular movies: {e}")
            return []
    
    def get_movies_by_genre(self, genre: str, limit: int = 10) -> List[Dict]:
        """Lấy phim theo thể loại"""
        movies, _ = self._search_simple(genre, page=1, per_page=limit)
        return movies