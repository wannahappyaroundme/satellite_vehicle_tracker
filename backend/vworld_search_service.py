"""
vworld_search_service.py
VWorld 추가 API 서비스

기능:
- POI (Point of Interest) 검색
- 주차장 위치 검색
- CCTV 위치 검색
- 2D 배경지도 제공
"""

import requests
from typing import Dict, List, Optional
import os


class VWorldSearchService:
    """
    VWorld 추가 API 서비스
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        초기화

        Args:
            api_key: VWorld API 키
        """
        self.api_key = api_key or '85942406-5BBA-329A-94AE-BD66BE1DB672'
        self.base_url = "https://api.vworld.kr/req"

    def search_poi(
        self,
        query: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: int = 1000,
        count: int = 10
    ) -> Dict:
        """
        POI (관심 지점) 검색

        Args:
            query: 검색어 (예: "주차장", "CCTV", "경찰서")
            lat: 중심 위도
            lon: 중심 경도
            radius: 검색 반경 (미터)
            count: 결과 개수

        Returns:
            POI 검색 결과
        """
        try:
            # VWorld POI API
            url = f"{self.base_url}/search"

            params = {
                'service': 'search',
                'request': 'search',
                'version': '2.0',
                'crs': 'EPSG:4326',
                'query': query,
                'type': 'place',
                'category': 'L4',
                'format': 'json',
                'errorformat': 'json',
                'count': count,
                'key': self.api_key
            }

            # 좌표 기반 검색
            if lat is not None and lon is not None:
                params['point'] = f"{lon},{lat}"
                params['radius'] = radius

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if data.get('response', {}).get('status') == 'OK':
                    results = data.get('response', {}).get('result', {}).get('items', [])

                    # 결과 파싱
                    pois = []
                    for item in results:
                        pois.append({
                            'title': item.get('title', ''),
                            'category': item.get('category', ''),
                            'address': item.get('address', ''),
                            'latitude': float(item.get('point', {}).get('y', 0)),
                            'longitude': float(item.get('point', {}).get('x', 0)),
                            'distance': item.get('distance', 0)
                        })

                    return {
                        'success': True,
                        'total_count': len(pois),
                        'pois': pois
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('response', {}).get('error', {}).get('text', 'Unknown error')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def search_parking_lots(
        self,
        lat: float,
        lon: float,
        radius: int = 2000
    ) -> Dict:
        """
        주차장 검색

        Args:
            lat: 중심 위도
            lon: 중심 경도
            radius: 검색 반경 (미터)

        Returns:
            주차장 목록
        """
        return self.search_poi(
            query='주차장',
            lat=lat,
            lon=lon,
            radius=radius,
            count=50
        )

    def search_cctv(
        self,
        lat: float,
        lon: float,
        radius: int = 1000
    ) -> Dict:
        """
        CCTV 검색

        Args:
            lat: 중심 위도
            lon: 중심 경도
            radius: 검색 반경 (미터)

        Returns:
            CCTV 목록
        """
        # VWorld에는 CCTV API가 직접 없으므로 데모 데이터 반환
        # 실제로는 각 지자체의 공공데이터 API를 사용해야 함

        return {
            'success': True,
            'total_count': 3,
            'cctv': [
                {
                    'id': f'cctv_{int(lat * 1000)}_{int(lon * 1000)}_1',
                    'name': f'CCTV #{int(lat * 1000) % 100}-1',
                    'latitude': lat + 0.001,
                    'longitude': lon + 0.001,
                    'distance': 100,
                    'type': 'traffic',
                    'is_public': True
                },
                {
                    'id': f'cctv_{int(lat * 1000)}_{int(lon * 1000)}_2',
                    'name': f'CCTV #{int(lat * 1000) % 100}-2',
                    'latitude': lat - 0.001,
                    'longitude': lon + 0.001,
                    'distance': 150,
                    'type': 'security',
                    'is_public': True
                },
                {
                    'id': f'cctv_{int(lat * 1000)}_{int(lon * 1000)}_3',
                    'name': f'CCTV #{int(lat * 1000) % 100}-3',
                    'latitude': lat,
                    'longitude': lon - 0.001,
                    'distance': 120,
                    'type': 'parking',
                    'is_public': True
                }
            ],
            'note': '데모 데이터입니다. 실제 CCTV 위치는 각 지자체 공공데이터를 활용하세요.'
        }

    def get_2d_map_tile_url(self, z: int, x: int, y: int) -> str:
        """
        VWorld 2D 배경지도 타일 URL

        Args:
            z: 줌 레벨
            x: 타일 X 좌표
            y: 타일 Y 좌표

        Returns:
            타일 URL
        """
        # VWorld Base Map
        return f"http://xdworld.vworld.kr:8080/2d/Base/service/{z}/{x}/{y}.png"

    def get_hybrid_map_tile_url(self, z: int, x: int, y: int) -> str:
        """
        VWorld 하이브리드 지도 타일 URL (항공사진 + 도로명)

        Args:
            z: 줌 레벨
            x: 타일 X 좌표
            y: 타일 Y 좌표

        Returns:
            타일 URL
        """
        # VWorld Hybrid Map
        return f"http://xdworld.vworld.kr:8080/2d/Hybrid/service/{z}/{x}/{y}.png"


# 싱글톤 인스턴스
_vworld_search_service = None


def get_vworld_search_service() -> VWorldSearchService:
    """
    VWorld Search 서비스 싱글톤 인스턴스 반환

    Returns:
        VWorldSearchService 인스턴스
    """
    global _vworld_search_service
    if _vworld_search_service is None:
        _vworld_search_service = VWorldSearchService()
    return _vworld_search_service
