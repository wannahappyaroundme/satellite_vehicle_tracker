"""
SQLite 데이터베이스 초기화 스크립트
방치 차량 탐지 시스템용 테이블 생성

실행 방법:
    python create_db.py
"""

import os
import sys
from pathlib import Path

# 현재 디렉토리를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from database import Base, engine, SessionLocal
from models_sqlalchemy import AbandonedVehicle, AnalysisLog


def create_database():
    """
    SQLite 데이터베이스 및 테이블 생성
    """
    print("=" * 60)
    print("SQLite 데이터베이스 초기화 시작")
    print("=" * 60)

    # 데이터베이스 파일 경로 확인
    db_path = "satellite_tracker.db"

    if os.path.exists(db_path):
        print(f"\n⚠️  기존 데이터베이스 발견: {db_path}")
        response = input("기존 데이터베이스를 삭제하고 새로 만들까요? (y/N): ")

        if response.lower() == 'y':
            os.remove(db_path)
            print(f"✅ 기존 데이터베이스 삭제 완료")
        else:
            print("❌ 초기화 취소됨")
            return

    try:
        # 테이블 생성
        print(f"\n📊 테이블 생성 중...")
        Base.metadata.create_all(bind=engine)

        print("\n✅ 다음 테이블이 생성되었습니다:")
        print(f"   - {AbandonedVehicle.__tablename__} (방치 차량 데이터)")
        print(f"   - {AnalysisLog.__tablename__} (분석 실행 로그)")

        # 데이터베이스 연결 테스트
        print(f"\n🔍 데이터베이스 연결 테스트...")
        db = SessionLocal()

        try:
            # 빈 쿼리 실행 (연결 확인용)
            vehicle_count = db.query(AbandonedVehicle).count()
            log_count = db.query(AnalysisLog).count()

            print(f"   - abandoned_vehicles: {vehicle_count}개")
            print(f"   - analysis_logs: {log_count}개")

        finally:
            db.close()

        # 인덱스 정보 출력
        print(f"\n📇 생성된 인덱스:")
        print(f"   - idx_location (latitude, longitude)")
        print(f"   - idx_city_district (city, district)")
        print(f"   - idx_status_risk (status, risk_level)")
        print(f"   - idx_first_detected (first_detected)")
        print(f"   - idx_last_detected (last_detected)")
        print(f"   - idx_status_city (status, city)")

        print("\n" + "=" * 60)
        print("✅ 데이터베이스 초기화 완료!")
        print("=" * 60)
        print(f"\n📁 데이터베이스 파일: {os.path.abspath(db_path)}")
        print(f"📏 파일 크기: {os.path.getsize(db_path)} bytes")

        print("\n다음 단계:")
        print("  1. 기존 JSON 데이터 마이그레이션: python migrate_json_to_sqlite.py")
        print("  2. FastAPI 서버 재시작: python fastapi_app.py")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def verify_database_structure():
    """
    데이터베이스 구조 검증
    """
    print("\n" + "=" * 60)
    print("데이터베이스 구조 검증")
    print("=" * 60)

    from sqlalchemy import inspect

    inspector = inspect(engine)

    # AbandonedVehicle 테이블 검증
    print(f"\n[{AbandonedVehicle.__tablename__}]")
    columns = inspector.get_columns(AbandonedVehicle.__tablename__)

    print(f"\n컬럼 목록 ({len(columns)}개):")
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        print(f"  - {col['name']:25} {str(col['type']):15} {nullable}")

    # 인덱스 검증
    indexes = inspector.get_indexes(AbandonedVehicle.__tablename__)
    print(f"\n인덱스 목록 ({len(indexes)}개):")
    for idx in indexes:
        columns_str = ', '.join(idx['column_names'])
        unique = "UNIQUE" if idx.get('unique') else ""
        print(f"  - {idx['name']:30} ({columns_str}) {unique}")

    # AnalysisLog 테이블 검증
    print(f"\n[{AnalysisLog.__tablename__}]")
    columns = inspector.get_columns(AnalysisLog.__tablename__)

    print(f"\n컬럼 목록 ({len(columns)}개):")
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        print(f"  - {col['name']:25} {str(col['type']):15} {nullable}")

    print("\n✅ 구조 검증 완료")


if __name__ == "__main__":
    create_database()
    verify_database_structure()
