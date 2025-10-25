"""
Abandoned Vehicle Storage Module
JSON 파일 기반 방치 차량 데이터 저장 및 관리

파일 구조:
- data/abandoned_vehicles_db.json: 전국 방치 차량 데이터베이스
"""

import json
import os
import math
from datetime import datetime
from typing import List, Dict, Optional
from threading import Lock

# 파일 경로
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_FILE = os.path.join(DATA_DIR, 'abandoned_vehicles_db.json')

# 파일 접근 락 (동시 쓰기 방지)
file_lock = Lock()


class AbandonedVehicleStorage:
    """
    방치 차량 저장소 관리 클래스
    JSON 파일 기반으로 CRUD 작업 수행
    """

    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._ensure_data_directory()
        self._ensure_db_file()

    def _ensure_data_directory(self):
        """data 디렉토리가 없으면 생성"""
        os.makedirs(DATA_DIR, exist_ok=True)

    def _ensure_db_file(self):
        """DB 파일이 없으면 빈 구조로 생성"""
        if not os.path.exists(self.db_path):
            empty_db = {
                "vehicles": [],
                "metadata": {
                    "total_vehicles": 0,
                    "last_updated": datetime.utcnow().isoformat(),
                    "total_scans": 0,
                    "version": "1.0.0"
                }
            }
            self._save_db(empty_db)

    def _load_db(self) -> Dict:
        """DB 파일 로드"""
        with file_lock:
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"⚠️  Warning: Failed to load DB ({e}). Creating new DB.")
                self._ensure_db_file()
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)

    def _save_db(self, db_data: Dict):
        """DB 파일 저장"""
        with file_lock:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(db_data, f, ensure_ascii=False, indent=2)

    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        두 좌표 간 거리 계산 (Haversine formula)
        Returns: 거리 (미터)
        """
        R = 6371000  # 지구 반지름 (미터)

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lng2 - lng1)

        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _generate_vehicle_id(self, latitude: float, longitude: float, index: int = 0) -> str:
        """
        차량 고유 ID 생성
        형식: vehicle_LAT_LNG_INDEX
        """
        lat_str = f"{latitude:.6f}".replace('.', '_').replace('-', 'm')
        lng_str = f"{longitude:.6f}".replace('.', '_').replace('-', 'm')
        return f"vehicle_{lat_str}_{lng_str}_{index:03d}"

    def add_vehicle(self, vehicle_data: Dict) -> Dict:
        """
        새 방치 차량 추가

        Args:
            vehicle_data: 차량 정보 딕셔너리
                {
                    "latitude": 37.5172,
                    "longitude": 127.0473,
                    "address": "서울특별시 강남구",
                    "vehicle_type": "car",
                    "similarity_score": 0.95,
                    "risk_level": "CRITICAL",
                    "years_difference": 3,
                    "bbox": {"x": 350, "y": 220, "w": 85, "h": 60}
                }

        Returns:
            저장된 차량 정보 (ID 포함)
        """
        db = self._load_db()

        # 차량 ID 생성
        vehicle_id = self._generate_vehicle_id(
            vehicle_data['latitude'],
            vehicle_data['longitude'],
            len(db['vehicles'])
        )

        # 차량 데이터 구성
        vehicle = {
            "id": vehicle_id,
            "latitude": vehicle_data['latitude'],
            "longitude": vehicle_data['longitude'],
            "address": vehicle_data.get('address', '알 수 없는 위치'),
            "vehicle_type": vehicle_data.get('vehicle_type', 'car'),
            "similarity_score": vehicle_data.get('similarity_score', 0.90),
            "similarity_percentage": vehicle_data.get('similarity_score', 0.90) * 100,
            "risk_level": vehicle_data.get('risk_level', 'MEDIUM'),
            "years_difference": vehicle_data.get('years_difference', 1),
            "first_detected": datetime.utcnow().isoformat(),
            "last_checked": datetime.utcnow().isoformat(),
            "detection_count": 1,
            "status": "DETECTED",
            "bbox": vehicle_data.get('bbox', {}),
            "metadata": vehicle_data.get('metadata', {})
        }

        # DB에 추가
        db['vehicles'].append(vehicle)

        # 메타데이터 업데이트
        db['metadata']['total_vehicles'] = len(db['vehicles'])
        db['metadata']['last_updated'] = datetime.utcnow().isoformat()
        db['metadata']['total_scans'] = db['metadata'].get('total_scans', 0) + 1

        # 저장
        self._save_db(db)

        return vehicle

    def get_vehicles_in_area(
        self,
        latitude: float,
        longitude: float,
        radius: float = 500
    ) -> List[Dict]:
        """
        특정 지역 내 방치 차량 조회

        Args:
            latitude: 중심 위도
            longitude: 중심 경도
            radius: 반경 (미터, 기본 500m)

        Returns:
            방치 차량 목록
        """
        db = self._load_db()
        vehicles_in_area = []

        for vehicle in db['vehicles']:
            distance = self._calculate_distance(
                latitude, longitude,
                vehicle['latitude'], vehicle['longitude']
            )

            if distance <= radius:
                # 거리 정보 추가
                vehicle_copy = vehicle.copy()
                vehicle_copy['distance_from_center'] = round(distance, 2)
                vehicles_in_area.append(vehicle_copy)

        # 거리 순으로 정렬
        vehicles_in_area.sort(key=lambda v: v['distance_from_center'])

        return vehicles_in_area

    def get_vehicle_by_id(self, vehicle_id: str) -> Optional[Dict]:
        """특정 차량 조회"""
        db = self._load_db()

        for vehicle in db['vehicles']:
            if vehicle['id'] == vehicle_id:
                return vehicle

        return None

    def update_vehicle_status(
        self,
        vehicle_id: str,
        status: str,
        notes: str = None
    ) -> Optional[Dict]:
        """
        차량 상태 업데이트

        Args:
            vehicle_id: 차량 ID
            status: 새 상태 (DETECTED, INVESTIGATING, RESOLVED)
            notes: 메모

        Returns:
            업데이트된 차량 정보
        """
        db = self._load_db()

        for vehicle in db['vehicles']:
            if vehicle['id'] == vehicle_id:
                vehicle['status'] = status
                vehicle['last_checked'] = datetime.utcnow().isoformat()

                if notes:
                    vehicle.setdefault('notes', []).append({
                        'timestamp': datetime.utcnow().isoformat(),
                        'note': notes
                    })

                # 저장
                db['metadata']['last_updated'] = datetime.utcnow().isoformat()
                self._save_db(db)

                return vehicle

        return None

    def update_detection(self, vehicle_id: str, similarity_score: float, risk_level: str):
        """
        차량 재감지 시 이력 업데이트

        Args:
            vehicle_id: 차량 ID
            similarity_score: 유사도 점수
            risk_level: 위험도
        """
        db = self._load_db()

        for vehicle in db['vehicles']:
            if vehicle['id'] == vehicle_id:
                vehicle['last_checked'] = datetime.utcnow().isoformat()
                vehicle['detection_count'] = vehicle.get('detection_count', 0) + 1
                vehicle['risk_level'] = risk_level

                # 평균 유사도 업데이트
                if 'avg_similarity' in vehicle:
                    count = vehicle['detection_count']
                    vehicle['avg_similarity'] = (
                        vehicle['avg_similarity'] * (count - 1) + similarity_score
                    ) / count
                else:
                    vehicle['avg_similarity'] = similarity_score

                # 최고 유사도 업데이트
                if 'max_similarity' not in vehicle or similarity_score > vehicle['max_similarity']:
                    vehicle['max_similarity'] = similarity_score

                # 저장
                db['metadata']['last_updated'] = datetime.utcnow().isoformat()
                self._save_db(db)

                return vehicle

        return None

    def get_all_vehicles(
        self,
        status_filter: Optional[str] = None,
        risk_level_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        전체 방치 차량 조회 (필터 옵션)

        Args:
            status_filter: 상태 필터 (DETECTED, INVESTIGATING, RESOLVED)
            risk_level_filter: 위험도 필터 (CRITICAL, HIGH, MEDIUM, LOW)

        Returns:
            방치 차량 목록
        """
        db = self._load_db()
        vehicles = db['vehicles']

        # 필터 적용
        if status_filter:
            vehicles = [v for v in vehicles if v['status'] == status_filter]

        if risk_level_filter:
            vehicles = [v for v in vehicles if v['risk_level'] == risk_level_filter]

        return vehicles

    def delete_vehicle(self, vehicle_id: str) -> bool:
        """
        차량 삭제 (처리 완료 시)

        Args:
            vehicle_id: 차량 ID

        Returns:
            삭제 성공 여부
        """
        db = self._load_db()

        original_count = len(db['vehicles'])
        db['vehicles'] = [v for v in db['vehicles'] if v['id'] != vehicle_id]

        if len(db['vehicles']) < original_count:
            # 메타데이터 업데이트
            db['metadata']['total_vehicles'] = len(db['vehicles'])
            db['metadata']['last_updated'] = datetime.utcnow().isoformat()

            # 저장
            self._save_db(db)
            return True

        return False

    def get_statistics(self) -> Dict:
        """
        통계 정보 조회

        Returns:
            {
                "total_vehicles": 1247,
                "by_status": {"DETECTED": 1200, "INVESTIGATING": 40, "RESOLVED": 7},
                "by_risk_level": {"CRITICAL": 350, "HIGH": 450, "MEDIUM": 300, "LOW": 147},
                "by_vehicle_type": {"car": 1000, "truck": 200, "bus": 47},
                "last_updated": "2025-01-26T10:30:00"
            }
        """
        db = self._load_db()
        vehicles = db['vehicles']

        # 상태별 통계
        by_status = {}
        for status in ['DETECTED', 'INVESTIGATING', 'RESOLVED']:
            by_status[status] = len([v for v in vehicles if v['status'] == status])

        # 위험도별 통계
        by_risk_level = {}
        for risk in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            by_risk_level[risk] = len([v for v in vehicles if v['risk_level'] == risk])

        # 차량 타입별 통계
        by_vehicle_type = {}
        for vehicle in vehicles:
            vtype = vehicle.get('vehicle_type', 'unknown')
            by_vehicle_type[vtype] = by_vehicle_type.get(vtype, 0) + 1

        return {
            "total_vehicles": len(vehicles),
            "by_status": by_status,
            "by_risk_level": by_risk_level,
            "by_vehicle_type": by_vehicle_type,
            "last_updated": db['metadata']['last_updated'],
            "total_scans": db['metadata'].get('total_scans', 0)
        }


# 싱글톤 인스턴스
_storage_instance = None


def get_storage() -> AbandonedVehicleStorage:
    """
    싱글톤 저장소 인스턴스 반환
    """
    global _storage_instance

    if _storage_instance is None:
        _storage_instance = AbandonedVehicleStorage()

    return _storage_instance


# 테스트
if __name__ == "__main__":
    print("=" * 60)
    print("Abandoned Vehicle Storage 테스트")
    print("=" * 60)

    storage = get_storage()

    # 테스트 1: 차량 추가
    print("\n[테스트 1] 방치 차량 추가")
    test_vehicle = storage.add_vehicle({
        "latitude": 37.5172,
        "longitude": 127.0473,
        "address": "서울특별시 강남구",
        "vehicle_type": "car",
        "similarity_score": 0.95,
        "risk_level": "CRITICAL",
        "years_difference": 3,
        "bbox": {"x": 350, "y": 220, "w": 85, "h": 60}
    })
    print(f"  추가된 차량 ID: {test_vehicle['id']}")
    print(f"  위치: {test_vehicle['address']}")
    print(f"  위험도: {test_vehicle['risk_level']}")

    # 테스트 2: 지역 내 차량 조회
    print("\n[테스트 2] 강남구 인근 500m 내 차량 조회")
    nearby_vehicles = storage.get_vehicles_in_area(37.5172, 127.0473, radius=500)
    print(f"  발견된 차량: {len(nearby_vehicles)}대")

    # 테스트 3: 통계
    print("\n[테스트 3] 전체 통계")
    stats = storage.get_statistics()
    print(f"  전체 차량: {stats['total_vehicles']}대")
    print(f"  위험도별: {stats['by_risk_level']}")
    print(f"  상태별: {stats['by_status']}")

    print("\n" + "=" * 60)
    print(f"✅ DB 파일 저장 위치: {DB_FILE}")
    print("=" * 60)
