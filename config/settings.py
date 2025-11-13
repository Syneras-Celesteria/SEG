"""
Cấu hình chung cho ứng dụng Máy Tìm Kiếm
Configuration settings for the search engine application
"""

import os
from pathlib import Path

class Config:
    """Cấu hình cơ bản cho ứng dụng"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # Database settings
    BASE_DIR = Path(__file__).parent.parent
    DATABASE_PATH = BASE_DIR / 'data' / 'search_engine.db'
    
    # Crawling settings
    CRAWL_DELAY = 1  # Giây delay giữa các request
    MAX_PAGES_PER_SITE = 100
    ALLOWED_DOMAINS = [
        'motchill.cc',
        'motphim.net',
        'phimmoi.net'
    ]
    
    # Text processing settings
    VIETNAMESE_STOPWORDS_PATH = BASE_DIR / 'data' / 'vietnamese_stopwords.txt'
    MIN_WORD_LENGTH = 2
    MAX_WORD_LENGTH = 50
    
    # Search settings
    RESULTS_PER_PAGE = 10
    MAX_RESULTS = 1000
    MIN_SCORE_THRESHOLD = 0.1
    
    # TF-IDF settings
    MAX_DF = 0.85  # Bỏ qua từ xuất hiện trong >85% documents
    MIN_DF = 2     # Bỏ qua từ xuất hiện trong <2 documents
    MAX_FEATURES = 10000  # Số từ tối đa trong vocabulary
    
    # Evaluation settings
    GROUND_TRUTH_PATH = BASE_DIR / 'data' / 'ground_truth.json'
    PRECISION_K = 10  # Tính Precision@10
    
    # Logging settings
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # File paths
    RAW_DATA_PATH = BASE_DIR / 'data' / 'raw'
    PROCESSED_DATA_PATH = BASE_DIR / 'data' / 'processed'
    INDEX_PATH = BASE_DIR / 'data' / 'index'
    
    @classmethod
    def init_directories(cls):
        """Tạo các thư mục cần thiết"""
        directories = [
            cls.RAW_DATA_PATH,
            cls.PROCESSED_DATA_PATH,
            cls.INDEX_PATH,
            cls.BASE_DIR / 'logs'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(Config):
    """Cấu hình cho môi trường development"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Cấu hình cho môi trường production"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
class TestingConfig(Config):
    """Cấu hình cho testing"""
    TESTING = True
    DATABASE_PATH = ':memory:'  # SQLite in-memory database for testing

# Mapping các môi trường
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}