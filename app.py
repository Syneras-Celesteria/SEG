"""
Ứng dụng Máy Tìm Kiếm Chuyên Sâu - Lĩnh Vực Phim Việt Nam
Main Flask Application Entry Point
"""

from flask import Flask, request, render_template, jsonify
import logging
import os
import sys
import io
from modules.module3_search_ranking.search_engine import SearchEngine
from config.settings import Config

if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

app = Flask(__name__)
app.config.from_object(Config)

app.jinja_env.globals.update(min=min)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

search_engine = SearchEngine()

@app.route('/')
def index():
    """Trang chủ với form tìm kiếm"""
    return render_template('index.html')

@app.route('/search')
def search():
    """Endpoint xử lý tìm kiếm"""
    query = request.args.get('q', '').strip()
    page = int(request.args.get('page', 1))
    
    if not query:
        return render_template('search_results.html', 
                             query='', 
                             results=[], 
                             total=0,
                             page=page)
    
    try:
        # Thực hiện tìm kiếm
        results, total = search_engine.search(query, page=page)
        
        # Log kết quả
        logger.info(f"Tìm kiếm: '{query}' - Tìm thấy {total} kết quả")
        
        return render_template('search_results.html',
                             query=query,
                             results=results,
                             total=total,
                             page=page)
                             
    except Exception as e:
        logger.error(f"Lỗi khi tìm kiếm: {str(e)}")
        return render_template('error.html', error="Có lỗi xảy ra khi tìm kiếm")

@app.route('/api/search')
def api_search():
    """API endpoint cho tìm kiếm"""
    query = request.args.get('q', '').strip()
    page = int(request.args.get('page', 1))
    
    if not query:
        return jsonify({'results': [], 'total': 0, 'page': page})
    
    try:
        results, total = search_engine.search(query, page=page)
        return jsonify({
            'query': query,
            'results': results,
            'total': total,
            'page': page
        })
    except Exception as e:
        logger.error(f"API search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/api/suggestions')
def api_suggestions():
    """API endpoint cho search suggestions"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'suggestions': []})
    
    try:
        suggestions = search_engine.get_suggestions(query, limit=5)
        return jsonify({'suggestions': suggestions})
    except Exception as e:
        logger.error(f"API suggestions error: {str(e)}")
        return jsonify({'suggestions': []})

@app.route('/api/popular-movies')
def api_popular_movies():
    """API endpoint cho phim phổ biến"""
    try:
        movies = search_engine.get_popular_movies(limit=12)
        return jsonify({'movies': movies})
    except Exception as e:
        logger.error(f"API popular movies error: {str(e)}")
        return jsonify({'movies': []})

@app.route('/api/movies-by-genre/<genre>')
def api_movies_by_genre(genre):
    """API endpoint cho phim theo thể loại"""
    try:
        movies = search_engine.get_movies_by_genre(genre, limit=10)
        return jsonify({'movies': movies, 'genre': genre})
    except Exception as e:
        logger.error(f"API movies by genre error: {str(e)}")
        return jsonify({'movies': [], 'genre': genre})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Vietnamese Movie Search Engine'})

if __name__ == '__main__':
    # Tạo thư mục logs nếu chưa có
    os.makedirs('logs', exist_ok=True)
    
    # Chạy ứng dụng
    app.run(
        host=app.config.get('HOST', '127.0.0.1'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', True)
    )