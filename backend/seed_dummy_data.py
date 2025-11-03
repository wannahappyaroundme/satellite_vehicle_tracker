#!/usr/bin/env python3
"""
더미 데이터 생성 스크립트
- 36대의 장기 방치 차량 데이터 생성
- 소형차 70% (25대), 대형차/트럭 30% (11대)
- 다양한 위험도 레벨 (CRITICAL, HIGH, MEDIUM, LOW)
- 전국 주요 도시 분포
- SQLite DB에 영구 저장
"""

import sys
import os
import random
from datetime import datetime
from pathlib import Path

# backend 디렉토리를 Python 경로에 추가
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database import get_db
from models_sqlalchemy import AbandonedVehicle


# 전국 주요 도시 좌표 (실제 한국 좌표)
LOCATIONS = [
    {"city": "서울 강남구", "lat": 37.4979, "lng": 127.0276},
    {"city": "서울 종로구", "lat": 37.5735, "lng": 126.9788},
    {"city": "서울 마포구", "lat": 37.5663, "lng": 126.9019},
    {"city": "부산 해운대구", "lat": 35.1631, "lng": 129.1633},
    {"city": "부산 부산진구", "lat": 35.1628, "lng": 129.0537},
    {"city": "대구 중구", "lat": 35.8694, "lng": 128.6067},
    {"city": "인천 남동구", "lat": 37.4475, "lng": 126.7311},
    {"city": "광주 서구", "lat": 35.1524, "lng": 126.8899},
    {"city": "대전 유성구", "lat": 36.3624, "lng": 127.3563},
    {"city": "울산 남구", "lat": 35.5441, "lng": 129.3311},
    {"city": "경기 수원시", "lat": 37.2636, "lng": 127.0286},
    {"city": "경기 성남시", "lat": 37.4449, "lng": 127.1389},
    {"city": "경기 고양시", "lat": 37.6584, "lng": 126.8320},
    {"city": "제주 제주시", "lat": 33.4996, "lng": 126.5312},
    {"city": "강원 춘천시", "lat": 37.8813, "lng": 127.7300},
]

# 위험도 분포 (실제 배율 고려)
RISK_LEVELS = [
    {"level": "CRITICAL", "weight": 3},  # 약 20%
    {"level": "HIGH", "weight": 5},      # 약 35%
    {"level": "MEDIUM", "weight": 4},    # 약 28%
    {"level": "LOW", "weight": 2},       # 약 14%
]

# 차량 타입 (소형차 70%, 대형차/트럭 30%)
VEHICLE_TYPES = [
    {"type": "small-vehicle", "weight": 7},   # 70%
    {"type": "large-vehicle", "weight": 2},   # 20%
    {"type": "truck", "weight": 1},           # 10%
]


def weighted_choice(choices):
    """가중치 기반 랜덤 선택"""
    total = sum(c["weight"] for c in choices)
    r = random.uniform(0, total)
    upto = 0
    for choice in choices:
        if upto + choice["weight"] >= r:
            return choice
        upto += choice["weight"]
    return choices[-1]


def generate_similarity_by_risk(risk_level):
    """위험도에 따른 유사도 생성"""
    if risk_level == "CRITICAL":
        return round(random.uniform(0.95, 0.99), 4)
    elif risk_level == "HIGH":
        return round(random.uniform(0.90, 0.949), 4)
    elif risk_level == "MEDIUM":
        return round(random.uniform(0.85, 0.899), 4)
    else:  # LOW
        return round(random.uniform(0.75, 0.849), 4)


def generate_years_by_risk(risk_level):
    """위험도에 따른 방치 기간 생성"""
    if risk_level == "CRITICAL":
        year1 = random.randint(2015, 2018)
        year2 = year1 + random.randint(3, 6)
    elif risk_level == "HIGH":
        year1 = random.randint(2017, 2020)
        year2 = year1 + random.randint(2, 4)
    elif risk_level == "MEDIUM":
        year1 = random.randint(2019, 2021)
        year2 = year1 + random.randint(1, 3)
    else:  # LOW
        year1 = random.randint(2020, 2022)
        year2 = year1 + random.randint(1, 2)

    return year1, min(year2, 2024)


def generate_vehicle_description(vehicle_type, risk_level):
    """차량 타입에 따른 설명 생성"""
    colors = ["검정색", "흰색", "은색", "파란색", "빨간색", "회색"]
    brands_small = ["현대", "기아", "쉐보레", "르노삼성", "쌍용"]
    brands_large = ["현대", "기아", "쌍용"]
    brands_truck = ["현대", "기아", "타타대우"]

    color = random.choice(colors)

    if vehicle_type == "small-vehicle":
        brand = random.choice(brands_small)
        models = ["소나타", "아반떼", "K5", "스파크", "모닝", "SM3"]
        model = random.choice(models)
        return f"{color} {brand} {model} (승용차)"
    elif vehicle_type == "large-vehicle":
        brand = random.choice(brands_large)
        models = ["카니발", "스타렉스", "G4 렉스턴"]
        model = random.choice(models)
        return f"{color} {brand} {model} (대형 승합차)"
    else:  # truck
        brand = random.choice(brands_truck)
        models = ["포터", "봉고", "타우너"]
        model = random.choice(models)
        return f"{color} {brand} {model} (화물차)"


def generate_dummy_vehicles(count=36):
    """더미 차량 데이터 생성"""
    vehicles = []

    for i in range(count):
        # 위험도 선택
        risk_choice = weighted_choice(RISK_LEVELS)
        risk_level = risk_choice["level"]

        # 차량 타입 선택
        vehicle_choice = weighted_choice(VEHICLE_TYPES)
        vehicle_type = vehicle_choice["type"]

        # 위치 선택
        location = random.choice(LOCATIONS)

        # 좌표에 약간의 랜덤성 추가 (같은 도시 내 다른 위치)
        lat = location["lat"] + random.uniform(-0.01, 0.01)
        lng = location["lng"] + random.uniform(-0.01, 0.01)

        # 유사도 및 연도 생성
        similarity = generate_similarity_by_risk(risk_level)
        year1, year2 = generate_years_by_risk(risk_level)
        years_diff = year2 - year1

        # 차량 설명
        description = generate_vehicle_description(vehicle_type, risk_level)

        # 도시명에서 시/도와 구/군 분리
        city_parts = location["city"].split()
        city = city_parts[0] if len(city_parts) > 0 else location["city"]
        district = city_parts[1] if len(city_parts) > 1 else ""

        # Unique vehicle_id 생성
        vehicle_id = f"VH{datetime.now().strftime('%Y%m%d')}{i:04d}"

        # Bounding box 더미 데이터
        bbox = {
            "x": random.randint(100, 800),
            "y": random.randint(100, 600),
            "w": random.randint(60, 120),
            "h": random.randint(40, 90)
        }

        # 메타데이터
        metadata = {
            "year1": year1,
            "year2": year2,
            "description": description,
            "confidence": round(random.uniform(0.85, 0.98), 4),
        }

        vehicle = {
            "vehicle_id": vehicle_id,
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "city": city,
            "district": district,
            "address": location["city"],
            "vehicle_type": vehicle_type,
            "similarity_score": similarity,
            "similarity_percentage": similarity * 100,
            "risk_level": risk_level,
            "years_difference": years_diff,
            "first_detected": datetime.now(),
            "last_detected": datetime.now(),
            "detection_count": random.randint(1, 5),
            "avg_similarity": similarity,
            "max_similarity": min(similarity + random.uniform(0, 0.05), 1.0),
            "status": "DETECTED",
            "bbox_data": bbox,
            "extra_metadata": metadata,
        }

        vehicles.append(vehicle)

    return vehicles


def seed_database():
    """더미 데이터를 DB에 삽입"""
    print("=" * 60)
    print("장기 방치 차량 더미 데이터 생성 시작")
    print("=" * 60)

    # 더미 데이터 생성
    vehicles = generate_dummy_vehicles(36)

    # 통계 출력
    print(f"\n총 {len(vehicles)}대의 차량 데이터 생성 완료")

    # 차량 타입별 통계
    type_counts = {}
    for v in vehicles:
        vtype = v["vehicle_type"]
        type_counts[vtype] = type_counts.get(vtype, 0) + 1

    print("\n[차량 타입별 분포]")
    for vtype, count in sorted(type_counts.items()):
        percentage = (count / len(vehicles)) * 100
        print(f"  - {vtype}: {count}대 ({percentage:.1f}%)")

    # 위험도별 통계
    risk_counts = {}
    for v in vehicles:
        risk = v["risk_level"]
        risk_counts[risk] = risk_counts.get(risk, 0) + 1

    print("\n[위험도별 분포]")
    for risk in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = risk_counts.get(risk, 0)
        percentage = (count / len(vehicles)) * 100
        print(f"  - {risk}: {count}대 ({percentage:.1f}%)")

    # 지역별 통계
    location_counts = {}
    for v in vehicles:
        loc = v["address"]  # location_name -> address
        location_counts[loc] = location_counts.get(loc, 0) + 1

    print("\n[지역별 분포 (상위 5개)]")
    sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for loc, count in sorted_locations:
        print(f"  - {loc}: {count}대")

    # DB에 삽입
    print("\n" + "=" * 60)
    print("SQLite 데이터베이스에 삽입 중...")
    print("=" * 60)

    db = next(get_db())

    try:
        # 기존 데이터 삭제 (선택 사항 - 주석 처리하면 누적됨)
        existing_count = db.query(AbandonedVehicle).count()
        print(f"\n기존 데이터: {existing_count}개")

        # 새 데이터 삽입
        inserted_count = 0
        for vehicle_data in vehicles:
            vehicle = AbandonedVehicle(**vehicle_data)
            db.add(vehicle)
            inserted_count += 1

        db.commit()

        print(f"✅ 새로 삽입된 데이터: {inserted_count}개")

        total_count = db.query(AbandonedVehicle).count()
        print(f"✅ 총 데이터: {total_count}개")

        # 샘플 데이터 출력
        print("\n[샘플 데이터 미리보기]")
        samples = db.query(AbandonedVehicle).limit(3).all()
        for i, sample in enumerate(samples, 1):
            metadata = sample.extra_metadata or {}
            description = metadata.get("description", "설명 없음")
            year1 = metadata.get("year1", "?")
            year2 = metadata.get("year2", "?")

            print(f"\n{i}. {description}")
            print(f"   위치: {sample.address} ({sample.latitude}, {sample.longitude})")
            print(f"   유사도: {sample.similarity_score:.2%}")
            print(f"   위험도: {sample.risk_level}")
            print(f"   연도: {year1} → {year2}")

        print("\n" + "=" * 60)
        print("✅ 더미 데이터 생성 완료!")
        print("=" * 60)
        print("\n다음 명령어로 FastAPI 서버를 시작하세요:")
        print("  cd backend && python fastapi_app.py")
        print("\n또는 프론트엔드에서 바로 확인:")
        print("  http://localhost:3000")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"\n❌ 에러 발생: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
