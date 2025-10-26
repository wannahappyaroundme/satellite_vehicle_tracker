"""
VWorld WMTS (Web Map Tile Service) API Integration
타일 기반 고속 항공사진 다운로드 서비스

WMS 대비 5-10배 빠른 성능:
- WMS: 매번 전체 이미지 생성 (느림)
- WMTS: 미리 생성된 타일 다운로드 (빠름)

250개 시/군/구 전국 스캔에 최적화
"""

import os
import math
import requests
from PIL import Image
import numpy as np
from io import BytesIO
from typing import Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)


class VWorldWMTSService:
    """
    VWorld WMTS API 서비스

    타일 맵 시스템:
    - Zoom level 18: 고해상도 (차량 탐지 최적)
    - 256x256 타일 크기
    - 3x3 타일 = 768x768 픽셀 이미지
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        초기화

        Args:
            api_key: VWorld API 키 (없으면 기본값 사용)
        """
        # Use approved VWorld API key (ignore env variable as it may be incorrect)
        self.api_key = api_key or '85942406-5BBA-329A-94AE-BD66BE1DB672'

        # WMTS Base URL (Satellite layer)
        self.wmts_base_url = "https://api.vworld.kr/req/wmts/1.0.0/{api_key}/Satellite/{z}/{y}/{x}.jpeg"

        # 타일 크기 (고정)
        self.tile_size = 256

        logger.info(f"✅ VWorld WMTS 서비스 초기화 (API Key: {self.api_key[:20]}...)")

    def latlon_to_tile(self, lat: float, lon: float, zoom: int) -> Tuple[int, int]:
        """
        위경도를 타일 좌표로 변환

        Args:
            lat: 위도
            lon: 경도
            zoom: 줌 레벨 (18 권장)

        Returns:
            (tile_x, tile_y) 타일 좌표
        """
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom

        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)

        return x, y

    def tile_to_latlon(self, tile_x: int, tile_y: int, zoom: int) -> Tuple[float, float]:
        """
        타일 좌표를 위경도로 변환 (타일 왼쪽 상단 모서리)

        Args:
            tile_x: 타일 X 좌표
            tile_y: 타일 Y 좌표
            zoom: 줌 레벨

        Returns:
            (lat, lon) 위경도
        """
        n = 2.0 ** zoom
        lon = tile_x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n)))
        lat = math.degrees(lat_rad)

        return lat, lon

    def download_tile(self, tile_x: int, tile_y: int, zoom: int, timeout: int = 10) -> Optional[Image.Image]:
        """
        단일 타일 다운로드

        Args:
            tile_x: 타일 X 좌표
            tile_y: 타일 Y 좌표
            zoom: 줌 레벨
            timeout: 타임아웃 (초)

        Returns:
            PIL Image 또는 None (실패 시)
        """
        url = self.wmts_base_url.format(
            api_key=self.api_key,
            z=zoom,
            y=tile_y,
            x=tile_x
        )

        try:
            logger.debug(f"🔗 타일 다운로드 URL: {url}")
            response = requests.get(url, timeout=timeout)

            logger.debug(f"📡 HTTP Status: {response.status_code}")
            logger.debug(f"📋 Content-Type: {response.headers.get('Content-Type')}")
            logger.debug(f"📏 Content-Length: {len(response.content)} bytes")

            if response.status_code == 200:
                # Check if response is XML (error) instead of image
                if response.headers.get('Content-Type', '').startswith('application/xml'):
                    logger.error(f"❌ API 에러 응답 (XML): {response.text}")
                    return None

                # 응답 내용 미리보기 (처음 100바이트)
                logger.debug(f"📄 Content preview: {response.content[:100]}")

                return Image.open(BytesIO(response.content))
            else:
                logger.warning(f"⚠️  타일 다운로드 실패 ({tile_x}, {tile_y}, z{zoom}): HTTP {response.status_code}")
                logger.warning(f"   Response: {response.text[:200]}")
                return None

        except Exception as e:
            logger.error(f"❌ 타일 다운로드 에러 ({tile_x}, {tile_y}): {e}")
            return None

    def download_area(
        self,
        lat: float,
        lon: float,
        zoom: int = 18,
        tile_width: int = 3,
        tile_height: int = 3
    ) -> Optional[np.ndarray]:
        """
        지정된 위치 주변의 타일들을 다운로드하여 하나의 이미지로 병합

        Args:
            lat: 중심 위도
            lon: 중심 경도
            zoom: 줌 레벨 (18 = 고해상도, 차량 탐지 최적)
            tile_width: 가로 타일 수 (기본 3)
            tile_height: 세로 타일 수 (기본 3)

        Returns:
            numpy array (RGB) 또는 None (실패 시)
        """
        # 중심 타일 좌표
        center_x, center_y = self.latlon_to_tile(lat, lon, zoom)

        # 타일 범위 계산 (중심 기준 확장)
        half_w = tile_width // 2
        half_h = tile_height // 2

        start_x = center_x - half_w
        end_x = center_x + half_w + 1
        start_y = center_y - half_h
        end_y = center_y + half_h + 1

        # 결과 이미지 크기
        result_width = tile_width * self.tile_size
        result_height = tile_height * self.tile_size

        # 빈 캔버스 생성
        result_image = Image.new('RGB', (result_width, result_height), color=(0, 0, 0))

        downloaded_tiles = 0
        failed_tiles = 0

        # 타일 다운로드 및 병합
        for row, ty in enumerate(range(start_y, end_y)):
            for col, tx in enumerate(range(start_x, end_x)):
                tile_img = self.download_tile(tx, ty, zoom)

                if tile_img:
                    # 타일 위치 계산
                    paste_x = col * self.tile_size
                    paste_y = row * self.tile_size

                    # 타일 붙이기
                    result_image.paste(tile_img, (paste_x, paste_y))
                    downloaded_tiles += 1
                else:
                    failed_tiles += 1

        total_tiles = tile_width * tile_height

        if downloaded_tiles == 0:
            logger.error(f"❌ 모든 타일 다운로드 실패 ({lat}, {lon})")
            return None

        if failed_tiles > 0:
            logger.warning(f"⚠️  일부 타일 실패: {failed_tiles}/{total_tiles} (성공: {downloaded_tiles})")
        else:
            logger.info(f"✅ 타일 다운로드 완료: {downloaded_tiles}/{total_tiles} tiles")

        # numpy array로 변환
        return np.array(result_image)

    def download_high_resolution_area(
        self,
        latitude: float,
        longitude: float,
        width_tiles: int = 3,
        height_tiles: int = 3,
        zoom: int = 18
    ) -> dict:
        """
        고해상도 항공사진 다운로드 (FastAPI 호환 인터페이스)

        Args:
            latitude: 위도
            longitude: 경도
            width_tiles: 가로 타일 수
            height_tiles: 세로 타일 수
            zoom: 줌 레벨

        Returns:
            dict with keys: success, image_array, image_size, tiles_downloaded, method
        """
        image_array = self.download_area(
            lat=latitude,
            lon=longitude,
            zoom=zoom,
            tile_width=width_tiles,
            tile_height=height_tiles
        )

        if image_array is None:
            return {
                'success': False,
                'error': 'Failed to download tiles',
                'method': 'wmts'
            }

        return {
            'success': True,
            'image_array': image_array,
            'image_size': image_array.shape[:2],  # (height, width)
            'tiles_downloaded': width_tiles * height_tiles,
            'method': 'wmts',
            'zoom_level': zoom
        }

    def batch_download_regions(
        self,
        coordinates: List[Tuple[float, float]],
        zoom: int = 18,
        tile_width: int = 3,
        tile_height: int = 3
    ) -> List[dict]:
        """
        여러 지역을 배치로 다운로드 (250개 시/군/구 스캔용)

        Args:
            coordinates: [(lat, lon), ...] 좌표 리스트
            zoom: 줌 레벨
            tile_width: 가로 타일 수
            tile_height: 세로 타일 수

        Returns:
            List of results (각 결과는 download_high_resolution_area와 동일)
        """
        results = []

        logger.info(f"🚀 배치 다운로드 시작: {len(coordinates)}개 지역")

        for idx, (lat, lon) in enumerate(coordinates, 1):
            logger.info(f"  📍 [{idx}/{len(coordinates)}] 다운로드 중: ({lat:.4f}, {lon:.4f})")

            result = self.download_high_resolution_area(
                latitude=lat,
                longitude=lon,
                width_tiles=tile_width,
                height_tiles=tile_height,
                zoom=zoom
            )

            result['index'] = idx
            result['latitude'] = lat
            result['longitude'] = lon

            results.append(result)

        successful = sum(1 for r in results if r['success'])
        logger.info(f"✅ 배치 다운로드 완료: {successful}/{len(coordinates)} 성공")

        return results


def test_wmts_service():
    """
    WMTS 서비스 테스트
    """
    print("=" * 60)
    print("VWorld WMTS 서비스 테스트")
    print("=" * 60)

    service = VWorldWMTSService()

    # 테스트 좌표 (서울 강남구)
    test_lat = 37.5172
    test_lon = 127.0473

    print(f"\n📍 테스트 위치: ({test_lat}, {test_lon})")

    # 타일 좌표 변환
    tile_x, tile_y = service.latlon_to_tile(test_lat, test_lon, zoom=18)
    print(f"   타일 좌표: ({tile_x}, {tile_y}, z18)")

    # 단일 타일 다운로드
    print(f"\n🔽 단일 타일 다운로드 테스트...")
    tile_img = service.download_tile(tile_x, tile_y, zoom=18)

    if tile_img:
        print(f"   ✅ 성공: {tile_img.size} 픽셀")
    else:
        print(f"   ❌ 실패")

    # 3x3 타일 영역 다운로드
    print(f"\n🔽 3x3 타일 영역 다운로드 테스트...")
    result = service.download_high_resolution_area(
        latitude=test_lat,
        longitude=test_lon,
        width_tiles=3,
        height_tiles=3,
        zoom=18
    )

    if result['success']:
        print(f"   ✅ 성공!")
        print(f"   - 이미지 크기: {result['image_size']}")
        print(f"   - 타일 수: {result['tiles_downloaded']}")
        print(f"   - 방법: {result['method']}")
    else:
        print(f"   ❌ 실패: {result.get('error')}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.DEBUG,  # Changed to DEBUG for detailed output
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    test_wmts_service()
