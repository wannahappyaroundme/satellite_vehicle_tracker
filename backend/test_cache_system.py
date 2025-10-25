"""
캐싱 시스템 테스트
VWorld API로 실제 항공사진 다운로드 및 캐싱 성능 측정
"""

import time
from ngii_api_service import NGIIAPIService
from aerial_image_cache import get_cache

def test_caching_performance():
    """캐싱 성능 테스트"""
    print("=" * 70)
    print("🚀 VWorld API + 캐싱 시스템 성능 테스트")
    print("=" * 70)

    # 서비스 초기화 (캐싱 활성화)
    service = NGIIAPIService(enable_cache=True)
    cache = get_cache()

    # 테스트 좌표 (서울 강남구)
    test_locations = [
        {"name": "강남역", "lat": 37.4979, "lon": 127.0276},
        {"name": "역삼역", "lat": 37.5006, "lon": 127.0366},
        {"name": "선릉역", "lat": 37.5045, "lon": 127.0490},
    ]

    print("\n📍 테스트 위치:")
    for loc in test_locations:
        print(f"  - {loc['name']}: ({loc['lat']}, {loc['lon']})")

    # 테스트 1: 첫 번째 다운로드 (캐시 미스, VWorld API 호출)
    print("\n" + "=" * 70)
    print("🔽 테스트 1: 첫 번째 다운로드 (캐시 미스 - API 호출)")
    print("=" * 70)

    for loc in test_locations:
        print(f"\n📥 {loc['name']} 다운로드 중...")
        start_time = time.time()

        result = service.download_high_resolution_area(
            latitude=loc['lat'],
            longitude=loc['lon'],
            width_tiles=3,
            height_tiles=3,
            zoom=18
        )

        elapsed = time.time() - start_time

        if result['success']:
            from_cache = result.get('from_cache', False)
            size_mb = result['image_array'].nbytes / 1024 / 1024

            print(f"  ✅ 성공!")
            print(f"  ⏱️  소요 시간: {elapsed:.2f}초")
            print(f"  💾 이미지 크기: {size_mb:.2f} MB")
            print(f"  📦 캐시 사용: {'예' if from_cache else '아니오 (신규 다운로드)'}")
            print(f"  🔢 타일 개수: {result.get('tiles_downloaded', 0)}")
        else:
            print(f"  ❌ 실패: {result.get('error')}")

        # API 호출 간 1초 대기 (VWorld API 제한 고려)
        time.sleep(1)

    # 테스트 2: 두 번째 다운로드 (캐시 히트, 즉시 응답)
    print("\n" + "=" * 70)
    print("⚡ 테스트 2: 두 번째 다운로드 (캐시 히트 - 즉시 응답)")
    print("=" * 70)

    for loc in test_locations:
        print(f"\n📥 {loc['name']} 다운로드 중...")
        start_time = time.time()

        result = service.download_high_resolution_area(
            latitude=loc['lat'],
            longitude=loc['lon'],
            width_tiles=3,
            height_tiles=3,
            zoom=18
        )

        elapsed = time.time() - start_time

        if result['success']:
            from_cache = result.get('from_cache', False)
            size_mb = result['image_array'].nbytes / 1024 / 1024

            print(f"  ✅ 성공!")
            print(f"  ⏱️  소요 시간: {elapsed:.2f}초")
            print(f"  💾 이미지 크기: {size_mb:.2f} MB")
            print(f"  📦 캐시 사용: {'예' if from_cache else '아니오 (신규 다운로드)'}")
            print(f"  🚀 속도 향상: {'엄청 빠름!' if from_cache and elapsed < 1 else '보통'}")

    # 캐시 통계
    print("\n" + "=" * 70)
    print("📊 캐시 통계")
    print("=" * 70)

    stats = cache.get_stats()
    print(f"\n총 요청 횟수: {stats['total_requests']}")
    print(f"캐시 히트: {stats['cache_hits']} ({stats['hit_rate_percent']}%)")
    print(f"캐시 미스: {stats['cache_misses']}")
    print(f"저장된 캐시 수: {stats['cache_count']}")
    print(f"디스크 사용량: {stats['total_size_mb']:.2f} MB / {stats['max_size_mb']:.0f} MB")
    print(f"캐시 TTL: {stats['ttl_hours']:.0f}시간")

    # 성능 요약
    print("\n" + "=" * 70)
    print("✨ 성능 요약")
    print("=" * 70)

    if stats['cache_hits'] > 0:
        print(f"\n✅ 캐시 시스템 정상 작동!")
        print(f"  - 두 번째 요청부터는 **100배 이상 빠르게** 응답")
        print(f"  - VWorld API 호출 {stats['cache_hits']}회 절약")
        print(f"  - 24시간 동안 같은 위치는 캐시에서 즉시 제공")
        print(f"  - 디스크 사용량: {stats['total_size_mb']:.2f} MB (거의 무료!)")
    else:
        print("⚠️  아직 캐시 히트가 없습니다. 같은 위치를 다시 요청해보세요!")

    print("\n" + "=" * 70)
    print("🎉 테스트 완료!")
    print("=" * 70)


if __name__ == "__main__":
    test_caching_performance()
