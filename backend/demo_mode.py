"""
Demo Mode - API 없이 작동하는 데모 데이터
Works without NGII API key - uses mock data and sample images
"""

import random
from typing import Dict, List

# 주요 도시 좌표 데이터
CITY_COORDINATES = {
    "서울특별시": {
        "강남구": {"latitude": 37.5172, "longitude": 127.0473, "address": "서울특별시 강남구"},
        "강동구": {"latitude": 37.5301, "longitude": 127.1238, "address": "서울특별시 강동구"},
        "강북구": {"latitude": 37.6396, "longitude": 127.0257, "address": "서울특별시 강북구"},
        "강서구": {"latitude": 37.5509, "longitude": 126.8495, "address": "서울특별시 강서구"},
        "관악구": {"latitude": 37.4784, "longitude": 126.9516, "address": "서울특별시 관악구"},
        "광진구": {"latitude": 37.5384, "longitude": 127.0822, "address": "서울특별시 광진구"},
        "구로구": {"latitude": 37.4954, "longitude": 126.8874, "address": "서울특별시 구로구"},
        "금천구": {"latitude": 37.4519, "longitude": 126.9021, "address": "서울특별시 금천구"},
        "노원구": {"latitude": 37.6542, "longitude": 127.0568, "address": "서울특별시 노원구"},
        "도봉구": {"latitude": 37.6688, "longitude": 127.0471, "address": "서울특별시 도봉구"},
        "동대문구": {"latitude": 37.5744, "longitude": 127.0396, "address": "서울특별시 동대문구"},
        "동작구": {"latitude": 37.5124, "longitude": 126.9393, "address": "서울특별시 동작구"},
        "마포구": {"latitude": 37.5663, "longitude": 126.9019, "address": "서울특별시 마포구"},
        "서대문구": {"latitude": 37.5791, "longitude": 126.9368, "address": "서울특별시 서대문구"},
        "서초구": {"latitude": 37.4837, "longitude": 127.0324, "address": "서울특별시 서초구"},
        "성동구": {"latitude": 37.5634, "longitude": 127.0368, "address": "서울특별시 성동구"},
        "성북구": {"latitude": 37.5894, "longitude": 127.0167, "address": "서울특별시 성북구"},
        "송파구": {"latitude": 37.5145, "longitude": 127.1059, "address": "서울특별시 송파구"},
        "양천구": {"latitude": 37.5170, "longitude": 126.8664, "address": "서울특별시 양천구"},
        "영등포구": {"latitude": 37.5264, "longitude": 126.8963, "address": "서울특별시 영등포구"},
        "용산구": {"latitude": 37.5324, "longitude": 126.9902, "address": "서울특별시 용산구"},
        "은평구": {"latitude": 37.6027, "longitude": 126.9291, "address": "서울특별시 은평구"},
        "종로구": {"latitude": 37.5735, "longitude": 126.9788, "address": "서울특별시 종로구"},
        "중구": {"latitude": 37.5636, "longitude": 126.9977, "address": "서울특별시 중구"},
        "중랑구": {"latitude": 37.6063, "longitude": 127.0929, "address": "서울특별시 중랑구"},
    },
    "부산광역시": {
        "강서구": {"latitude": 35.2117, "longitude": 128.9803, "address": "부산광역시 강서구"},
        "금정구": {"latitude": 35.2428, "longitude": 129.0928, "address": "부산광역시 금정구"},
        "남구": {"latitude": 35.1364, "longitude": 129.0844, "address": "부산광역시 남구"},
        "동구": {"latitude": 35.1295, "longitude": 129.0456, "address": "부산광역시 동구"},
        "해운대구": {"latitude": 35.1631, "longitude": 129.1635, "address": "부산광역시 해운대구"},
    },
    "인천광역시": {
        "계양구": {"latitude": 37.5375, "longitude": 126.7375, "address": "인천광역시 계양구"},
        "남동구": {"latitude": 37.4476, "longitude": 126.7310, "address": "인천광역시 남동구"},
        "연수구": {"latitude": 37.4104, "longitude": 126.6777, "address": "인천광역시 연수구"},
    },
    "대전광역시": {
        "대덕구": {"latitude": 36.3468, "longitude": 127.4167, "address": "대전광역시 대덕구"},
        "동구": {"latitude": 36.3114, "longitude": 127.4549, "address": "대전광역시 동구"},
        "서구": {"latitude": 36.3553, "longitude": 127.3838, "address": "대전광역시 서구"},
        "유성구": {"latitude": 36.3621, "longitude": 127.3567, "address": "대전광역시 유성구"},
        "중구": {"latitude": 36.3254, "longitude": 127.4214, "address": "대전광역시 중구"},
    },
    "제주특별자치도": {
        "제주시": {"latitude": 33.4996, "longitude": 126.5312, "address": "제주특별자치도 제주시"},
        "서귀포시": {"latitude": 33.2541, "longitude": 126.5601, "address": "제주특별자치도 서귀포시"},
    },
    "경기도": {
        "수원시": {"latitude": 37.2636, "longitude": 127.0286, "address": "경기도 수원시"},
        "성남시": {"latitude": 37.4201, "longitude": 127.1262, "address": "경기도 성남시"},
        "안양시": {"latitude": 37.3943, "longitude": 126.9568, "address": "경기도 안양시"},
        "용인시": {"latitude": 37.2410, "longitude": 127.1776, "address": "경기도 용인시"},
        "고양시": {"latitude": 37.6584, "longitude": 126.8320, "address": "경기도 고양시"},
        "화성시": {"latitude": 37.1995, "longitude": 126.8310, "address": "경기도 화성시"},
    }
}


def get_demo_coordinates(sido: str = None, sigungu: str = None) -> Dict:
    """
    데모 모드 좌표 반환 (API 없이)

    Args:
        sido: 시/도
        sigungu: 시/군/구

    Returns:
        좌표 및 주소 정보
    """
    # 시/도가 없으면 서울 강남구 기본
    if not sido:
        return {
            "success": True,
            "address": "서울특별시 강남구",
            "latitude": 37.5172,
            "longitude": 127.0473,
            "mode": "demo",
            "message": "🎭 데모 모드 - API 키 없이 샘플 데이터 사용"
        }

    # 해당 시/도 데이터 찾기
    if sido in CITY_COORDINATES:
        if sigungu and sigungu in CITY_COORDINATES[sido]:
            data = CITY_COORDINATES[sido][sigungu]
            return {
                "success": True,
                "address": data["address"],
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "mode": "demo",
                "message": "🎭 데모 모드 - API 키 없이 샘플 데이터 사용"
            }
        else:
            # 시/군/구가 없으면 첫 번째 구 반환
            first_gu = list(CITY_COORDINATES[sido].values())[0]
            return {
                "success": True,
                "address": first_gu["address"],
                "latitude": first_gu["latitude"],
                "longitude": first_gu["longitude"],
                "mode": "demo",
                "message": "🎭 데모 모드 - API 키 없이 샘플 데이터 사용"
            }

    # 찾을 수 없으면 서울 강남구
    return {
        "success": True,
        "address": "서울특별시 강남구 (기본)",
        "latitude": 37.5172,
        "longitude": 127.0473,
        "mode": "demo",
        "message": "🎭 데모 모드 - 해당 지역을 찾을 수 없어 기본 위치 사용"
    }


def generate_mock_abandoned_vehicles(latitude: float, longitude: float, count: int = 5) -> List[Dict]:
    """
    Mock 방치 차량 데이터 생성

    Args:
        latitude: 중심 위도
        longitude: 중심 경도
        count: 생성할 차량 수

    Returns:
        방치 차량 목록
    """
    vehicles = []
    risk_levels = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']

    for i in range(count):
        # 중심에서 약간씩 떨어진 위치 (반경 500m 내)
        offset_lat = random.uniform(-0.005, 0.005)
        offset_lng = random.uniform(-0.005, 0.005)

        # 유사도 (85-98%)
        similarity = random.uniform(0.85, 0.98)

        # 위험도
        if similarity >= 0.95:
            risk_level = 'CRITICAL'
        elif similarity >= 0.92:
            risk_level = 'HIGH'
        elif similarity >= 0.88:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'

        # 경과 년수 (1-5년)
        years = random.randint(1, 5)

        vehicle = {
            "id": f"demo_vehicle_{i}",
            "latitude": latitude + offset_lat,
            "longitude": longitude + offset_lng,
            "similarity_score": similarity,
            "similarity_percentage": round(similarity * 100, 2),
            "risk_level": risk_level,
            "years_difference": years,
            "year1": 2020 - years,
            "year2": 2020,
            "parking_space_id": f"parking_{i}",
            "status": "ABANDONED_SUSPECTED",
            "is_abandoned": True,
            "bbox": {
                "x": random.randint(100, 800),
                "y": random.randint(100, 600),
                "w": random.randint(50, 100),
                "h": random.randint(40, 80)
            }
        }

        vehicles.append(vehicle)

    return vehicles


def get_demo_analysis_result(latitude: float, longitude: float, address: str) -> Dict:
    """
    데모 분석 결과 생성

    Args:
        latitude: 위도
        longitude: 경도
        address: 주소

    Returns:
        분석 결과
    """
    # 랜덤하게 방치 차량 0-5대 생성
    vehicle_count = random.randint(0, 5)

    if vehicle_count == 0:
        return {
            "success": True,
            "mode": "demo",
            "status_message": "✅ 방치 차량이 발견되지 않았습니다 (데모 데이터)",
            "status_message_en": "No abandoned vehicles detected (Demo data)",
            "metadata": {
                "address": address,
                "latitude": latitude,
                "longitude": longitude,
                "mode": "demo"
            },
            "analysis": {
                "total_parking_spaces_detected": random.randint(10, 30),
                "spaces_analyzed": random.randint(8, 25),
                "abandoned_vehicles_found": 0,
                "detection_threshold": 0.90,
                "is_clean": True
            },
            "abandoned_vehicles": [],
            "results": []
        }

    vehicles = generate_mock_abandoned_vehicles(latitude, longitude, vehicle_count)

    return {
        "success": True,
        "mode": "demo",
        "status_message": f"🔵 {vehicle_count}대의 방치 차량 발견 (데모 데이터)",
        "status_message_en": f"{vehicle_count} abandoned vehicle(s) detected (Demo data)",
        "metadata": {
            "address": address,
            "latitude": latitude,
            "longitude": longitude,
            "mode": "demo"
        },
        "analysis": {
            "total_parking_spaces_detected": random.randint(15, 40),
            "spaces_analyzed": random.randint(10, 30),
            "abandoned_vehicles_found": vehicle_count,
            "detection_threshold": 0.90,
            "is_clean": False
        },
        "abandoned_vehicles": vehicles,
        "results": vehicles
    }


# 테스트
if __name__ == "__main__":
    print("=" * 60)
    print("데모 모드 테스트")
    print("=" * 60)

    # 테스트 1: 서울 강남구
    print("\n[테스트 1] 서울 강남구")
    coords = get_demo_coordinates("서울특별시", "강남구")
    print(f"  주소: {coords['address']}")
    print(f"  좌표: ({coords['latitude']}, {coords['longitude']})")
    print(f"  메시지: {coords['message']}")

    # 테스트 2: 제주시
    print("\n[테스트 2] 제주특별자치도 제주시")
    coords = get_demo_coordinates("제주특별자치도", "제주시")
    print(f"  주소: {coords['address']}")
    print(f"  좌표: ({coords['latitude']}, {coords['longitude']})")

    # 테스트 3: 방치 차량 생성
    print("\n[테스트 3] 방치 차량 생성")
    result = get_demo_analysis_result(37.5172, 127.0473, "서울특별시 강남구")
    print(f"  발견된 차량: {result['analysis']['abandoned_vehicles_found']}대")
    print(f"  상태: {result['status_message']}")

    if result['abandoned_vehicles']:
        print("\n  차량 목록:")
        for v in result['abandoned_vehicles']:
            print(f"    - {v['id']}: {v['similarity_percentage']}% ({v['risk_level']})")

    print("\n" + "=" * 60)
    print("✅ 데모 모드 정상 작동!")
    print("=" * 60)
