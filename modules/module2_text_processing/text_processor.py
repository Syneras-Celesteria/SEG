"""
Module 2: Text Processing & Indexing
Xử lý văn bản tiếng Việt và xây dựng chỉ mục ngược (Inverted Index)
"""

import sqlite3
import json
import pickle
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter
import re
import math
import logging
from pathlib import Path
import sys

# Thêm path để import config
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import Config

try:
    from underthesea import word_tokenize
    UNDERTHESEA_AVAILABLE = True
except ImportError:
    UNDERTHESEA_AVAILABLE = False
    print("Warning: underthesea not installed. Using simple tokenization.")

class VietnameseTextProcessor:
    """Xử lý văn bản tiếng Việt"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Load Vietnamese stopwords
        self.stopwords = self.load_vietnamese_stopwords()
        
        # Regex patterns for cleaning
        self.patterns = {
            'html_tags': re.compile(r'<[^>]+>'),
            'special_chars': re.compile(r'[^\w\s]'),
            'multiple_spaces': re.compile(r'\s+'),
            'numbers': re.compile(r'\d+')
        }
    
    def load_vietnamese_stopwords(self) -> Set[str]:
        """Load danh sách từ dừng tiếng Việt"""
        # Từ dừng tiếng Việt cơ bản
        default_stopwords = {
            'là', 'của', 'và', 'có', 'được', 'một', 'trong', 'cho', 'với', 'này',
            'đó', 'những', 'các', 'để', 'từ', 'không', 'đã', 'sẽ', 'bị', 'bởi',
            'về', 'tại', 'lại', 'như', 'hay', 'hoặc', 'nếu', 'mà', 'khi', 'nào',
            'đâu', 'ai', 'gì', 'sao', 'thế', 'vậy', 'rất', 'lắm', 'nhiều', 'ít',
            'mỗi', 'tất', 'toàn', 'cả', 'chỉ', 'duy', 'nhất', 'cũng', 'thêm',
            'nữa', 'khác', 'giữa', 'trước', 'sau', 'trên', 'dưới', 'ngoài', 'theo'
        }
        
        # Thử load từ file nếu có
        try:
            if Config.VIETNAMESE_STOPWORDS_PATH.exists():
                with open(Config.VIETNAMESE_STOPWORDS_PATH, 'r', encoding='utf-8') as f:
                    file_stopwords = set(line.strip() for line in f if line.strip())
                default_stopwords.update(file_stopwords)
        except Exception as e:
            self.logger.warning(f"Không thể load stopwords từ file: {e}")
        
        return default_stopwords
    
    def clean_text(self, text: str) -> str:
        """Làm sạch văn bản"""
        if not text:
            return ""
        
        # Loại bỏ HTML tags
        text = self.patterns['html_tags'].sub(' ', text)
        
        # Chuyển về chữ thường
        text = text.lower()
        
        # Loại bỏ ký tự đặc biệt (giữ lại tiếng Việt)
        text = re.sub(r'[^\w\s\u00C0-\u1EF9]', ' ', text)
        
        # Loại bỏ số
        text = self.patterns['numbers'].sub(' ', text)
        
        # Loại bỏ khoảng trắng thừa
        text = self.patterns['multiple_spaces'].sub(' ', text)
        
        return text.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """Tách từ tiếng Việt"""
        if not text:
            return []
        
        if UNDERTHESEA_AVAILABLE:
            # Sử dụng underthesea để tách từ
            try:
                tokens = word_tokenize(text)
            except Exception as e:
                self.logger.warning(f"Lỗi khi tách từ với underthesea: {e}")
                tokens = text.split()
        else:
            # Fallback: tách từ đơn giản
            tokens = text.split()
        
        # Lọc từ
        filtered_tokens = []
        for token in tokens:
            # Bỏ từ quá ngắn hoặc quá dài
            if Config.MIN_WORD_LENGTH <= len(token) <= Config.MAX_WORD_LENGTH:
                # Bỏ từ dừng
                if token not in self.stopwords:
                    filtered_tokens.append(token)
        
        return filtered_tokens
    
    def process_text(self, text: str) -> List[str]:
        """Pipeline xử lý văn bản hoàn chỉnh"""
        # Làm sạch
        cleaned_text = self.clean_text(text)
        
        # Tách từ
        tokens = self.tokenize(cleaned_text)
        
        return tokens

class InvertedIndex:
    """Chỉ mục ngược (Inverted Index) cho tìm kiếm"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_processor = VietnameseTextProcessor()
        
        # Cấu trúc dữ liệu chính
        self.index = defaultdict(dict)  # {term: {doc_id: [positions]}}
        self.doc_lengths = {}  # {doc_id: length}
        self.doc_count = 0
        self.vocabulary = set()
        
        # TF-IDF data
        self.tf_idf = defaultdict(dict)  # {doc_id: {term: tf_idf_score}}
        self.idf = {}  # {term: idf_score}
        
    def add_document(self, doc_id: int, text_fields: Dict[str, str], weights: Dict[str, float] = None):
        """Thêm document vào index
        
        Args:
            doc_id: ID của document
            text_fields: Dict chứa các field text {"title": "...", "description": "..."}
            weights: Dict trọng số cho từng field {"title": 2.0, "description": 1.0}
        """
        if weights is None:
            weights = {"title": 2.0, "description": 1.0, "genre": 1.5, "cast": 1.2, "director": 1.3}
        
        all_tokens = []
        term_positions = defaultdict(list)
        position = 0
        
        # Xử lý từng field
        for field_name, field_text in text_fields.items():
            if not field_text:
                continue
                
            tokens = self.text_processor.process_text(field_text)
            field_weight = weights.get(field_name, 1.0)
            
            for token in tokens:
                # Áp dụng trọng số bằng cách lặp lại token
                for _ in range(int(field_weight)):
                    all_tokens.append(token)
                    term_positions[token].append(position)
                    position += 1
        
        # Cập nhật index
        for term, positions in term_positions.items():
            self.index[term][doc_id] = positions
            self.vocabulary.add(term)
        
        # Lưu độ dài document
        self.doc_lengths[doc_id] = len(all_tokens)
        self.doc_count += 1
        
        self.logger.debug(f"Đã index document {doc_id} với {len(all_tokens)} tokens")
    
    def calculate_tf_idf(self):
        """Tính toán TF-IDF cho toàn bộ collection"""
        self.logger.info("Bắt đầu tính toán TF-IDF...")
        
        # Tính IDF cho mỗi term
        for term in self.vocabulary:
            df = len(self.index[term])  # Document frequency
            self.idf[term] = math.log(self.doc_count / df) if df > 0 else 0
        
        # Tính TF-IDF cho mỗi document
        for doc_id in self.doc_lengths:
            doc_length = self.doc_lengths[doc_id]
            
            for term in self.vocabulary:
                if doc_id in self.index[term]:
                    tf = len(self.index[term][doc_id]) / doc_length  # Term frequency
                    idf = self.idf[term]
                    self.tf_idf[doc_id][term] = tf * idf
                else:
                    self.tf_idf[doc_id][term] = 0
        
        self.logger.info(f"Đã tính toán TF-IDF cho {len(self.vocabulary)} terms và {self.doc_count} documents")
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """Tìm kiếm documents liên quan đến query
        
        Returns:
            List of (doc_id, score) sorted by score descending
        """
        query_tokens = self.text_processor.process_text(query)
        
        if not query_tokens:
            return []
        
        # Tính vector query
        query_tf = Counter(query_tokens)
        query_length = len(query_tokens)
        query_vector = {}
        
        for term in query_tf:
            if term in self.vocabulary:
                tf = query_tf[term] / query_length
                idf = self.idf.get(term, 0)
                query_vector[term] = tf * idf
        
        # Tính cosine similarity với mỗi document
        doc_scores = {}
        
        for doc_id in self.doc_lengths:
            score = 0
            doc_norm = 0
            query_norm = 0
            
            for term in query_vector:
                query_weight = query_vector[term]
                doc_weight = self.tf_idf[doc_id].get(term, 0)
                
                score += query_weight * doc_weight
                query_norm += query_weight ** 2
                doc_norm += doc_weight ** 2
            
            # Normalize
            if doc_norm > 0 and query_norm > 0:
                score = score / (math.sqrt(doc_norm) * math.sqrt(query_norm))
                doc_scores[doc_id] = score
        
        # Sắp xếp theo score
        results = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
    
    def save_index(self, file_path: str):
        """Lưu index ra file"""
        try:
            data = {
                'index': dict(self.index),
                'doc_lengths': self.doc_lengths,
                'doc_count': self.doc_count,
                'vocabulary': list(self.vocabulary),
                'tf_idf': dict(self.tf_idf),
                'idf': self.idf
            }
            
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            
            self.logger.info(f"Đã lưu index tại {file_path}")
            
        except Exception as e:
            self.logger.error(f"Lỗi khi lưu index: {e}")
    
    def load_index(self, file_path: str):
        """Load index từ file"""
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            self.index = defaultdict(dict, data['index'])
            self.doc_lengths = data['doc_lengths']
            self.doc_count = data['doc_count']
            self.vocabulary = set(data['vocabulary'])
            self.tf_idf = defaultdict(dict, data['tf_idf'])
            self.idf = data['idf']
            
            self.logger.info(f"Đã load index từ {file_path}")
            
        except Exception as e:
            self.logger.error(f"Lỗi khi load index: {e}")

class MovieIndexBuilder:
    """Builder để xây dựng index cho dữ liệu phim"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.index = InvertedIndex()
        self.db_path = Config.DATABASE_PATH
    
    def build_index_from_database(self):
        """Xây dựng index từ dữ liệu trong database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, original_title, description, genre, 
                       cast, director, country 
                FROM movies
            ''')
            
            movies = cursor.fetchall()
            conn.close()
            
            self.logger.info(f"Bắt đầu xây dựng index cho {len(movies)} phim...")
            
            for movie in movies:
                doc_id, title, original_title, description, genre, cast, director, country = movie
                
                # Chuẩn bị text fields
                text_fields = {
                    'title': title or '',
                    'original_title': original_title or '',
                    'description': description or '',
                    'genre': genre or '',
                    'cast': cast or '',
                    'director': director or '',
                    'country': country or ''
                }
                
                # Thêm vào index
                self.index.add_document(doc_id, text_fields)
            
            # Tính TF-IDF
            self.index.calculate_tf_idf()
            
            self.logger.info("Hoàn thành xây dựng index")
            
        except Exception as e:
            self.logger.error(f"Lỗi khi xây dựng index: {e}")
    
    def save_index(self):
        """Lưu index ra file"""
        Config.init_directories()
        index_file = Config.INDEX_PATH / 'movie_index.pkl'
        self.index.save_index(str(index_file))
    
    def load_index(self):
        """Load index từ file"""
        index_file = Config.INDEX_PATH / 'movie_index.pkl'
        if index_file.exists():
            self.index.load_index(str(index_file))
            return True
        return False

def main():
    """Hàm main để build index"""
    logging.basicConfig(level=logging.INFO)
    
    # Tạo và lưu danh sách từ dừng
    Config.init_directories()
    stopwords_file = Config.VIETNAMESE_STOPWORDS_PATH
    
    if not stopwords_file.exists():
        vietnamese_stopwords = [
            'là', 'của', 'và', 'có', 'được', 'một', 'trong', 'cho', 'với', 'này',
            'đó', 'những', 'các', 'để', 'từ', 'không', 'đã', 'sẽ', 'bị', 'bởi',
            'về', 'tại', 'lại', 'như', 'hay', 'hoặc', 'nếu', 'mà', 'khi', 'nào',
            'đâu', 'ai', 'gì', 'sao', 'thế', 'vậy', 'rất', 'lắm', 'nhiều', 'ít'
        ]
        
        with open(stopwords_file, 'w', encoding='utf-8') as f:
            for word in vietnamese_stopwords:
                f.write(word + '\n')
        
        print(f"Đã tạo file từ dừng tại: {stopwords_file}")
    
    # Build index
    builder = MovieIndexBuilder()
    
    # Thử load index có sẵn
    if builder.load_index():
        print("Đã load index có sẵn")
    else:
        print("Xây dựng index mới...")
        builder.build_index_from_database()
        builder.save_index()
        print("Hoàn thành xây dựng index")
    
    # Test search
    query = "phim hành động"
    results = builder.index.search(query, top_k=5)
    print(f"\nKết quả tìm kiếm cho '{query}':")
    for doc_id, score in results:
        print(f"Document {doc_id}: score = {score:.4f}")

if __name__ == "__main__":
    main()