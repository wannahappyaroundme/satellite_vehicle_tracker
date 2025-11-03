#!/usr/bin/env python3
"""
SQLite DB에 저장된 더미 데이터 확인 스크립트
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database import get_db
from models_sqlalchemy import AbandonedVehicle


def test_database():
    """DB 데이터 확인"""
    print("=" * 60)
    print("SQLite 데이터베이스 확인")
    print("=" * 60)

    db = next(get_db())

    try:
        # 전체 데이터 개수
        total = db.query(AbandonedVehicle).count()
        print(f"\n총 차량 수: {total}개")

        if total == 0:
            print("❌ 데이터가 없습니다! seed_dummy_data.py를 실행하세요.")
            return

        # 위험도별 통계
        print("\n[위험도별 분포]")
        for risk in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            count = db.query(AbandonedVehicle).filter(
                AbandonedVehicle.risk_level == risk
            ).count()
            percentage = (count / total) * 100 if total > 0 else 0
            print(f"  {risk}: {count}대 ({percentage:.1f}%)")

        # 차량 타입별 통계
        print("\n[차량 타입별 분포]")
        for vtype in ["small-vehicle", "large-vehicle", "truck"]:
            count = db.query(AbandonedVehicle).filter(
                AbandonedVehicle.vehicle_type == vtype
            ).count()
            percentage = (count / total) * 100 if total > 0 else 0
            print(f"  {vtype}: {count}대 ({percentage:.1f}%)")

        # 샘플 데이터 (최신 5개)
        print("\n[최신 데이터 5개 샘플]")
        samples = (
            db.query(AbandonedVehicle)
            .order_by(AbandonedVehicle.created_at.desc())
            .limit(5)
            .all()
        )

        for i, sample in enumerate(samples, 1):
            metadata = sample.extra_metadata or {}
            description = metadata.get("description", "설명 없음")
            year1 = metadata.get("year1", "?")
            year2 = metadata.get("year2", "?")

            print(f"\n{i}. [{sample.vehicle_id}] {description}")
            print(f"   위치: {sample.address or sample.city}")
            print(f"   좌표: ({sample.latitude}, {sample.longitude})")
            print(f"   유사도: {sample.similarity_score:.2%} (위험도: {sample.risk_level})")
            print(f"   연도: {year1} → {year2} ({sample.years_difference}년 차이)")
            print(f"   상태: {sample.status}")

        # JSON 형식으로 하나 출력 (API 응답 확인용)
        print("\n[API 응답 형식 샘플]")
        if samples:
            import json
            sample_dict = samples[0].to_dict()
            print(json.dumps(sample_dict, indent=2, ensure_ascii=False))

        print("\n" + "=" * 60)
        print("✅ 데이터베이스 확인 완료!")
        print("=" * 60)
        print("\n다음 단계:")
        print("1. 로컬 FastAPI 서버 시작:")
        print("   cd backend && python fastapi_app.py")
        print("\n2. 프론트엔드에서 확인:")
        print("   http://localhost:3000")
        print("\n3. Lightsail에 배포:")
        print("   - 로컬에서 확인 후 Lightsail SSH에서 seed_dummy_data.py 실행")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    test_database()
