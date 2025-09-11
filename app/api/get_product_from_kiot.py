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
        
        # Cache - chỉ dùng cache chính, bỏ name_index
        self.product_cache = {}  # {product_name: (retailerId, code, price)}
        self.cache_file = "kiot_product_cache.pkl"
        self.cache_expiry_hours = 24
        
        # Load cache if exists
        self.load_cache()
    
    def save_cache(self):
        """Lưu cache vào file"""
        cache_data = {
            'product_cache': self.product_cache,
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
                
                # Kiểm tra cache có hết hạn không
                cache_time = cache_data.get('timestamp', datetime.now())
                if datetime.now() - cache_time < timedelta(hours=self.cache_expiry_hours):
                    self.product_cache = cache_data.get('product_cache', {})
                    print(f"✅ Cache loaded với {len(self.product_cache)} sản phẩm")
                else:
                    print("⚠️ Cache đã hết hạn, sẽ rebuild lại")
        except Exception as e:
            print(f"❌ Lỗi khi load cache: {e}")
    
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
                
                # Thêm vào cache - sử dụng tên gốc
                for product in products:
                    name = product.get("name", "").strip()
                    product_id = product.get("id")
                    code = product.get("code")
                    product_price = product.get("basePrice")
                    
                    if name and product_id and code:
                        # Cache với tên gốc không normalize
                        self.product_cache[name] = (product_id, code, product_price)
                
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
        """Tìm kiếm chính xác theo tên - không normalize"""
        # Tìm chính xác theo tên gốc
        if product_name in self.product_cache:
            return self.product_cache[product_name]
        
        # Tìm case-insensitive
        for cached_name, value in self.product_cache.items():
            if cached_name.lower() == product_name.lower():
                return value
        
        return None
    
    def normalize_for_search(self, text: str) -> str:
        """Normalize chỉ để tìm kiếm fuzzy - bỏ dấu tiếng Việt và khoảng trắng thừa"""
        import unicodedata
        # Bỏ dấu tiếng Việt
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        # Lowercase và bỏ khoảng trắng thừa
        return text.lower().strip()
    
    def search_fuzzy(self, product_name: str) -> List[Tuple[str, int, str, float]]:
        """Tìm kiếm mờ (fuzzy search) - có xử lý dấu tiếng Việt"""
        results = []
        search_lower = product_name.lower()
        search_normalized = self.normalize_for_search(product_name)
        print(f"search product name == {search_lower}")
        print(f"search normalized == {search_normalized}")
        
        for cached_name, (id, code, price) in self.product_cache.items():
            cached_lower = cached_name.lower()
            cached_normalized = self.normalize_for_search(cached_name)
            
            # Kiểm tra substring với 2 cách:
            # 1. So sánh trực tiếp (giữ nguyên dấu)
            direct_match = search_lower in cached_lower or cached_lower in search_lower
            
            # 2. So sánh sau khi bỏ dấu (cho trường hợp thiếu/sai dấu)
            normalized_match = search_normalized in cached_normalized or cached_normalized in search_normalized
            
            if direct_match or normalized_match:
                results.append((cached_name, id, code, price))
        
        return results[:10]  # Giới hạn 10 kết quả
    
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
                    self.product_cache[name] = (product_id, code, product_price)
            
            # Tìm chính xác trong kết quả
            for product in products:
                if product.get("name", "").lower() == product_name.lower():
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
    1. Cache chính xác (không normalize)
    2. Cache fuzzy (không normalize)
    3. API fallback
    
    Returns:
        Tuple[int, str, float]: (ProductId, code, price) hoặc None
    """
    if not _searcher_instance:
        raise ValueError("Searcher chưa được khởi tạo. Gọi initialize_searcher() trước.")
    
    print(f"🔍 Tìm kiếm: '{product_name}'")
    
    # Strategy 1: Tìm chính xác trong cache (không normalize)
    result = _searcher_instance.search_exact(product_name)
    if result:
        print(f"✅ Tìm thấy chính xác: ProductId={result[0]}, code={result[1]}, price={result[2]}")
        return result
    
    # Strategy 2: Tìm fuzzy trong cache (không normalize)
    fuzzy_results = _searcher_instance.search_fuzzy(product_name)
    if fuzzy_results:
        # Lấy kết quả đầu tiên (có thể là gần nhất)
        best_match = fuzzy_results[0]
        print(f"✅ Tìm thấy fuzzy: '{best_match[0]}' -> ProductId={best_match[1]}, code={best_match[2]}, price={best_match[3]}")
        print(f"📋 Tất cả fuzzy matches: {[r[0] for r in fuzzy_results]}")
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
        "cache_file": _searcher_instance.cache_file,
        "cache_exists": os.path.exists(_searcher_instance.cache_file)
    }