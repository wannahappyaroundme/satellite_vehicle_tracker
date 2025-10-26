"""
public_cctv_integration.py
실제 공공데이터 기반 CCTV 통합 서비스

데이터 소스:
1. 전국CCTV표준데이터 (행정안전부) - 수만 개 CCTV 위치
2. 국토교통부 ITS API - 실시간 교통 CCTV 영상
3. 서울시 Open API - 서울시 CCTV 상세 정보
"""

import os
import math
import requests
import pandas as pd
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
import asyncio
import aiohttp

logger = logging.getLogger(__name__)


class PublicCCTVIntegration:
    """
    실제 공공데이터 기반 CCTV 통합 서비스
    """

    def __init__(self):
        """초기화"""
        # API 키 (환경 변수에서 로드)
        self.its_api_key = os.getenv('ITS_API_KEY', 'DEMO')  # 국토교통부 ITS
        self.seoul_api_key = os.getenv('SEOUL_API_KEY', 'sample')  # 서울시

        # API Base URLs
        self.its_base_url = "http://openapi.its.go.kr:8081/api"
        self.seoul_base_url = f"http://openapi.seoul.go.kr:8088/{self.seoul_api_key}/json"

        # 데이터베이스 경로
        self.db_path = os.path.join(
            os.path.dirname(__file__),
            'data',
            'cctv_database.db'
        )

        # 데이터 폴더 생성
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # 데이터베이스 초기화
        self._init_database()

    def _init_database(self):
        """SQLite 데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # CCTV 위치 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cctv_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cctv_id TEXT UNIQUE,
                name TEXT,
                latitude REAL,
                longitude REAL,
                address TEXT,
                purpose TEXT,
                management_agency TEXT,
                camera_count INTEGER,
                installation_date TEXT,
                has_realtime_stream INTEGER DEFAULT 0,
                stream_url TEXT,
                data_source TEXT,
                is_available INTEGER DEFAULT 1,
                last_checked TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Spatial index 대용 (latitude, longitude 복합 인덱스)
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cctv_coords
            ON cctv_locations(latitude, longitude)
        ''')

        # CCTV 가용성 로그
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cctv_availability_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cctv_id TEXT,
                status TEXT,
                checked_at TEXT,
                response_time_ms INTEGER,
                error_message TEXT,
                FOREIGN KEY(cctv_id) REFERENCES cctv_locations(cctv_id)
            )
        ''')

        conn.commit()
        conn.close()

        logger.info(f"Database initialized at {self.db_path}")

    def load_national_cctv_data(self, csv_path: str) -> int:
        """
        전국CCTV표준데이터 CSV 로드

        Args:
            csv_path: CSV 파일 경로

        Returns:
            로드된 CCTV 개수
        """
        try:
            # CSV 로드 (다양한 인코딩 시도)
            for encoding in ['utf-8', 'cp949', 'euc-kr']:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Unable to read CSV with any encoding")

            # 컬럼명 정규화 (공백 제거)
            df.columns = df.columns.str.strip()

            # 필수 컬럼 확인
            required_cols = ['위도', '경도']
            if not all(col in df.columns for col in required_cols):
                logger.error(f"Missing required columns. Found: {df.columns.tolist()}")
                return 0

            # 위경도 없는 행 제거
            df = df.dropna(subset=['위도', '경도'])

            # 데이터베이스에 저장
            conn = sqlite3.connect(self.db_path)

            for idx, row in df.iterrows():
                try:
                    # CCTV ID 생성
                    cctv_id = f"nat_{int(row.get('위도', 0)*1000000)}_{int(row.get('경도', 0)*1000000)}"

                    # INSERT 또는 UPDATE
                    conn.execute('''
                        INSERT OR REPLACE INTO cctv_locations
                        (cctv_id, name, latitude, longitude, address, purpose,
                         management_agency, camera_count, data_source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        cctv_id,
                        row.get('소재지도로명주소', row.get('소재지지번주소', '')),
                        float(row['위도']),
                        float(row['경도']),
                        row.get('소재지도로명주소', row.get('소재지지번주소', '')),
                        row.get('설치목적', '기타'),
                        row.get('관리기관명', ''),
                        int(row.get('카메라대수', 1)),
                        'national_standard_data'
                    ))

                except Exception as e:
                    logger.warning(f"Failed to insert row {idx}: {e}")
                    continue

            conn.commit()
            total_loaded = len(df)
            conn.close()

            logger.info(f"Loaded {total_loaded} CCTVs from national data")
            return total_loaded

        except Exception as e:
            logger.error(f"Failed to load national CCTV data: {e}")
            return 0

    def fetch_its_cctvs(self, min_x: float, max_x: float, min_y: float, max_y: float) -> List[Dict]:
        """
        국토교통부 ITS CCTV 데이터 가져오기

        Args:
            min_x, max_x, min_y, max_y: 검색 영역 좌표 (WGS84)

        Returns:
            CCTV 목록
        """
        try:
            url = f"{self.its_base_url}/NCCTVInfo"
            params = {
                'key': self.its_api_key,
                'type': 'json',
                'cctvType': '1',  # 1: 고속도로, 2: 국도
                'minX': min_x,
                'maxX': max_x,
                'minY': min_y,
                'maxY': max_y
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if isinstance(data, dict) and 'data' in data:
                    return data['data']
                elif isinstance(data, list):
                    return data

            logger.warning(f"ITS API returned status {response.status_code}")
            return []

        except Exception as e:
            logger.error(f"Failed to fetch ITS CCTVs: {e}")
            return []

    def get_its_stream_url(self, cctv_id: str) -> Optional[str]:
        """
        ITS CCTV 실시간 영상 URL 가져오기

        Args:
            cctv_id: CCTV ID

        Returns:
            JPEG 이미지 URL (5초 간격 갱신)
        """
        try:
            url = f"{self.its_base_url}/GetCCTVInfo"
            params = {
                'key': self.its_api_key,
                'cctvid': cctv_id,
                'type': 'json'
            }

            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                return data.get('imageUrl') or data.get('streamUrl')

            return None

        except Exception as e:
            logger.error(f"Failed to get ITS stream URL for {cctv_id}: {e}")
            return None

    def fetch_seoul_cctvs(self, start: int = 1, end: int = 1000) -> List[Dict]:
        """
        서울시 CCTV 데이터 가져오기

        Args:
            start: 시작 번호
            end: 끝 번호

        Returns:
            CCTV 목록
        """
        try:
            url = f"{self.seoul_base_url}/CCTV/{start}/{end}"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if 'CCTV' in data and 'row' in data['CCTV']:
                    return data['CCTV']['row']

            return []

        except Exception as e:
            logger.error(f"Failed to fetch Seoul CCTVs: {e}")
            return []

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        두 좌표 간 거리 계산 (Haversine formula)

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

    def search_nearby_cctvs(
        self,
        lat: float,
        lon: float,
        radius: int = 1000,
        purpose_filter: Optional[str] = None
    ) -> Dict:
        """
        주변 CCTV 검색

        Args:
            lat: 중심 위도
            lon: 중심 경도
            radius: 검색 반경 (미터)
            purpose_filter: 목적 필터 (교통, 방범, 주차 등)

        Returns:
            검색 결과
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 대략적인 위경도 범위 계산 (1도 ≈ 111km)
            lat_range = radius / 111000
            lon_range = radius / (111000 * math.cos(math.radians(lat)))

            # SQL 쿼리
            query = '''
                SELECT * FROM cctv_locations
                WHERE latitude BETWEEN ? AND ?
                  AND longitude BETWEEN ? AND ?
                  AND is_available = 1
            '''
            params = [
                lat - lat_range,
                lat + lat_range,
                lon - lon_range,
                lon + lon_range
            ]

            if purpose_filter:
                query += " AND purpose LIKE ?"
                params.append(f"%{purpose_filter}%")

            cursor.execute(query, params)

            # 결과 처리
            nearby_cctvs = []
            for row in cursor.fetchall():
                distance = self.calculate_distance(
                    lat, lon,
                    row['latitude'], row['longitude']
                )

                if distance <= radius:
                    cctv_dict = dict(row)
                    cctv_dict['distance'] = round(distance, 1)
                    nearby_cctvs.append(cctv_dict)

            # 거리순 정렬
            nearby_cctvs.sort(key=lambda x: x['distance'])

            conn.close()

            return {
                'success': True,
                'total_count': len(nearby_cctvs),
                'cctv': nearby_cctvs[:50],  # 최대 50개 반환
                'search_params': {
                    'latitude': lat,
                    'longitude': lon,
                    'radius': radius,
                    'purpose_filter': purpose_filter
                },
                'data_source': 'public_data_integration'
            }

        except Exception as e:
            logger.error(f"CCTV search failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_count': 0,
                'cctv': []
            }

    async def check_cctv_availability(self, cctv_id: str, stream_url: str) -> Dict:
        """
        CCTV 가용성 비동기 체크

        Args:
            cctv_id: CCTV ID
            stream_url: 스트림 URL

        Returns:
            가용성 정보
        """
        start_time = datetime.now()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(stream_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    response_time = (datetime.now() - start_time).total_seconds() * 1000

                    if response.status == 200:
                        content = await response.read()

                        # 유효한 이미지인지 확인 (최소 크기)
                        if len(content) > 1000:
                            return {
                                'cctv_id': cctv_id,
                                'status': 'online',
                                'response_time_ms': int(response_time),
                                'image_size': len(content),
                                'checked_at': datetime.now().isoformat()
                            }

            return {
                'cctv_id': cctv_id,
                'status': 'offline',
                'response_time_ms': int(response_time),
                'checked_at': datetime.now().isoformat()
            }

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000

            return {
                'cctv_id': cctv_id,
                'status': 'error',
                'error': str(e),
                'response_time_ms': int(response_time),
                'checked_at': datetime.now().isoformat()
            }

    def get_database_stats(self) -> Dict:
        """데이터베이스 통계 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 전체 CCTV 개수
            cursor.execute("SELECT COUNT(*) FROM cctv_locations")
            total_count = cursor.fetchone()[0]

            # 데이터 소스별 개수
            cursor.execute("""
                SELECT data_source, COUNT(*) as count
                FROM cctv_locations
                GROUP BY data_source
            """)
            by_source = {row[0]: row[1] for row in cursor.fetchall()}

            # 목적별 개수
            cursor.execute("""
                SELECT purpose, COUNT(*) as count
                FROM cctv_locations
                GROUP BY purpose
                ORDER BY count DESC
                LIMIT 10
            """)
            by_purpose = {row[0]: row[1] for row in cursor.fetchall()}

            # 실시간 스트림 있는 CCTV
            cursor.execute("""
                SELECT COUNT(*) FROM cctv_locations
                WHERE has_realtime_stream = 1
            """)
            with_stream = cursor.fetchone()[0]

            conn.close()

            return {
                'total_cctv_count': total_count,
                'by_data_source': by_source,
                'by_purpose': by_purpose,
                'with_realtime_stream': with_stream,
                'database_path': self.db_path
            }

        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}


# Singleton 인스턴스
_cctv_service_instance = None


def get_public_cctv_service() -> PublicCCTVIntegration:
    """공공 CCTV 서비스 싱글톤"""
    global _cctv_service_instance
    if _cctv_service_instance is None:
        _cctv_service_instance = PublicCCTVIntegration()
    return _cctv_service_instance
