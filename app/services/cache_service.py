from functools import wraps
from flask import current_app
import json
import hashlib

class CacheService:
    """간단한 메모리 캐시 서비스 (향후 Redis로 확장 가능)"""
    
    def __init__(self):
        self.cache = {}
        self.max_size = 1000
    
    def _generate_key(self, prefix, *args, **kwargs):
        """캐시 키 생성"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key):
        """캐시에서 값 조회"""
        return self.cache.get(key)
    
    def set(self, key, value, timeout=300):
        """캐시에 값 저장"""
        if len(self.cache) >= self.max_size:
            # LRU 방식으로 가장 오래된 항목 제거
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'value': value,
            'expires_at': timeout  # 간단 구현, 실제로는 시간 기반
        }
    
    def delete(self, key):
        """캐시에서 값 제거"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """전체 캐시 제거"""
        self.cache.clear()

# 전역 캐시 인스턴스
cache_service = CacheService()

def cached(timeout=300, key_prefix='cache'):
    """함수 결과를 캐시하는 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = cache_service._generate_key(
                f"{key_prefix}:{func.__name__}", *args, **kwargs
            )
            
            # 캐시에서 조회
            cached_result = cache_service.get(cache_key)
            if cached_result:
                return cached_result['value']
            
            # 함수 실행 및 결과 캐시
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator