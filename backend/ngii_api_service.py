"""
국토정보플랫폼(NGII) API 연동 서비스
National Geographic Information Institute API Service
"""

import os
import requests
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
import math
import numpy as np
from PIL import Image
import io
from dotenv import load_dotenv
from aerial_image_cache import get_cache

load_dotenv()


class NGIIAPIService:
    """
    국토정보플랫폼 Open API 서비스
    항공사진, 주소 검색 등의 기능 제공
    """

    def __init__(self, enable_cache: bool = True):
        self.api_key = os.getenv('NGII_API_KEY', '')
        if not self.api_key or self.api_key == '여기에_발급받은_API_키를_입력하세요':
            print("⚠️  경고: NGII API 키가 설정되지 않았습니다!")
            print("   .env 파일에서 NGII_API_KEY를 설정하세요.")

        # API 엔드포인트
        self.base_url = "http://api.vworld.kr/req"
        self.geocode_url = f"{self.base_url}/address"
        self.aerial_url = f"{self.base_url}/wms"
        self.wmts_base_url = "https://api.vworld.kr/req/wmts/1.0.0"

        # 캐싱 활성화
        self.enable_cache = enable_cache
        self.cache = get_cache() if enable_cache else None
        if self.enable_cache:
            print("✅ 항공사진 캐싱 시스템 활성화 (24시간 TTL, 최대 5GB)")

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

    def lat_lon_to_tile(self, latitude: float, longitude: float, zoom: int) -> Tuple[int, int]:
        """
        위경도 좌표를 WMTS 타일 좌표로 변환

        Args:
            latitude: 위도
            longitude: 경도
            zoom: 확대 레벨 (6-19)

        Returns:
            (tile_x, tile_y) 튜플
        """
        n = 2.0 ** zoom
        x_tile = int((longitude + 180.0) / 360.0 * n)
        y_tile = int((1.0 - math.asinh(math.tan(math.radians(latitude))) / math.pi) / 2.0 * n)
        return (x_tile, y_tile)

    def get_wmts_tile_url(self, zoom: int, tile_x: int, tile_y: int, layer: str = 'Satellite') -> str:
        """
        WMTS 타일 URL 생성 (WMS보다 빠름)

        Args:
            zoom: 확대 레벨 (6-19)
            tile_x: 타일 X 좌표
            tile_y: 타일 Y 좌표
            layer: 레이어명 (Satellite, Hybrid, Base 등)

        Returns:
            WMTS 타일 URL
        """
        return f"{self.wmts_base_url}/{self.api_key}/{layer}/{zoom}/{tile_y}/{tile_x}.jpeg"

    def download_aerial_tile(
        self,
        latitude: float,
        longitude: float,
        zoom: int = 18,
        output_path: Optional[str] = None
    ) -> Dict:
        """
        WMTS API로 고해상도 항공사진 타일 다운로드

        Args:
            latitude: 위도
            longitude: 경도
            zoom: 확대 레벨 (18-19 권장, 높을수록 고해상도)
            output_path: 저장 경로 (None이면 numpy array 반환)

        Returns:
            다운로드 결과 (path 또는 image_array 포함)
        """
        try:
            # 좌표를 타일 좌표로 변환
            tile_x, tile_y = self.lat_lon_to_tile(latitude, longitude, zoom)

            # WMTS URL 생성
            url = self.get_wmts_tile_url(zoom, tile_x, tile_y)

            # 다운로드
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                # 이미지 데이터
                image = Image.open(io.BytesIO(response.content))

                result = {
                    'success': True,
                    'tile_x': tile_x,
                    'tile_y': tile_y,
                    'zoom': zoom,
                    'coordinates': {
                        'latitude': latitude,
                        'longitude': longitude
                    },
                    'size': len(response.content)
                }

                if output_path:
                    # 파일로 저장
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    result['path'] = output_path
                else:
                    # numpy array로 반환
                    result['image_array'] = np.array(image)

                return result
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: 타일 다운로드 실패',
                    'url': url
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'다운로드 오류: {str(e)}'
            }

    def download_high_resolution_area(
        self,
        latitude: float,
        longitude: float,
        width_tiles: int = 3,
        height_tiles: int = 3,
        zoom: int = 18,
        output_path: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict:
        """
        여러 타일을 다운로드하여 넓은 영역의 고해상도 항공사진 생성
        24시간 캐싱으로 API 호출 최소화

        Args:
            latitude: 중심 위도
            longitude: 중심 경도
            width_tiles: 가로 타일 수 (홀수 권장)
            height_tiles: 세로 타일 수 (홀수 권장)
            zoom: 확대 레벨 (18-19 권장)
            output_path: 저장 경로
            use_cache: 캐시 사용 여부

        Returns:
            다운로드 결과 (병합된 이미지)
        """
        try:
            # 캐시 확인
            if self.enable_cache and use_cache and self.cache:
                cached_data = self.cache.get(latitude, longitude, zoom, width_tiles, height_tiles)
                if cached_data:
                    # 캐시 히트!
                    image = Image.open(io.BytesIO(cached_data))

                    result = {
                        'success': True,
                        'tiles_downloaded': 0,  # 캐시에서 가져옴
                        'image_size': image.size,
                        'zoom': zoom,
                        'coordinates': {
                            'latitude': latitude,
                            'longitude': longitude
                        },
                        'from_cache': True
                    }

                    if output_path:
                        with open(output_path, 'wb') as f:
                            f.write(cached_data)
                        result['path'] = output_path
                    else:
                        result['image_array'] = np.array(image)

                    return result
            # 중심 타일 좌표
            center_x, center_y = self.lat_lon_to_tile(latitude, longitude, zoom)

            # 타일 범위 계산
            start_x = center_x - width_tiles // 2
            start_y = center_y - height_tiles // 2

            # 타일 다운로드
            tiles = []
            for y_offset in range(height_tiles):
                row = []
                for x_offset in range(width_tiles):
                    tile_x = start_x + x_offset
                    tile_y = start_y + y_offset

                    url = self.get_wmts_tile_url(zoom, tile_x, tile_y)
                    response = requests.get(url, timeout=30)

                    if response.status_code == 200:
                        tile_image = Image.open(io.BytesIO(response.content))
                        row.append(tile_image)
                    else:
                        # 빈 타일로 대체
                        row.append(Image.new('RGB', (256, 256), (200, 200, 200)))

                tiles.append(row)

            # 타일 병합
            tile_width = tiles[0][0].width
            tile_height = tiles[0][0].height

            merged_width = tile_width * width_tiles
            merged_height = tile_height * height_tiles

            merged_image = Image.new('RGB', (merged_width, merged_height))

            for y_idx, row in enumerate(tiles):
                for x_idx, tile in enumerate(row):
                    x_pos = x_idx * tile_width
                    y_pos = y_idx * tile_height
                    merged_image.paste(tile, (x_pos, y_pos))

            result = {
                'success': True,
                'tiles_downloaded': width_tiles * height_tiles,
                'image_size': (merged_width, merged_height),
                'zoom': zoom,
                'coordinates': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'from_cache': False
            }

            # 이미지를 JPEG 바이트로 변환
            image_buffer = io.BytesIO()
            merged_image.save(image_buffer, 'JPEG', quality=95)
            image_bytes = image_buffer.getvalue()

            # 캐시에 저장
            if self.enable_cache and use_cache and self.cache:
                self.cache.set(
                    latitude, longitude, zoom, image_bytes,
                    width_tiles, height_tiles,
                    metadata={
                        'image_size': (merged_width, merged_height),
                        'api': 'vworld_wmts'
                    }
                )

            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
                result['path'] = output_path
            else:
                result['image_array'] = np.array(merged_image)

            return result

        except Exception as e:
            return {
                'success': False,
                'error': f'영역 다운로드 오류: {str(e)}'
            }


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
