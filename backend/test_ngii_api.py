#!/usr/bin/env python3
"""
국토정보플랫폼(VWorld) API 테스트 스크립트
"""

import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

def test_api_key():
    """API 키 유효성 테스트"""

    api_key = os.getenv('NGII_API_KEY', '')

    print("=" * 70)
    print("🔑 VWorld API 키 테스트")
    print("=" * 70)
    print()

    if not api_key:
        print("❌ .env 파일에 NGII_API_KEY가 설정되지 않았습니다.")
        return False

    print(f"API Key: {api_key[:15]}...{api_key[-10:]} (총 {len(api_key)}자)")
    print()

    # 테스트 1: 간단한 주소 검색
    print("📍 테스트 1: 주소 검색 API")
    print("-" * 70)

    test_address = "서울특별시 종로구 세종대로 209"  # 정부서울청사

    params = {
        'service': 'address',
        'request': 'getCoord',
        'version': '2.0',
        'crs': 'epsg:4326',
        'address': test_address,
        'format': 'json',
        'type': 'road',  # road(도로명) 또는 parcel(지번)
        'key': api_key
    }

    url = "http://api.vworld.kr/req/address"

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        print(f"테스트 주소: {test_address}")
        print(f"HTTP 상태: {response.status_code}")
        print(f"API 상태: {data.get('response', {}).get('status')}")
        print()

        if data.get('response', {}).get('status') == 'OK':
            result = data['response']['result']
            point = result.get('point', {})

            print("✅ 성공!")
            print(f"  경도: {point.get('x')}")
            print(f"  위도: {point.get('y')}")
            print(f"  전체 주소: {result.get('text')}")
            print()
            return True

        elif data.get('response', {}).get('status') == 'ERROR':
            error = data['response'].get('error', {})
            print(f"❌ 에러 발생")
            print(f"  코드: {error.get('code')}")
            print(f"  메시지: {error.get('text')}")
            print()
            print("💡 해결 방법:")

            if error.get('code') == 'INVALID_KEY':
                print("  1. https://www.vworld.kr/ 접속")
                print("  2. 로그인 > 마이페이지 > API 관리")
                print("  3. 발급된 API 키 확인")
                print("  4. .env 파일의 NGII_API_KEY 값 업데이트")
                print("  5. API 키 상태가 '승인'인지 확인")
                print()
                print("  ⚠️  주의: 승인 후 실제 활성화까지 1-2시간 소요될 수 있습니다")
            elif error.get('code') == 'UNKNOWN_ADDRESS':
                print("  - 주소 형식이 올바른지 확인")
                print("  - 도로명 주소 또는 지번 주소로 시도")

            print()
            print("전체 응답:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print()
            return False

    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")
        return False

    print()
    print("=" * 70)

def test_wms_service():
    """WMS 서비스 테스트 (지도 이미지)"""

    api_key = os.getenv('NGII_API_KEY', '')

    print()
    print("=" * 70)
    print("🗺️  테스트 2: WMS 지도 서비스")
    print("=" * 70)
    print()

    # 서울 시청 좌표
    lon, lat = 126.9784, 37.5665

    wms_url = "http://api.vworld.kr/req/wms"

    params = {
        'service': 'WMS',
        'request': 'GetMap',
        'version': '1.3.0',
        'layers': 'Satellite',
        'styles': 'Satellite',
        'crs': 'EPSG:4326',
        'bbox': f'{lon-0.001},{lat-0.001},{lon+0.001},{lat+0.001}',
        'width': 256,
        'height': 256,
        'format': 'image/png',
        'transparent': 'false',
        'bgcolor': '0xFFFFFF',
        'exceptions': 'text/xml',
        'key': api_key
    }

    try:
        response = requests.get(wms_url, params=params, timeout=10)

        print(f"HTTP 상태: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print()

        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            print("✅ WMS 서비스 정상 작동")
            print(f"  이미지 크기: {len(response.content)} bytes")
            print()

            # 샘플 이미지 저장
            output_path = "test_satellite_image.png"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"  📁 테스트 이미지 저장: {output_path}")
            print()
            return True
        else:
            print("❌ WMS 서비스 응답 이상")
            print(f"  응답 내용: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")
        return False

if __name__ == "__main__":
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "VWorld API 통합 테스트" + " " * 30 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    # API 키 테스트
    result1 = test_api_key()

    # WMS 테스트 (API 키가 유효한 경우에만)
    if result1:
        result2 = test_wms_service()
    else:
        print()
        print("⚠️  API 키 테스트가 실패하여 WMS 테스트를 건너뜁니다.")

    print()
    print("=" * 70)
    print()

    if result1:
        print("✅ 모든 테스트 통과! API가 정상 작동합니다.")
    else:
        print("❌ API 키 문제를 해결한 후 다시 시도하세요.")
        print()
        print("   python backend/test_ngii_api.py")

    print()
