"""
Module 5: Evaluation System
Đánh giá hiệu quả của hệ thống tìm kiếm
ĐÃ CẬP NHẬT TEST SCENARIOS KHỚP VỚI CRAWLER
"""

import json
import sqlite3
from typing import List, Dict, Tuple, Set
import logging
from pathlib import Path
import sys
import io
import numpy as np
from collections import defaultdict
import os

# Thêm path để import config và modules khác
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import Config
from modules.module3_search_ranking.search_engine import SearchEngine

# [FIX] Sửa lỗi hiển thị tiếng Việt trên Windows Console
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class SearchEvaluator:
    """Đánh giá hiệu quả tìm kiếm"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.search_engine = SearchEngine()
        self.ground_truth_path = Config.GROUND_TRUTH_PATH
        self.db_path = Config.DATABASE_PATH
        
        # Load ground truth data (Nếu chưa có sẽ tự tạo từ DB thật)
        self.ground_truth = self.load_ground_truth()
    
    def load_ground_truth(self) -> Dict[str, List[int]]:
        """Load ground truth data"""
        try:
            self.logger.info("Đang tạo Ground Truth từ dữ liệu thực tế trong Database...")
            return self.create_real_ground_truth_from_db()
        except Exception as e:
            self.logger.error(f"Error loading ground truth: {e}")
            return {}
    
    def create_real_ground_truth_from_db(self) -> Dict[str, List[int]]:
        """
        Tạo Ground Truth dựa trên dữ liệu THẬT trong SQLite.
        Danh sách test được đồng bộ với Crawler.
        """
        ground_truth = {}
        
        # === DANH SÁCH QUERY TEST (Đồng bộ với Crawler) ===
        # Key: Từ khóa tìm kiếm (User search)
        # Value: Điều kiện SQL để xác định kết quả đúng (Ground Truth)
        test_scenarios = {
            # --- Thể loại (Theo crawler categories) ---
            "Cổ trang": "LOWER(genre) LIKE '%cổ trang%'",
            "Chính kịch": "LOWER(genre) LIKE '%chính kịch%'",
            "Bí ẩn": "LOWER(genre) LIKE '%bí ẩn%'",
            "Gia đình": "LOWER(genre) LIKE '%gia đình%'",
            "Hài hước": "LOWER(genre) LIKE '%hài%'",
            "Hành động": "LOWER(genre) LIKE '%hành động%'",
            "Hình sự": "LOWER(genre) LIKE '%hình sự%'",
            "Khoa học": "LOWER(genre) LIKE '%khoa học%'",
            "Kinh dị": "LOWER(genre) LIKE '%kinh dị%'",
            "Phiêu lưu": "LOWER(genre) LIKE '%phiêu lưu%'",
            "Tâm lý": "LOWER(genre) LIKE '%tâm lý%'",
            "Tình cảm": "LOWER(genre) LIKE '%tình cảm%'",
            "Viễn tưởng": "LOWER(genre) LIKE '%viễn tưởng%'",
            "Võ thuật": "LOWER(genre) LIKE '%võ thuật%'",
            
            # --- Quốc gia ---
            "Trung Quốc": "LOWER(country) LIKE '%trung quốc%'",
            "Hàn Quốc": "LOWER(country) LIKE '%hàn quốc%'",
            "Thái Lan": "LOWER(country) LIKE '%thái lan%'",
            "Âu Mỹ": "LOWER(country) LIKE '%âu mỹ%' OR LOWER(country) LIKE '%mỹ%'",
            "Việt Nam": "LOWER(country) LIKE '%việt nam%'",
            
            # --- Năm phát hành ---
            "2024": "year = 2024",
            "2025": "year = 2025"
        }

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for query_text, sql_condition in test_scenarios.items():
                # Tìm tất cả ID phim thỏa mãn điều kiện
                sql = f"SELECT id FROM movies WHERE {sql_condition}"
                cursor.execute(sql)
                ids = [row[0] for row in cursor.fetchall()]
                
                # Chỉ thêm vào bài test nếu database có ít nhất 1 phim thuộc loại này
                if ids:
                    ground_truth[query_text] = ids
                else:
                    # Log warning để biết database đang thiếu thể loại nào
                    pass 
                    # self.logger.warning(f"Skip '{query_text}': Không có dữ liệu trong DB")

            conn.close()

            # Lưu file JSON để backup/debug
            Config.init_directories()
            with open(self.ground_truth_path, 'w', encoding='utf-8') as f:
                json.dump(ground_truth, f, ensure_ascii=False, indent=2)
            
            return ground_truth

        except Exception as e:
            self.logger.error(f"Lỗi khi tạo Ground Truth từ DB: {e}")
            return {}
    
    def calculate_metrics(self, query: str, k: int = 10) -> Dict[str, float]:
        """Tính toán các chỉ số: Precision, Recall, F1, AP"""
        if query not in self.ground_truth:
            return {}
        
        # 1. Search Engine thực hiện tìm kiếm
        results, _ = self.search_engine.search(query, page=1, per_page=k)
        retrieved_ids = [r['id'] for r in results]
        
        # 2. Lấy danh sách đáp án đúng (Ground Truth)
        relevant_ids = set(self.ground_truth[query])
        if not relevant_ids: 
            return {}

        # --- Tính toán ---
        relevant_retrieved = sum(1 for doc_id in retrieved_ids if doc_id in relevant_ids)
        
        precision = relevant_retrieved / len(retrieved_ids) if retrieved_ids else 0.0
        recall = relevant_retrieved / len(relevant_ids)
        
        f1 = 0.0
        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
            
        # Average Precision (AP)
        hits = 0
        sum_precisions = 0
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in relevant_ids:
                hits += 1
                sum_precisions += hits / (i + 1.0)
        
        ap = sum_precisions / min(len(relevant_ids), k) if relevant_ids else 0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "ap": ap,
            "retrieved_count": len(retrieved_ids),
            "relevant_count": len(relevant_ids)
        }

    def evaluate_system(self):
        """Chạy đánh giá và in báo cáo"""
        print("\n" + "="*85)
        print(f"BÁO CÁO ĐÁNH GIÁ HỆ THỐNG MÁY TÌM KIẾM (Top-K = {Config.RESULTS_PER_PAGE})")
        print("="*85)
        print(f"{'Query (Truy vấn)':<20} | {'P@10':<8} | {'R@10':<8} | {'MAP':<8} | {'Kết quả tìm/Tổng đúng'}")
        print("-" * 85)
        
        total_ap = 0
        count = 0
        
        # Sắp xếp query theo alphabet để dễ nhìn
        sorted_queries = sorted(self.ground_truth.keys())
        
        for query in sorted_queries:
            metrics = self.calculate_metrics(query, k=10)
            if not metrics:
                continue
                
            print(f"{query:<20} | {metrics['precision']:.2f}     | {metrics['recall']:.2f}     | {metrics['ap']:.2f}     | {metrics['retrieved_count']}/{metrics['relevant_count']} docs")
            
            total_ap += metrics['ap']
            count += 1
            
        print("-" * 85)
        mean_map = total_ap / count if count > 0 else 0
        print(f"ĐIỂM TRUNG BÌNH TOÀN HỆ THỐNG (Mean MAP): {mean_map:.4f}")
        print("="*85)
        
        if mean_map > 0.7:
            print("=> ĐÁNH GIÁ: XUẤT SẮC (Hệ thống tìm kiếm rất chính xác)")
        elif mean_map > 0.4:
            print("=> ĐÁNH GIÁ: TỐT (Hệ thống hoạt động ổn định)")
        else:
            print("=> ĐÁNH GIÁ: CẦN CẢI THIỆN (Độ chính xác chưa cao)")

def main():
    """Hàm main"""
    # Tắt log rác
    logging.getLogger('modules.module3_search_ranking.search_engine').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO)
    
    evaluator = SearchEvaluator()
    if not evaluator.ground_truth:
        print("CẢNH BÁO: Chưa có dữ liệu trong Database để đánh giá!")
        print("Vui lòng chạy module crawler trước: python modules/module1_crawling/crawler.py")
        return

    evaluator.evaluate_system()

if __name__ == "__main__":
    main()