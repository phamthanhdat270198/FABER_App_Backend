import requests
import json
import time
from typing import Dict, List, Tuple, Optional
from functools import lru_cache
import threading
import pickle
import os
from datetime import datetime, timedelta

class FastProductSearcher:
    def __init__(self, access_token: str, retailer: str):
        self.access_token = access_token
        self.retailer = retailer
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Retailer": retailer,
            "Content-Type": "application/json"
        }
        
        # Cache chính và cache normalized để tìm kiếm nhanh
        self.product_cache = {}  # {product_name: (retailerId, code, price)}
        self.normalized_cache = {}  # {normalized_name: original_name} - để map ngược lại
        self.cache_file = "kiot_product_cache.pkl"
        self.cache_expiry_hours = 24
        
        # Load cache if exists
        self.load_cache()
    
    def save_cache(self):
        """Lưu cache vào file"""
        cache_data = {
            'product_cache': self.product_cache,
            'normalized_cache': self.normalized_cache,
            'timestamp': datetime.now()
        }
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            print(f"✅ Cache đã được lưu với {len(self.product_cache)} sản phẩm")
        except Exception as e:
            print(f"❌ Lỗi khi lưu cache: {e}")
    
    def load_cache(self):
        """Load cache từ file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                self.product_cache = cache_data.get('product_cache', {})
                self.normalized_cache = cache_data.get('normalized_cache', {})
                print(f"✅ Cache loaded với {len(self.product_cache)} sản phẩm")
        except Exception as e:
            print(f"❌ Lỗi khi load cache: {e}")
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text để tìm kiếm:
        - Bỏ dấu tiếng Việt
        - Lowercase
        - Bỏ khoảng trắng thừa
        - Giữ nguyên số và ký tự đặc biệt
        """
        import unicodedata
        
        # Bỏ dấu tiếng Việt
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        
        # Lowercase và normalize khoảng trắng
        text = text.lower().strip()
        text = text.replace('-', '')  # Bỏ dấu gạch ngang
        text = ' '.join(text.split())  # Bỏ khoảng trắng thừa
        
        return text
    
    def build_product_cache(self):
        """Xây dựng cache từ tất cả sản phẩm"""
        print("🚀 Bắt đầu xây dựng product cache...")
        
        url = "https://public.kiotapi.com/products"
        current_item = 0
        page_size = 100
        
        while True:
            params = {
                "pageSize": page_size,
                "currentItem": current_item,
                "isActive": True,
                "orderBy": "id",
                "orderDirection": "asc"
            }
            
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                products = data.get("data", [])
                
                if not products:
                    break
                
                # Thêm vào cache
                for product in products:
                    name = product.get("name", "").strip()
                    product_id = product.get("id")
                    code = product.get("code")
                    product_price = product.get("basePrice")
                    
                    if name and product_id and code:
                        # Cache chính với tên gốc
                        self.product_cache[name] = (product_id, code, product_price)
                        
                        # Cache normalized để tìm kiếm nhanh
                        normalized_name = self.normalize_text(name)
                        self.normalized_cache[normalized_name] = name
                
                print(f"✅ Processed {len(products)} products (Total: {len(self.product_cache)})")
                current_item += len(products)
                
                if len(products) < page_size:
                    break
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Lỗi khi build cache: {e}")
                break
        
        # Lưu cache
        self.save_cache()
        print(f"🎉 Cache hoàn thành với {len(self.product_cache)} sản phẩm!")
    
    def search_exact(self, product_name: str) -> Optional[Tuple[int, str, float]]:
        """Tìm kiếm chính xác theo tên"""
        # 1. Tìm chính xác theo tên gốc
        if product_name in self.product_cache:
            return self.product_cache[product_name]
        
        # 2. Tìm case-insensitive với tên gốc
        for cached_name, value in self.product_cache.items():
            if cached_name.lower() == product_name.lower():
                return value
        
        # 3. Tìm theo normalized name (bỏ dấu)
        normalized_search = self.normalize_text(product_name)
        if normalized_search in self.normalized_cache:
            original_name = self.normalized_cache[normalized_search]
            return self.product_cache[original_name]
        
        return None
    
    def search_fuzzy(self, product_name: str) -> List[Tuple[str, int, str, float]]:
        """Tìm kiếm mờ (fuzzy search) với xử lý dấu tiếng Việt"""
        results = []
        search_lower = product_name.lower()
        search_normalized = self.normalize_text(product_name)
        
        print(f"🔍 Search lower: '{search_lower}'")
        print(f"🔍 Search normalized: '{search_normalized}'")
        
        for cached_name, (product_id, code, price) in self.product_cache.items():
            cached_lower = cached_name.lower()
            cached_normalized = self.normalize_text(cached_name)
            
            # Kiểm tra substring với 3 cách:
            # 1. So sánh trực tiếp (giữ nguyên dấu, case-insensitive)
            direct_match = search_lower in cached_lower or cached_lower in search_lower
            
            # 2. So sánh sau khi normalize (bỏ dấu)
            normalized_match = search_normalized in cached_normalized or cached_normalized in search_normalized
            
            # 3. Kiểm tra từ khóa chính (cho trường hợp tìm "AP100" -> tìm thấy "AP100-1 ...")
            main_keywords_search = search_normalized.split()
            main_keywords_cached = cached_normalized.split()
            keyword_match = any(kw in cached_normalized for kw in main_keywords_search if len(kw) >= 3)
            
            if direct_match or normalized_match or keyword_match:
                # Tính điểm ưu tiên (càng khớp nhiều càng cao)
                score = 0
                if direct_match:
                    score += 10
                if normalized_match:
                    score += 5
                if search_normalized == cached_normalized:
                    score += 20  # Khớp hoàn toàn
                if search_lower == cached_lower:
                    score += 25  # Khớp hoàn toàn không normalize
                
                results.append((cached_name, product_id, code, price, score))
        
        # Sắp xếp theo điểm từ cao đến thấp
        results.sort(key=lambda x: x[4], reverse=True)
        
        # Trả về không có score
        return [(name, pid, code, price) for name, pid, code, price, _ in results[:10]]
    
    def search_api_fallback(self, product_name: str) -> Optional[Tuple[int, str, float]]:
        """Tìm kiếm qua API nếu cache không có"""
        url = "https://public.kiotapi.com/products"
        params = {
            "name": product_name,
            "pageSize": 50,
            "isActive": True
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            products = data.get("data", [])
            
            # Cập nhật cache với kết quả mới
            for product in products:
                name = product.get("name", "").strip()
                product_id = product.get("id")
                code = product.get("code")
                product_price = product.get("basePrice")
                
                if name and product_id and code:
                    # Cập nhật cả cache chính và normalized cache
                    self.product_cache[name] = (product_id, code, product_price)
                    normalized_name = self.normalize_text(name)
                    self.normalized_cache[normalized_name] = name
            
            # Tìm chính xác trong kết quả mới
            for product in products:
                product_name_api = product.get("name", "")
                if (product_name_api.lower() == product_name.lower() or 
                    self.normalize_text(product_name_api) == self.normalize_text(product_name)):
                    return (product.get("id"), product.get("code"), product.get("basePrice"))
            
            return None
            
        except Exception as e:
            print(f"❌ Lỗi API fallback: {e}")
            return None

# Wrapper functions để sử dụng dễ dàng
_searcher_instance = None

def initialize_searcher(access_token: str, retailer: str, rebuild_cache: bool = False):
    """Khởi tạo searcher và build cache nếu cần"""
    global _searcher_instance
    _searcher_instance = FastProductSearcher(access_token, retailer)
    
    # Build cache nếu chưa có hoặc yêu cầu rebuild
    if rebuild_cache or len(_searcher_instance.product_cache) == 0:
        _searcher_instance.build_product_cache()

def find_product_fast(product_name: str) -> Optional[Tuple[int, str, float]]:
    """
    Tìm sản phẩm nhanh nhất với các strategy:
    1. Cache exact (bao gồm cả normalized)
    2. Cache fuzzy (với scoring)
    3. API fallback
    
    Returns:
        Tuple[int, str, float]: (ProductId, code, price) hoặc None
    """
    if not _searcher_instance:
        raise ValueError("Searcher chưa được khởi tạo. Gọi initialize_searcher() trước.")
    
    print(f"🔍 Tìm kiếm: '{product_name}'")
    
    # Strategy 1: Tìm chính xác (bao gồm normalized)
    result = _searcher_instance.search_exact(product_name)
    if result:
        print(f"✅ Tìm thấy chính xác: ProductId={result[0]}, code={result[1]}, price={result[2]}")
        return result
    
    # Strategy 2: Tìm fuzzy với scoring
    fuzzy_results = _searcher_instance.search_fuzzy(product_name)
    if fuzzy_results:
        best_match = fuzzy_results[0]
        print(f"✅ Tìm thấy fuzzy: '{best_match[0]}' -> ProductId={best_match[1]}, code={best_match[2]}, price={best_match[3]}")
        print(f"📋 Tất cả fuzzy matches: {[r[0] for r in fuzzy_results[:5]]}")  # Chỉ show 5 kết quả đầu
        return (best_match[1], best_match[2], best_match[3])
    
    # Strategy 3: API fallback
    print("🌐 Cache miss, tìm kiếm qua API...")
    result = _searcher_instance.search_api_fallback(product_name)
    if result:
        print(f"✅ API fallback success: ProductId={result[0]}, code={result[1]}, price={result[2]}")
        return result
    
    print(f"❌ Không tìm thấy sản phẩm: '{product_name}'")
    return None

def get_cache_stats():
    """Lấy thống kê cache"""
    if not _searcher_instance:
        return "Searcher chưa được khởi tạo"
    
    return {
        "total_products": len(_searcher_instance.product_cache),
        "normalized_entries": len(_searcher_instance.normalized_cache),
        "cache_file": _searcher_instance.cache_file,
        "cache_exists": os.path.exists(_searcher_instance.cache_file)
    }

def rebuild_cache_if_needed():
    """Rebuild cache nếu cần thiết"""
    if not _searcher_instance:
        print("❌ Searcher chưa được khởi tạo")
        return
    
    if len(_searcher_instance.normalized_cache) == 0:
        print("🔄 Rebuilding cache với normalized support...")
        _searcher_instance.build_product_cache()