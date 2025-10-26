"""
JSON to SQLite Migration Script
기존 abandoned_vehicles_db.json 데이터를 SQLite로 마이그레이션

실행 방법:
    python migrate_json_to_sqlite.py
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 현재 디렉토리를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from models_sqlalchemy import AbandonedVehicle


# JSON 파일 경로
JSON_FILE = os.path.join(os.path.dirname(__file__), 'data', 'abandoned_vehicles_db.json')


def parse_iso_datetime(iso_string):
    """
    ISO 8601 형식 문자열을 datetime 객체로 변환

    Args:
        iso_string: ISO 8601 형식 문자열

    Returns:
        datetime 객체 또는 None
    """
    if not iso_string:
        return None

    try:
        # ISO 8601 형식 파싱
        return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    except Exception as e:
        print(f"⚠️  날짜 파싱 실패: {iso_string} ({e})")
        return datetime.utcnow()


def extract_city_district_from_address(address):
    """
    주소에서 시/도, 구/군 추출

    Args:
        address: 전체 주소 (예: "서울특별시 강남구")

    Returns:
        (city, district) 튜플
    """
    if not address:
        return None, None

    parts = address.split()

    city = None
    district = None

    # 첫 번째 파트: 시/도
    if len(parts) >= 1:
        city = parts[0]

    # 두 번째 파트: 구/군
    if len(parts) >= 2:
        district = parts[1]

    return city, district


def migrate_json_to_sqlite():
    """
    JSON 데이터를 SQLite로 마이그레이션
    """
    print("=" * 60)
    print("JSON → SQLite 마이그레이션 시작")
    print("=" * 60)

    # JSON 파일 존재 확인
    if not os.path.exists(JSON_FILE):
        print(f"\n⚠️  JSON 파일을 찾을 수 없습니다: {JSON_FILE}")
        print("마이그레이션할 데이터가 없습니다.")
        return

    # JSON 데이터 로드
    print(f"\n📂 JSON 파일 로드 중: {JSON_FILE}")

    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ JSON 파일 로드 실패: {e}")
        return

    vehicles_data = data.get('vehicles', [])
    metadata = data.get('metadata', {})

    print(f"✅ {len(vehicles_data)}개의 차량 데이터 로드 완료")
    print(f"\nJSON 메타데이터:")
    print(f"  - 총 차량: {metadata.get('total_vehicles', 0)}")
    print(f"  - 마지막 업데이트: {metadata.get('last_updated', 'N/A')}")
    print(f"  - 총 스캔 횟수: {metadata.get('total_scans', 0)}")

    # 데이터베이스 연결
    db = SessionLocal()

    try:
        # 기존 데이터 확인
        existing_count = db.query(AbandonedVehicle).count()

        if existing_count > 0:
            print(f"\n⚠️  데이터베이스에 이미 {existing_count}개의 차량 데이터가 있습니다.")
            response = input("기존 데이터를 삭제하고 새로 추가할까요? (y/N): ")

            if response.lower() == 'y':
                db.query(AbandonedVehicle).delete()
                db.commit()
                print(f"✅ 기존 데이터 삭제 완료")
            else:
                print("❌ 마이그레이션 취소됨")
                return

        # 마이그레이션 시작
        print(f"\n🔄 마이그레이션 진행 중...")

        migrated_count = 0
        skipped_count = 0
        error_count = 0

        for idx, vehicle_json in enumerate(vehicles_data, 1):
            try:
                # 주소에서 city, district 추출
                address = vehicle_json.get('address', '')
                city, district = extract_city_district_from_address(address)

                # SQLAlchemy 모델 인스턴스 생성
                vehicle = AbandonedVehicle(
                    vehicle_id=vehicle_json.get('id'),

                    # Location
                    latitude=vehicle_json.get('latitude'),
                    longitude=vehicle_json.get('longitude'),
                    city=city,
                    district=district,
                    address=address,

                    # Vehicle Info
                    vehicle_type=vehicle_json.get('vehicle_type'),

                    # Detection Info
                    similarity_score=vehicle_json.get('similarity_score'),
                    similarity_percentage=vehicle_json.get('similarity_percentage',
                                                          vehicle_json.get('similarity_score', 0) * 100),
                    risk_level=vehicle_json.get('risk_level'),
                    years_difference=vehicle_json.get('years_difference'),

                    # History
                    first_detected=parse_iso_datetime(vehicle_json.get('first_detected')),
                    last_detected=parse_iso_datetime(vehicle_json.get('last_checked')),  # JSON은 last_checked
                    detection_count=vehicle_json.get('detection_count', 1),

                    # Similarity Stats
                    avg_similarity=vehicle_json.get('avg_similarity'),
                    max_similarity=vehicle_json.get('max_similarity'),

                    # Management
                    status=vehicle_json.get('status', 'DETECTED'),
                    verification_notes=None,  # JSON에는 없음

                    # Metadata
                    bbox_data=vehicle_json.get('bbox'),
                    metadata=vehicle_json.get('metadata'),
                )

                # 데이터베이스에 추가
                db.add(vehicle)
                migrated_count += 1

                # 진행 상황 출력 (10개마다)
                if idx % 10 == 0:
                    print(f"  진행: {idx}/{len(vehicles_data)} ({migrated_count}개 성공)")

            except Exception as e:
                error_count += 1
                print(f"  ⚠️  차량 {idx} 마이그레이션 실패: {e}")
                continue

        # 커밋
        print(f"\n💾 데이터베이스에 커밋 중...")
        db.commit()

        # 결과 출력
        print("\n" + "=" * 60)
        print("✅ 마이그레이션 완료!")
        print("=" * 60)
        print(f"\n📊 결과:")
        print(f"  - 성공: {migrated_count}개")
        print(f"  - 실패: {error_count}개")
        print(f"  - 총계: {len(vehicles_data)}개")

        # 데이터베이스 검증
        print(f"\n🔍 데이터베이스 검증...")
        final_count = db.query(AbandonedVehicle).count()
        print(f"  - 최종 차량 수: {final_count}개")

        # 통계 출력
        print(f"\n📈 통계:")

        # 위험도별 통계
        for risk_level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = db.query(AbandonedVehicle).filter(
                AbandonedVehicle.risk_level == risk_level
            ).count()
            print(f"  - {risk_level}: {count}개")

        # 상태별 통계
        print(f"\n상태별 통계:")
        for status in ['DETECTED', 'INVESTIGATING', 'VERIFIED', 'RESOLVED']:
            count = db.query(AbandonedVehicle).filter(
                AbandonedVehicle.status == status
            ).count()
            print(f"  - {status}: {count}개")

        print("\n다음 단계:")
        print("  1. FastAPI 서버 재시작: python fastapi_app.py")
        print("  2. 프론트엔드 확인: http://localhost:3000")

    except Exception as e:
        db.rollback()
        print(f"\n❌ 마이그레이션 오류: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


def verify_migration():
    """
    마이그레이션 결과 검증
    """
    print("\n" + "=" * 60)
    print("마이그레이션 결과 검증")
    print("=" * 60)

    db = SessionLocal()

    try:
        # 샘플 데이터 조회
        print(f"\n샘플 데이터 (최근 5개):")

        vehicles = db.query(AbandonedVehicle).order_by(
            AbandonedVehicle.first_detected.desc()
        ).limit(5).all()

        for vehicle in vehicles:
            print(f"\n  [{vehicle.vehicle_id}]")
            print(f"    위치: {vehicle.address}")
            print(f"    위험도: {vehicle.risk_level}")
            print(f"    유사도: {vehicle.similarity_percentage:.1f}%")
            print(f"    상태: {vehicle.status}")
            print(f"    최초 감지: {vehicle.first_detected}")

    finally:
        db.close()


if __name__ == "__main__":
    migrate_json_to_sqlite()
    verify_migration()
