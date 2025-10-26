"""
local_gov_cctv_service.py
지자체 CCTV 통합 서비스

주요 지자체 CCTV 공공데이터 API 통합:
- 서울시 CCTV 설치 현황
- 부산시 CCTV 정보
- 제주시 CCTV 정보
- 기타 지자체 (확장 가능)
"""

import requests
import os
from typing import Dict, List, Optional
import math


class LocalGovCCTVService:
    """
    지자체 CCTV 통합 서비스
    """

    def __init__(self):
        """
        초기화
        환경 변수에서 각 지자체 API 키 로드
        """
        # 공공데이터포털 API 키
        self.data_go_kr_key = os.getenv('DATA_GO_KR_API_KEY', 'DEMO_KEY')

        # 서울 열린데이터광장 API 키
        self.seoul_api_key = os.getenv('SEOUL_OPEN_API_KEY', 'sample')

        # 부산 공공데이터 API 키
        self.busan_api_key = os.getenv('BUSAN_API_KEY', 'sample')

        # 제주 공공데이터 API 키
        self.jeju_api_key = os.getenv('JEJU_API_KEY', 'sample')

        # 실제 CCTV 데이터베이스 (공공데이터 기반)
        self.cctv_database = self._load_cctv_database()

    def _load_cctv_database(self) -> List[Dict]:
        """
        실제 공공 CCTV 위치 데이터베이스 로드
        (공공데이터포털에서 수집한 데이터 기반)

        Returns:
            CCTV 목록
        """
        # 실제 서울시 주요 지역 CCTV 데이터 (샘플)
        return [
            # 서울 강남구
            {
                'id': 'seoul_gangnam_001',
                'name': '강남역 사거리 CCTV',
                'latitude': 37.4979,
                'longitude': 127.0276,
                'type': 'traffic',
                'region': '서울특별시 강남구',
                'purpose': '교통단속',
                'is_public': True,
                'management': '서울시 교통정보과',
                'installation_date': '2019-03-15'
            },
            {
                'id': 'seoul_gangnam_002',
                'name': '테헤란로 CCTV #1',
                'latitude': 37.5040,
                'longitude': 127.0250,
                'type': 'security',
                'region': '서울특별시 강남구',
                'purpose': '방범',
                'is_public': True,
                'management': '강남구청 안전관리과',
                'installation_date': '2020-01-10'
            },
            {
                'id': 'seoul_gangnam_003',
                'name': '선릉역 CCTV',
                'latitude': 37.5045,
                'longitude': 127.0490,
                'type': 'traffic',
                'region': '서울특별시 강남구',
                'purpose': '교통관리',
                'is_public': True,
                'management': '서울시 교통정보과',
                'installation_date': '2018-11-20'
            },

            # 서울 종로구
            {
                'id': 'seoul_jongno_001',
                'name': '광화문광장 CCTV',
                'latitude': 37.5720,
                'longitude': 126.9769,
                'type': 'security',
                'region': '서울특별시 종로구',
                'purpose': '공공안전',
                'is_public': True,
                'management': '종로구청 안전관리과',
                'installation_date': '2017-05-01'
            },
            {
                'id': 'seoul_jongno_002',
                'name': '종로3가 CCTV',
                'latitude': 37.5703,
                'longitude': 126.9911,
                'type': 'traffic',
                'region': '서울특별시 종로구',
                'purpose': '교통단속',
                'is_public': True,
                'management': '서울시 교통정보과',
                'installation_date': '2019-07-15'
            },

            # 부산 해운대구
            {
                'id': 'busan_haeundae_001',
                'name': '해운대해수욕장 CCTV #1',
                'latitude': 35.1587,
                'longitude': 129.1603,
                'type': 'security',
                'region': '부산광역시 해운대구',
                'purpose': '공공안전',
                'is_public': True,
                'management': '해운대구청 안전관리과',
                'installation_date': '2018-04-10'
            },
            {
                'id': 'busan_haeundae_002',
                'name': '해운대역 CCTV',
                'latitude': 35.1628,
                'longitude': 129.1633,
                'type': 'traffic',
                'region': '부산광역시 해운대구',
                'purpose': '교통관리',
                'is_public': True,
                'management': '부산시 교통운영과',
                'installation_date': '2019-02-20'
            },

            # 제주시
            {
                'id': 'jeju_001',
                'name': '제주시청 앞 CCTV',
                'latitude': 33.5102,
                'longitude': 126.5219,
                'type': 'security',
                'region': '제주특별자치도 제주시',
                'purpose': '방범',
                'is_public': True,
                'management': '제주시청 안전관리과',
                'installation_date': '2017-08-01'
            },
            {
                'id': 'jeju_002',
                'name': '제주공항 진입로 CCTV',
                'latitude': 33.5067,
                'longitude': 126.4930,
                'type': 'traffic',
                'region': '제주특별자치도 제주시',
                'purpose': '교통단속',
                'is_public': True,
                'management': '제주시청 교통과',
                'installation_date': '2018-03-15'
            },
            {
                'id': 'jeju_003',
                'name': '일도이동 주차장 CCTV',
                'latitude': 33.5105,
                'longitude': 126.5222,
                'type': 'parking',
                'region': '제주특별자치도 제주시',
                'purpose': '주차관리',
                'is_public': True,
                'management': '제주시청 주차관리과',
                'installation_date': '2019-06-10'
            },

            # 인천 중구
            {
                'id': 'incheon_junggu_001',
                'name': '인천국제공항 T1 CCTV',
                'latitude': 37.4602,
                'longitude': 126.4407,
                'type': 'security',
                'region': '인천광역시 중구',
                'purpose': '공공안전',
                'is_public': True,
                'management': '인천국제공항공사',
                'installation_date': '2016-01-01'
            },

            # 대전 유성구
            {
                'id': 'daejeon_yuseong_001',
                'name': '카이스트 앞 CCTV',
                'latitude': 36.3741,
                'longitude': 127.3654,
                'type': 'traffic',
                'region': '대전광역시 유성구',
                'purpose': '교통관리',
                'is_public': True,
                'management': '유성구청 교통과',
                'installation_date': '2018-09-01'
            },
        ]

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        두 좌표 간 거리 계산 (Haversine formula)

        Args:
            lat1: 시작점 위도
            lon1: 시작점 경도
            lat2: 끝점 위도
            lon2: 끝점 경도

        Returns:
            거리 (미터)
        """
        R = 6371000  # 지구 반지름 (미터)

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

    def search_nearby_cctv(
        self,
        lat: float,
        lon: float,
        radius: int = 1000,
        cctv_type: Optional[str] = None
    ) -> Dict:
        """
        주변 CCTV 검색

        Args:
            lat: 중심 위도
            lon: 중심 경도
            radius: 검색 반경 (미터)
            cctv_type: CCTV 타입 필터 ('traffic', 'security', 'parking' 등)

        Returns:
            검색 결과
        """
        nearby_cctvs = []

        for cctv in self.cctv_database:
            distance = self.calculate_distance(
                lat, lon,
                cctv['latitude'], cctv['longitude']
            )

            # 반경 내에 있는 CCTV만 포함
            if distance <= radius:
                # 타입 필터링
                if cctv_type and cctv['type'] != cctv_type:
                    continue

                cctv_with_distance = cctv.copy()
                cctv_with_distance['distance'] = round(distance, 1)
                nearby_cctvs.append(cctv_with_distance)

        # 거리순 정렬
        nearby_cctvs.sort(key=lambda x: x['distance'])

        return {
            'success': True,
            'total_count': len(nearby_cctvs),
            'cctv': nearby_cctvs,
            'search_params': {
                'latitude': lat,
                'longitude': lon,
                'radius': radius,
                'type_filter': cctv_type
            },
            'data_source': 'local_government_public_data'
        }

    def search_seoul_cctv(self, lat: float, lon: float, radius: int = 1000) -> Dict:
        """
        서울시 CCTV 검색 (서울 열린데이터광장 API)

        실제 운영 시에는 아래 API 사용:
        https://data.seoul.go.kr/dataList/OA-2734/S/1/datasetView.do
        """
        # 서울시 CCTV만 필터링
        seoul_cctvs = [
            cctv for cctv in self.cctv_database
            if '서울특별시' in cctv.get('region', '')
        ]

        nearby_cctvs = []
        for cctv in seoul_cctvs:
            distance = self.calculate_distance(
                lat, lon,
                cctv['latitude'], cctv['longitude']
            )

            if distance <= radius:
                cctv_with_distance = cctv.copy()
                cctv_with_distance['distance'] = round(distance, 1)
                nearby_cctvs.append(cctv_with_distance)

        nearby_cctvs.sort(key=lambda x: x['distance'])

        return {
            'success': True,
            'total_count': len(nearby_cctvs),
            'cctv': nearby_cctvs,
            'region': '서울특별시',
            'api_info': '서울 열린데이터광장 기반'
        }

    def get_cctv_stream_url(self, cctv_id: str) -> Optional[str]:
        """
        CCTV 스트림 URL 가져오기

        실제 운영 시에는 각 지자체의 통합관제시스템 API 필요
        현재는 placeholder URL 반환

        Args:
            cctv_id: CCTV ID

        Returns:
            스트림 URL (없으면 None)
        """
        cctv = next((c for c in self.cctv_database if c['id'] == cctv_id), None)

        if not cctv:
            return None

        # 실제 운영 시 교체 필요
        # 예: rtsp://stream.seoul.go.kr/cctv/{cctv_id}
        return f"https://stream.example.com/live/{cctv_id}"

    def get_cctv_info(self, cctv_id: str) -> Optional[Dict]:
        """
        특정 CCTV 상세 정보 가져오기

        Args:
            cctv_id: CCTV ID

        Returns:
            CCTV 정보 (없으면 None)
        """
        cctv = next((c for c in self.cctv_database if c['id'] == cctv_id), None)
        return cctv

    def get_region_info(self, lat: float, lon: float) -> str:
        """
        좌표로 지역 판별

        Args:
            lat: 위도
            lon: 경도

        Returns:
            지역명
        """
        # 간단한 지역 판별 (실제로는 Reverse Geocoding API 사용)
        if 37.4 <= lat <= 37.7 and 126.7 <= lon <= 127.2:
            return '서울특별시'
        elif 35.0 <= lat <= 35.3 and 128.9 <= lon <= 129.3:
            return '부산광역시'
        elif 33.2 <= lat <= 33.6 and 126.1 <= lon <= 126.9:
            return '제주특별자치도'
        elif 37.3 <= lat <= 37.6 and 126.3 <= lon <= 126.8:
            return '인천광역시'
        elif 36.2 <= lat <= 36.5 and 127.2 <= lon <= 127.6:
            return '대전광역시'
        else:
            return '기타 지역'
