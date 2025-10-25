"""
항공사진 캐싱 시스템
서버 사이드 캐싱으로 VWorld API 호출 최소화 및 응답 속도 향상
"""

import os
import time
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import shutil


class AerialImageCache:
    """
    항공사진 캐시 관리 클래스

    Features:
    - 24시간 TTL (Time To Live)
    - 자동 캐시 정리
    - 디스크 용량 관리
    - 캐시 통계
    """

    def __init__(self, cache_dir: str = "cache/aerial_images", ttl_hours: int = 24, max_size_gb: float = 5.0):
        """
        Args:
            cache_dir: 캐시 디렉토리 경로
            ttl_hours: 캐시 유효 시간 (시간)
            max_size_gb: 최대 캐시 크기 (GB)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_dir = self.cache_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)

        self.ttl_seconds = ttl_hours * 3600
        self.max_size_bytes = int(max_size_gb * 1024 * 1024 * 1024)

        # 통계 파일
        self.stats_file = self.cache_dir / "cache_stats.json"
        self._load_stats()

    def _load_stats(self):
        """캐시 통계 로드"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                "hits": 0,
                "misses": 0,
                "total_requests": 0,
                "total_saved_bytes": 0,
                "last_cleanup": None
            }

    def _save_stats(self):
        """캐시 통계 저장"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def _get_cache_key(self, latitude: float, longitude: float, zoom: int, width: int = 3, height: int = 3) -> str:
        """
        캐시 키 생성 (좌표 + 줌 레벨 + 크기)

        Args:
            latitude: 위도
            longitude: 경도
            zoom: 줌 레벨
            width: 타일 가로 개수
            height: 타일 세로 개수

        Returns:
            캐시 키 (해시값)
        """
        # 좌표를 소수점 4자리로 반올림 (약 11m 정확도)
        lat_rounded = round(latitude, 4)
        lon_rounded = round(longitude, 4)

        # 캐시 키 생성
        key_str = f"{lat_rounded}_{lon_rounded}_z{zoom}_w{width}_h{height}"

        # MD5 해시로 파일명 안전하게 생성
        key_hash = hashlib.md5(key_str.encode()).hexdigest()

        return key_hash

    def get(self, latitude: float, longitude: float, zoom: int, width: int = 3, height: int = 3) -> Optional[bytes]:
        """
        캐시에서 이미지 가져오기

        Args:
            latitude: 위도
            longitude: 경도
            zoom: 줌 레벨
            width: 타일 가로 개수
            height: 타일 세로 개수

        Returns:
            이미지 데이터 (bytes) 또는 None (캐시 미스)
        """
        self.stats["total_requests"] += 1

        cache_key = self._get_cache_key(latitude, longitude, zoom, width, height)
        cache_file = self.cache_dir / f"{cache_key}.jpg"
        metadata_file = self.metadata_dir / f"{cache_key}.json"

        # 캐시 파일 존재 확인
        if not cache_file.exists():
            self.stats["misses"] += 1
            self._save_stats()
            return None

        # 캐시 메타데이터 확인
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

            # TTL 확인
            created_at = datetime.fromisoformat(metadata['created_at'])
            age = datetime.now() - created_at

            if age.total_seconds() > self.ttl_seconds:
                # 캐시 만료
                self._delete_cache_entry(cache_key)
                self.stats["misses"] += 1
                self._save_stats()
                return None

        # 캐시 히트!
        try:
            with open(cache_file, 'rb') as f:
                image_data = f.read()

            self.stats["hits"] += 1
            self._save_stats()

            print(f"✅ Cache HIT: {cache_key} ({len(image_data) / 1024:.1f} KB)")
            return image_data

        except Exception as e:
            print(f"❌ Cache read error: {e}")
            self.stats["misses"] += 1
            self._save_stats()
            return None

    def set(
        self,
        latitude: float,
        longitude: float,
        zoom: int,
        image_data: bytes,
        width: int = 3,
        height: int = 3,
        metadata: Dict = None
    ) -> bool:
        """
        이미지를 캐시에 저장

        Args:
            latitude: 위도
            longitude: 경도
            zoom: 줌 레벨
            image_data: 이미지 데이터
            width: 타일 가로 개수
            height: 타일 세로 개수
            metadata: 추가 메타데이터

        Returns:
            저장 성공 여부
        """
        try:
            cache_key = self._get_cache_key(latitude, longitude, zoom, width, height)
            cache_file = self.cache_dir / f"{cache_key}.jpg"
            metadata_file = self.metadata_dir / f"{cache_key}.json"

            # 이미지 저장
            with open(cache_file, 'wb') as f:
                f.write(image_data)

            # 메타데이터 저장
            meta = {
                "latitude": latitude,
                "longitude": longitude,
                "zoom": zoom,
                "width": width,
                "height": height,
                "size_bytes": len(image_data),
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(seconds=self.ttl_seconds)).isoformat()
            }

            if metadata:
                meta.update(metadata)

            with open(metadata_file, 'w') as f:
                json.dump(meta, f, indent=2)

            self.stats["total_saved_bytes"] += len(image_data)
            self._save_stats()

            print(f"💾 Cache SET: {cache_key} ({len(image_data) / 1024:.1f} KB)")

            # 캐시 크기 확인 및 정리
            self._check_and_cleanup_size()

            return True

        except Exception as e:
            print(f"❌ Cache write error: {e}")
            return False

    def _delete_cache_entry(self, cache_key: str):
        """캐시 항목 삭제"""
        cache_file = self.cache_dir / f"{cache_key}.jpg"
        metadata_file = self.metadata_dir / f"{cache_key}.json"

        if cache_file.exists():
            cache_file.unlink()
        if metadata_file.exists():
            metadata_file.unlink()

    def cleanup_expired(self) -> int:
        """
        만료된 캐시 정리

        Returns:
            삭제된 캐시 개수
        """
        deleted_count = 0
        now = datetime.now()

        for metadata_file in self.metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                created_at = datetime.fromisoformat(metadata['created_at'])
                age = now - created_at

                if age.total_seconds() > self.ttl_seconds:
                    cache_key = metadata_file.stem
                    self._delete_cache_entry(cache_key)
                    deleted_count += 1

            except Exception as e:
                print(f"⚠️  Error processing {metadata_file}: {e}")

        self.stats["last_cleanup"] = now.isoformat()
        self._save_stats()

        print(f"🧹 Cleaned up {deleted_count} expired cache entries")
        return deleted_count

    def _check_and_cleanup_size(self):
        """디스크 용량 초과 시 오래된 캐시부터 삭제"""
        total_size = self.get_cache_size()

        if total_size > self.max_size_bytes:
            print(f"⚠️  Cache size ({total_size / 1024 / 1024:.1f} MB) exceeds limit. Cleaning up...")

            # 모든 캐시 항목을 생성 시간 순으로 정렬
            cache_entries = []
            for metadata_file in self.metadata_dir.glob("*.json"):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    cache_entries.append((
                        datetime.fromisoformat(metadata['created_at']),
                        metadata_file.stem,
                        metadata['size_bytes']
                    ))
                except:
                    pass

            cache_entries.sort()  # 오래된 것부터

            # 용량이 제한 이하로 떨어질 때까지 삭제
            for created_at, cache_key, size_bytes in cache_entries:
                if total_size <= self.max_size_bytes * 0.8:  # 80%까지 줄이기
                    break

                self._delete_cache_entry(cache_key)
                total_size -= size_bytes
                print(f"  Deleted old cache: {cache_key}")

    def get_cache_size(self) -> int:
        """현재 캐시 크기 (bytes)"""
        total_size = 0
        for cache_file in self.cache_dir.glob("*.jpg"):
            total_size += cache_file.stat().st_size
        return total_size

    def get_stats(self) -> Dict:
        """캐시 통계 반환"""
        total_size = self.get_cache_size()
        cache_count = len(list(self.cache_dir.glob("*.jpg")))

        hit_rate = 0
        if self.stats["total_requests"] > 0:
            hit_rate = (self.stats["hits"] / self.stats["total_requests"]) * 100

        return {
            "total_requests": self.stats["total_requests"],
            "cache_hits": self.stats["hits"],
            "cache_misses": self.stats["misses"],
            "hit_rate_percent": round(hit_rate, 2),
            "cache_count": cache_count,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "max_size_mb": round(self.max_size_bytes / 1024 / 1024, 2),
            "ttl_hours": self.ttl_seconds / 3600,
            "last_cleanup": self.stats["last_cleanup"]
        }

    def clear_all(self) -> int:
        """모든 캐시 삭제"""
        count = 0
        for cache_file in self.cache_dir.glob("*.jpg"):
            cache_file.unlink()
            count += 1

        for metadata_file in self.metadata_dir.glob("*.json"):
            metadata_file.unlink()

        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0,
            "total_saved_bytes": 0,
            "last_cleanup": datetime.now().isoformat()
        }
        self._save_stats()

        print(f"🗑️  Cleared {count} cache entries")
        return count


# 싱글톤 인스턴스
_cache_instance = None

def get_cache() -> AerialImageCache:
    """캐시 인스턴스 가져오기 (싱글톤)"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = AerialImageCache(
            cache_dir="cache/aerial_images",
            ttl_hours=24,  # 24시간 TTL
            max_size_gb=5.0  # 최대 5GB
        )
    return _cache_instance


# 테스트
if __name__ == "__main__":
    cache = AerialImageCache()

    print("=" * 60)
    print("항공사진 캐싱 시스템 테스트")
    print("=" * 60)

    # 테스트 데이터
    test_lat = 37.5172
    test_lon = 127.0473
    test_zoom = 18
    test_image = b"test image data" * 1000  # 가짜 이미지 데이터

    # 캐시 저장
    print("\n[테스트 1] 캐시 저장")
    cache.set(test_lat, test_lon, test_zoom, test_image)

    # 캐시 조회 (히트)
    print("\n[테스트 2] 캐시 조회 (히트)")
    result = cache.get(test_lat, test_lon, test_zoom)
    print(f"결과: {'성공' if result else '실패'}")

    # 캐시 조회 (미스)
    print("\n[테스트 3] 캐시 조회 (미스)")
    result = cache.get(37.5555, 127.0555, test_zoom)
    print(f"결과: {'캐시 없음' if not result else '캐시 있음'}")

    # 통계
    print("\n[테스트 4] 캐시 통계")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
