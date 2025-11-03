# 브라우저 SSH로 더미 데이터 배포하기

SSH 키 파일 없이 Lightsail 브라우저 SSH를 사용하여 더미 데이터를 배포하는 방법입니다.

## 배포 방법

### 1단계: Lightsail 브라우저 SSH 접속

1. **AWS Lightsail 콘솔 접속**
   - https://lightsail.aws.amazon.com/

2. **인스턴스 선택**
   - `satellite-backend` 클릭

3. **"Connect using SSH" 버튼 클릭**
   - 주황색 버튼, 화면 상단
   - 브라우저에서 터미널이 열립니다

---

### 2단계: 더미 데이터 생성 스크립트 작성

브라우저 SSH 터미널에서 다음 명령어를 **복사해서 붙여넣기** (전체 선택 후 한 번에):

```bash
cat > /home/ubuntu/satellite_vehicle_tracker/backend/seed_dummy_data.py << 'ENDPYTHON'
#!/usr/bin/env python3
"""
더미 데이터 생성 스크립트
36대 차량 데이터 자동 생성
"""
import sys
import random
from datetime import datetime
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database import get_db
from models_sqlalchemy import AbandonedVehicle

# 전국 주요 도시 좌표
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

RISK_LEVELS = [
    {"level": "CRITICAL", "weight": 3},
    {"level": "HIGH", "weight": 5},
    {"level": "MEDIUM", "weight": 4},
    {"level": "LOW", "weight": 2},
]

VEHICLE_TYPES = [
    {"type": "small-vehicle", "weight": 7},
    {"type": "large-vehicle", "weight": 2},
    {"type": "truck", "weight": 1},
]

def weighted_choice(choices):
    total = sum(c["weight"] for c in choices)
    r = random.uniform(0, total)
    upto = 0
    for choice in choices:
        if upto + choice["weight"] >= r:
            return choice
        upto += choice["weight"]
    return choices[-1]

def generate_similarity_by_risk(risk_level):
    if risk_level == "CRITICAL":
        return round(random.uniform(0.95, 0.99), 4)
    elif risk_level == "HIGH":
        return round(random.uniform(0.90, 0.949), 4)
    elif risk_level == "MEDIUM":
        return round(random.uniform(0.85, 0.899), 4)
    else:
        return round(random.uniform(0.75, 0.849), 4)

def generate_years_by_risk(risk_level):
    if risk_level == "CRITICAL":
        year1 = random.randint(2015, 2018)
        year2 = year1 + random.randint(3, 6)
    elif risk_level == "HIGH":
        year1 = random.randint(2017, 2020)
        year2 = year1 + random.randint(2, 4)
    elif risk_level == "MEDIUM":
        year1 = random.randint(2019, 2021)
        year2 = year1 + random.randint(1, 3)
    else:
        year1 = random.randint(2020, 2022)
        year2 = year1 + random.randint(1, 2)
    return year1, min(year2, 2024)

def generate_vehicle_description(vehicle_type, risk_level):
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
    else:
        brand = random.choice(brands_truck)
        models = ["포터", "봉고", "타우너"]
        model = random.choice(models)
        return f"{color} {brand} {model} (화물차)"

# 36대 생성
print("=" * 60)
print("더미 데이터 36대 생성 중...")
print("=" * 60)

db = next(get_db())
try:
    existing = db.query(AbandonedVehicle).count()
    print(f"\n기존 데이터: {existing}개")

    inserted = 0
    for i in range(36):
        risk_choice = weighted_choice(RISK_LEVELS)
        risk_level = risk_choice["level"]

        vehicle_choice = weighted_choice(VEHICLE_TYPES)
        vehicle_type = vehicle_choice["type"]

        location = random.choice(LOCATIONS)
        lat = location["lat"] + random.uniform(-0.01, 0.01)
        lng = location["lng"] + random.uniform(-0.01, 0.01)

        similarity = generate_similarity_by_risk(risk_level)
        year1, year2 = generate_years_by_risk(risk_level)
        years_diff = year2 - year1

        description = generate_vehicle_description(vehicle_type, risk_level)

        city_parts = location["city"].split()
        city = city_parts[0]
        district = city_parts[1] if len(city_parts) > 1 else ""

        vehicle_id = f"VH{datetime.now().strftime('%Y%m%d')}{i:04d}"

        bbox = {
            "x": random.randint(100, 800),
            "y": random.randint(100, 600),
            "w": random.randint(60, 120),
            "h": random.randint(40, 90)
        }

        metadata = {
            "year1": year1,
            "year2": year2,
            "description": description,
            "confidence": round(random.uniform(0.85, 0.98), 4),
        }

        vehicle = AbandonedVehicle(
            vehicle_id=vehicle_id,
            latitude=round(lat, 6),
            longitude=round(lng, 6),
            city=city,
            district=district,
            address=location["city"],
            vehicle_type=vehicle_type,
            similarity_score=similarity,
            similarity_percentage=similarity * 100,
            risk_level=risk_level,
            years_difference=years_diff,
            first_detected=datetime.now(),
            last_detected=datetime.now(),
            detection_count=random.randint(1, 5),
            avg_similarity=similarity,
            max_similarity=min(similarity + random.uniform(0, 0.05), 1.0),
            status="DETECTED",
            bbox_data=bbox,
            extra_metadata=metadata,
        )
        db.add(vehicle)
        inserted += 1

    db.commit()
    total = db.query(AbandonedVehicle).count()

    print(f"\n✅ {inserted}대 추가 완료!")
    print(f"✅ 총 데이터: {total}개")

    # 통계
    print("\n[위험도별 분포]")
    for risk in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = db.query(AbandonedVehicle).filter(AbandonedVehicle.risk_level == risk).count()
        pct = (count / total) * 100 if total > 0 else 0
        print(f"  {risk}: {count}대 ({pct:.1f}%)")

    print("\n" + "=" * 60)
    print("✅ 배포 완료!")
    print("=" * 60)

except Exception as e:
    db.rollback()
    print(f"\n❌ 에러: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
ENDPYTHON

echo "✅ 스크립트 생성 완료!"
```

---

### 3단계: 스크립트 실행

```bash
cd /home/ubuntu/satellite_vehicle_tracker/backend
source venv/bin/activate
python seed_dummy_data.py
```

**예상 출력:**
```
============================================================
더미 데이터 36대 생성 중...
============================================================

기존 데이터: 13개

✅ 36대 추가 완료!
✅ 총 데이터: 49개

[위험도별 분포]
  CRITICAL: 7대 (14.3%)
  HIGH: 25대 (51.0%)
  MEDIUM: 11대 (22.4%)
  LOW: 6대 (12.2%)

============================================================
✅ 배포 완료!
============================================================
```

---

### 4단계: 서비스 재시작

```bash
sudo supervisorctl restart satellite-backend
```

**예상 출력:**
```
satellite-backend: stopped
satellite-backend: started
```

---

### 5단계: 배포 확인

#### A. API 응답 확인

```bash
curl http://localhost:8000/api/abandoned-vehicles | python3 -c "import sys, json; print(f'{len(json.load(sys.stdin))}대')"
```

**예상 출력:** `49대`

#### B. Cloudflare Tunnel 확인 (로컬 브라우저에서)

```
https://standings-classification-easy-textbook.trycloudflare.com/api/abandoned-vehicles
```

브라우저에서 JSON 응답 확인 (49개 차량 데이터)

#### C. GitHub Pages 확인

```
https://wannahappyaroundme.github.io/satellite_vehicle_tracker/
```

- ✅ 지도에 49개 마커 표시
- ✅ 통계 대시보드 확인
- ✅ 관리자 대시보드에서 차량 리스트 확인

---

## 문제 해결

### 에러: ModuleNotFoundError

```bash
# 가상환경 활성화 확인
source venv/bin/activate

# 패키지 재설치
pip install -r requirements.txt
```

### 에러: database is locked

```bash
# 서비스 중지
sudo supervisorctl stop satellite-backend

# 스크립트 실행
python seed_dummy_data.py

# 서비스 재시작
sudo supervisorctl start satellite-backend
```

### 서비스가 시작되지 않음

```bash
# 에러 로그 확인
sudo tail -50 /var/log/satellite-backend.err.log

# 수동 실행 테스트
cd /home/ubuntu/satellite_vehicle_tracker/backend
source venv/bin/activate
python fastapi_app.py
```

---

## 추가 명령어

### 데이터 개수만 빠르게 확인

```bash
cd /home/ubuntu/satellite_vehicle_tracker/backend
source venv/bin/activate
python3 << EOF
from database import get_db
from models_sqlalchemy import AbandonedVehicle
db = next(get_db())
print(f"총 {db.query(AbandonedVehicle).count()}대")
db.close()
EOF
```

### 최신 5개 차량 확인

```bash
curl -s http://localhost:8000/api/abandoned-vehicles | python3 -c "
import sys, json
data = json.load(sys.stdin)
for i, v in enumerate(data[:5], 1):
    print(f\"{i}. {v['vehicle_id']} - {v['risk_level']} - {v['address']}\")
"
```

---

## 완료! 🎉

이제 다음에서 49개의 차량 데이터를 확인할 수 있습니다:

1. **API 응답:**
   - https://standings-classification-easy-textbook.trycloudflare.com/api/abandoned-vehicles

2. **GitHub Pages:**
   - https://wannahappyaroundme.github.io/satellite_vehicle_tracker/

3. **통계 대시보드:**
   - 위험도별, 지역별, 타입별 차트 확인

---

**Made with ❤️ for safer and better cities**
