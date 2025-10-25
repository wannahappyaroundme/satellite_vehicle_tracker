"""
국토정보플랫폼(NGII) API 연동 서비스
National Geographic Information Institute API Service
"""

import os
import requests
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

load_dotenv()


class NGIIAPIService:
    """
    국토정보플랫폼 Open API 서비스
    항공사진, 주소 검색 등의 기능 제공
    """

    def __init__(self):
        self.api_key = os.getenv('NGII_API_KEY', '')
        if not self.api_key or self.api_key == '여기에_발급받은_API_키를_입력하세요':
            print("⚠️  경고: NGII API 키가 설정되지 않았습니다!")
            print("   .env 파일에서 NGII_API_KEY를 설정하세요.")

        # API 엔드포인트
        self.base_url = "http://api.vworld.kr/req"
        self.geocode_url = f"{self.base_url}/address"
        self.aerial_url = f"{self.base_url}/wms"

    def search_address(
        self,
        sido: str = None,
        sigungu: str = None,
        dong: str = None,
        jibun: str = None,
        query: str = None
    ) -> Dict:
        """
        주소 검색 (지오코딩)

        Args:
            sido: 시/도 (예: 서울특별시, 제주특별자치도)
            sigungu: 시/군/구 (예: 강남구, 제주시)
            dong: 동/읍/면 (예: 역삼동, 일도이동)
            jibun: 지번 (예: 123, 123-45)
            query: 전체 주소 문자열 (다른 파라미터와 함께 사용 가능)

        Returns:
            주소 검색 결과 (좌표 포함)
        """
        try:
            # 주소 문자열 조합
            if query:
                address = query
            else:
                parts = []
                if sido:
                    parts.append(sido)
                if sigungu:
                    parts.append(sigungu)
                if dong:
                    parts.append(dong)
                if jibun:
                    parts.append(jibun)
                address = ' '.join(parts)

            if not address:
                return {"error": "주소 정보가 필요합니다"}

            # API 요청
            params = {
                'service': 'address',
                'request': 'getCoord',
                'version': '2.0',
                'crs': 'epsg:4326',  # WGS84 (위경도)
                'address': address,
                'format': 'json',
                'type': 'parcel',  # parcel(지번) or road(도로명)
                'key': self.api_key
            }

            response = requests.get(self.geocode_url, params=params, timeout=10)
            data = response.json()

            if data.get('response', {}).get('status') == 'OK':
                result = data['response']['result']
                if result.get('point'):
                    return {
                        'success': True,
                        'address': address,
                        'longitude': float(result['point']['x']),
                        'latitude': float(result['point']['y']),
                        'full_address': result.get('text', address),
                        'type': result.get('type', 'parcel')
                    }

            return {
                'success': False,
                'error': '주소를 찾을 수 없습니다',
                'query': address
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'주소 검색 오류: {str(e)}',
                'query': address if 'address' in locals() else query
            }

    def get_aerial_image_url(
        self,
        latitude: float,
        longitude: float,
        width: int = 800,
        height: int = 600,
        zoom_level: int = 18
    ) -> str:
        """
        항공사진 이미지 URL 생성

        Args:
            latitude: 위도
            longitude: 경도
            width: 이미지 너비 (픽셀)
            height: 이미지 높이 (픽셀)
            zoom_level: 확대 레벨 (1-19, 높을수록 확대)

        Returns:
            항공사진 이미지 URL
        """
        # vworld WMS 서비스 사용
        params = {
            'service': 'WMS',
            'request': 'GetMap',
            'version': '1.3.0',
            'layers': 'Satellite',  # 항공사진 레이어
            'styles': 'Satellite',
            'crs': 'EPSG:4326',
            'bbox': f'{longitude-0.001},{latitude-0.001},{longitude+0.001},{latitude+0.001}',
            'width': width,
            'height': height,
            'format': 'image/png',
            'transparent': 'false',
            'bgcolor': '0xFFFFFF',
            'exceptions': 'text/xml',
            'key': self.api_key
        }

        url = self.aerial_url + '?' + '&'.join([f'{k}={v}' for k, v in params.items()])
        return url

    def download_aerial_image(
        self,
        latitude: float,
        longitude: float,
        output_path: str,
        width: int = 1024,
        height: int = 1024
    ) -> Dict:
        """
        항공사진 다운로드

        Args:
            latitude: 위도
            longitude: 경도
            output_path: 저장 경로
            width: 이미지 너비
            height: 이미지 높이

        Returns:
            다운로드 결과
        """
        try:
            url = self.get_aerial_image_url(latitude, longitude, width, height)
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)

                return {
                    'success': True,
                    'path': output_path,
                    'size': len(response.content),
                    'coordinates': {
                        'latitude': latitude,
                        'longitude': longitude
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: 이미지 다운로드 실패'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'다운로드 오류: {str(e)}'
            }

    def get_sido_list(self) -> List[str]:
        """
        시/도 목록 반환

        Returns:
            시/도 목록
        """
        return [
            "서울특별시",
            "부산광역시",
            "대구광역시",
            "인천광역시",
            "광주광역시",
            "대전광역시",
            "울산광역시",
            "세종특별자치시",
            "경기도",
            "강원도",
            "충청북도",
            "충청남도",
            "전라북도",
            "전라남도",
            "경상북도",
            "경상남도",
            "제주특별자치도"
        ]

    def get_sigungu_list(self, sido: str) -> List[str]:
        """
        시/군/구 목록 반환 (실제로는 API 호출 필요)

        Args:
            sido: 시/도명

        Returns:
            시/군/구 목록
        """
        # 샘플 데이터 (실제로는 API에서 가져와야 함)
        sigungu_map = {
            "서울특별시": ["강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구",
                       "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구",
                       "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"],
            "제주특별자치도": ["제주시", "서귀포시"],
            "경기도": ["수원시", "성남시", "의정부시", "안양시", "부천시", "광명시", "평택시", "동두천시",
                     "안산시", "고양시", "과천시", "구리시", "남양주시", "오산시", "시흥시", "군포시",
                     "의왕시", "하남시", "용인시", "파주시", "이천시", "안성시", "김포시", "화성시",
                     "광주시", "양주시", "포천시", "여주시", "연천군", "가평군", "양평군"]
        }

        return sigungu_map.get(sido, [])

    def search_by_address_components(
        self,
        sido: str,
        sigungu: str = None,
        dong: str = None,
        jibun: str = None
    ) -> Dict:
        """
        주소 구성요소로 검색 (UI 드롭다운 선택용)

        Args:
            sido: 시/도
            sigungu: 시/군/구
            dong: 동/읍/면
            jibun: 지번

        Returns:
            검색 결과 (좌표 및 항공사진 URL 포함)
        """
        # 주소 검색
        result = self.search_address(sido=sido, sigungu=sigungu, dong=dong, jibun=jibun)

        if result.get('success'):
            # 항공사진 URL 추가
            result['aerial_image_url'] = self.get_aerial_image_url(
                result['latitude'],
                result['longitude']
            )

        return result


# 테스트용
if __name__ == "__main__":
    service = NGIIAPIService()

    # 테스트: 제주시 일도이동 검색
    print("=" * 60)
    print("국토정보플랫폼 API 테스트")
    print("=" * 60)

    result = service.search_address(
        sido="제주특별자치도",
        sigungu="제주시",
        dong="일도이동",
        jibun="923"
    )

    if result.get('success'):
        print("\n✓ 주소 검색 성공!")
        print(f"  주소: {result['full_address']}")
        print(f"  위도: {result['latitude']}")
        print(f"  경도: {result['longitude']}")
        print(f"\n  항공사진 URL:")
        print(f"  {service.get_aerial_image_url(result['latitude'], result['longitude'])}")
    else:
        print(f"\n✗ 검색 실패: {result.get('error')}")

    print("\n" + "=" * 60)
