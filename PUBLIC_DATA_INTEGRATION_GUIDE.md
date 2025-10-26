# 🏛️ 공공데이터 기반 CCTV 통합 시스템 가이드

## 📊 실제 공공데이터 소스 완전 정리

### 1. 전국 CCTV 표준데이터 (무료) ⭐ 핵심
**제공기관**: 행정안전부, 개인정보보호위원회
**데이터 규모**: 전국 수만 개 CCTV
**URL**: https://www.data.go.kr/data/15013094/standard.do

#### 📥 다운로드 방법:
1. 공공데이터포털 접속 (로그인 불필요)
2. EXCEL 버튼(초록색) 클릭
3. CSV/XLSX 파일 즉시 다운로드

#### 📋 제공 데이터 항목:
```
- 관리기관명
- 설치위치 (도로명주소, 지번주소)
- 설치목적 (교통정보수집, 방범, 시설물관리 등)
- 카메라대수
- 촬영방향
- 위도 (WGS84)
- 경도 (WGS84)
- 설치년월
- 관리기관전화번호
```

#### ✅ 특징:
- **완전 무료** - 로그인/API 키 불필요
- **정기 업데이트** - 월 1회 이상
- **전국 커버리지** - 17개 광역시도 전체
- **고품질 좌표** - WGS84 좌표계 (GPS 호환)

---

### 2. 국토교통부 ITS CCTV 화상자료 (무료) ⭐ 실시간 영상
**제공기관**: 국토교통부 국가교통정보센터
**데이터 규모**: 고속도로 + 주요 간선도로 약 10,000개
**URL**: https://www.data.go.kr/data/15040466/openapi.do

#### 🔑 API 키 발급 방법:
1. 공공데이터포털 회원가입 (무료)
2. 해당 API 페이지 → "활용신청" 버튼
3. 즉시 승인 또는 1~2일 내 승인
4. 인증키 발급 완료

#### 📡 제공 API:
```bash
# CCTV 목록 조회
GET http://openapi.its.go.kr:8081/api/NCCTVInfo
Parameters:
  - key: API 인증키
  - type: xml/json
  - cctvType: 1(고속도로), 2(국도)
  - minX, maxX, minY, maxY: 검색 영역 좌표

# CCTV 영상 URL 조회
GET http://openapi.its.go.kr:8081/api/GetCCTVInfo
Parameters:
  - key: API 인증키
  - cctvid: CCTV ID
  - type: xml/json
```

#### 🎥 실시간 영상 제공 형식:
- **JPEG 정지화상** - 5초마다 갱신
- **URL 직접 접근 가능** - 웹/앱에서 바로 표시
- **예시 URL**: `http://cctv1.its.go.kr/its/CCTV001.jpg`

#### ✅ 특징:
- **완전 무료** - 비상업적 이용 무료
- **실시간 영상** - 5초 간격 자동 갱신
- **고속도로 특화** - 고속도로 교통 CCTV 집중
- **높은 가용성** - 99% 이상 정상 동작

---

### 3. 서울시 CCTV 설치 현황 (무료)
**제공기관**: 서울특별시
**데이터 규모**: 서울시 전체 약 80,000개
**URL**: https://data.seoul.go.kr/dataList/OA-2734/F/1/datasetView.do

#### 📥 다운로드 방법:
1. 서울 열린데이터광장 접속 (로그인 불필요)
2. CSV 파일 다운로드 또는 Open API 이용

#### 📋 제공 데이터:
```
- 자치구명
- CCTV 설치 목적 (방범, 교통, 시설물관리 등)
- 설치 위치 (동/도로명)
- 카메라 대수
- 위도/경도
- 관리기관
```

#### 🔑 Open API 이용 (무료):
```bash
GET http://openapi.seoul.go.kr:8088/{인증키}/json/CCTV/{시작번호}/{끝번호}

예시:
http://openapi.seoul.go.kr:8088/sample/json/CCTV/1/100
```

**API 키 발급**: https://data.seoul.go.kr (무료, 즉시 발급)

---

### 4. 지자체별 CCTV 데이터 (무료)

#### 부산광역시
- **URL**: https://data.busan.go.kr
- **데이터**: 부산시 CCTV 설치 현황
- **API**: Open API 제공 (무료)

#### 경기도
- **URL**: https://data.gg.go.kr
- **데이터**: 경기도 CCTV 현황 (제공표준)
- **다운로드**: CSV/JSON

#### 인천광역시
- **URL**: https://data.incheon.go.kr
- **데이터**: 인천시 CCTV 설치 현황

#### 대전광역시
- **URL**: https://www.data.go.kr
- **검색어**: "대전 CCTV"

#### 제주특별자치도
- **URL**: https://www.data.go.kr
- **검색어**: "제주 CCTV"

---

## 🎯 데이터 통합 전략

### Phase 1: 기본 CCTV 위치 데이터 (수만 개)
**소스**: 전국CCTV표준데이터 (행정안전부)
**구현**:
1. CSV 파일 다운로드
2. PostgreSQL/SQLite에 import
3. 위경도 기반 spatial index 생성
4. REST API로 주변 CCTV 검색 제공

### Phase 2: 실시간 영상 통합 (교통 CCTV)
**소스**: 국토교통부 ITS API
**구현**:
1. ITS API 키 발급
2. CCTV ID → 영상 URL 매핑
3. 5초 간격 JPEG 이미지 스트리밍
4. 프론트엔드에서 자동 갱신

### Phase 3: 지역별 상세 데이터
**소스**: 서울/부산/경기 등 지자체 API
**구현**:
1. 각 지자체 API 키 발급
2. 일 1회 데이터 동기화 (cron job)
3. 중복 제거 및 병합

---

## 💻 실제 구현 코드 예시

### 1. 전국 CCTV CSV 데이터 로드
```python
import pandas as pd
import sqlite3

# CSV 다운로드 후 로드
df = pd.read_csv('전국CCTV표준데이터.csv', encoding='utf-8')

# 필요한 컬럼만 선택
df_clean = df[[
    '관리기관명', '설치위치', '설치목적',
    '카메라대수', '위도', '경도'
]].dropna(subset=['위도', '경도'])

# SQLite에 저장
conn = sqlite3.connect('cctv_database.db')
df_clean.to_sql('cctv_locations', conn, if_exists='replace', index=False)

print(f"Total CCTV loaded: {len(df_clean)}")
```

### 2. 국토교통부 ITS API 호출
```python
import requests

ITS_API_KEY = "YOUR_API_KEY_HERE"
ITS_BASE_URL = "http://openapi.its.go.kr:8081/api"

def get_nearby_its_cctv(min_x, max_x, min_y, max_y):
    """국토교통부 교통 CCTV 검색"""
    url = f"{ITS_BASE_URL}/NCCTVInfo"
    params = {
        'key': ITS_API_KEY,
        'type': 'json',
        'cctvType': '1',  # 고속도로
        'minX': min_x,
        'maxX': max_x,
        'minY': min_y,
        'maxY': max_y
    }

    response = requests.get(url, params=params)
    return response.json()

def get_cctv_image_url(cctv_id):
    """CCTV 실시간 영상 URL 가져오기"""
    url = f"{ITS_BASE_URL}/GetCCTVInfo"
    params = {
        'key': ITS_API_KEY,
        'cctvid': cctv_id,
        'type': 'json'
    }

    response = requests.get(url, params=params)
    data = response.json()
    return data.get('imageUrl')  # JPEG URL
```

### 3. 서울시 Open API 호출
```python
SEOUL_API_KEY = "YOUR_SEOUL_API_KEY"
SEOUL_BASE_URL = "http://openapi.seoul.go.kr:8088"

def get_seoul_cctv(start=1, end=1000):
    """서울시 CCTV 정보 조회"""
    url = f"{SEOUL_BASE_URL}/{SEOUL_API_KEY}/json/CCTV/{start}/{end}"

    response = requests.get(url)
    data = response.json()

    if 'CCTV' in data:
        return data['CCTV']['row']
    return []
```

---

## 🤖 머신러닝 통합 (YOLO/ResNet)

### 실시간 CCTV 영상에서 방치 차량 감지

```python
from ultralytics import YOLO
import cv2
import requests
from io import BytesIO

# YOLO 모델 로드
model = YOLO('yolov8x.pt')

def detect_vehicles_from_cctv(image_url):
    """CCTV 영상에서 차량 감지"""

    # ITS CCTV 이미지 다운로드
    response = requests.get(image_url)
    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # YOLO 차량 감지
    results = model(frame, classes=[2, 5, 7])  # car, bus, truck

    # 결과 파싱
    detected_vehicles = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            conf = box.conf[0]
            cls = box.cls[0]

            detected_vehicles.append({
                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                'confidence': float(conf),
                'class': int(cls)
            })

    return detected_vehicles

def track_abandoned_vehicles(cctv_id, check_interval=300):
    """5분 간격으로 CCTV 모니터링하여 방치 차량 추적"""

    previous_vehicles = []
    abandoned_threshold = 3600  # 1시간 동안 움직이지 않으면 방치

    while True:
        # CCTV 영상 URL 가져오기
        image_url = get_cctv_image_url(cctv_id)

        # 차량 감지
        current_vehicles = detect_vehicles_from_cctv(image_url)

        # 이전 프레임과 비교하여 움직이지 않은 차량 식별
        # (IoU 기반 매칭 + 시간 추적)

        time.sleep(check_interval)
```

---

## 🔍 CCTV 가용성 체크 시스템

```python
import asyncio
import aiohttp
from datetime import datetime

async def check_cctv_availability(cctv_id, image_url):
    """CCTV 가용성 비동기 체크"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url, timeout=5) as response:
                if response.status == 200:
                    content = await response.read()
                    if len(content) > 1000:  # 유효한 이미지인지 확인
                        return {
                            'cctv_id': cctv_id,
                            'status': 'online',
                            'checked_at': datetime.now(),
                            'image_size': len(content)
                        }

        return {
            'cctv_id': cctv_id,
            'status': 'offline',
            'checked_at': datetime.now()
        }

    except Exception as e:
        return {
            'cctv_id': cctv_id,
            'status': 'error',
            'error': str(e),
            'checked_at': datetime.now()
        }

async def monitor_all_cctvs(cctv_list):
    """전체 CCTV 가용성 모니터링"""
    tasks = [
        check_cctv_availability(cctv['id'], cctv['image_url'])
        for cctv in cctv_list
    ]

    results = await asyncio.gather(*tasks)

    # 통계 계산
    online = sum(1 for r in results if r['status'] == 'online')
    offline = sum(1 for r in results if r['status'] == 'offline')

    print(f"Online: {online}/{len(results)} ({online/len(results)*100:.1f}%)")
    print(f"Offline: {offline}/{len(results)}")

    return results
```

---

## 📦 데이터베이스 스키마 (PostgreSQL + PostGIS)

```sql
CREATE EXTENSION postgis;

-- CCTV 마스터 테이블
CREATE TABLE cctv_locations (
    id SERIAL PRIMARY KEY,
    cctv_id VARCHAR(100) UNIQUE,
    name VARCHAR(200),
    location GEOGRAPHY(POINT, 4326),  -- WGS84 좌표
    address TEXT,
    purpose VARCHAR(50),  -- 교통, 방범, 주차 등
    management_agency VARCHAR(200),
    camera_count INTEGER,
    installation_date DATE,
    has_realtime_stream BOOLEAN DEFAULT FALSE,
    stream_url TEXT,
    is_available BOOLEAN DEFAULT TRUE,
    last_checked TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Spatial Index 생성 (고속 검색)
CREATE INDEX idx_cctv_location ON cctv_locations USING GIST(location);

-- 방치 차량 감지 로그
CREATE TABLE abandoned_vehicle_detections (
    id SERIAL PRIMARY KEY,
    cctv_id VARCHAR(100) REFERENCES cctv_locations(cctv_id),
    detected_at TIMESTAMP,
    bbox JSONB,  -- {x, y, w, h}
    confidence FLOAT,
    vehicle_class VARCHAR(50),
    is_abandoned BOOLEAN,
    abandoned_duration INTEGER,  -- 초 단위
    alert_sent BOOLEAN DEFAULT FALSE
);

-- 주변 CCTV 검색 함수
CREATE OR REPLACE FUNCTION find_nearby_cctvs(
    lat FLOAT,
    lon FLOAT,
    radius_meters INTEGER DEFAULT 1000
)
RETURNS TABLE (
    cctv_id VARCHAR,
    name VARCHAR,
    distance_meters FLOAT,
    latitude FLOAT,
    longitude FLOAT,
    purpose VARCHAR,
    has_stream BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.cctv_id,
        c.name,
        ST_Distance(
            c.location,
            ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography
        ) as distance_meters,
        ST_Y(c.location::geometry) as latitude,
        ST_X(c.location::geometry) as longitude,
        c.purpose,
        c.has_realtime_stream
    FROM cctv_locations c
    WHERE ST_DWithin(
        c.location,
        ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography,
        radius_meters
    )
    AND c.is_available = TRUE
    ORDER BY distance_meters;
END;
$$ LANGUAGE plpgsql;
```

---

## 🚀 구현 로드맵

### Week 1: 데이터 수집 및 저장
- [ ] 전국CCTV표준데이터 CSV 다운로드
- [ ] PostgreSQL + PostGIS 설정
- [ ] CSV 데이터 import 스크립트 작성
- [ ] Spatial index 생성

### Week 2: API 통합
- [ ] 국토교통부 ITS API 키 발급
- [ ] ITS API 연동 코드 작성
- [ ] 서울시 Open API 키 발급
- [ ] 서울시 API 연동

### Week 3: 실시간 스트리밍
- [ ] CCTV 영상 URL 매핑 테이블 구축
- [ ] 5초 간격 이미지 갱신 구현
- [ ] 프론트엔드 실시간 뷰어 구현

### Week 4: 머신러닝 통합
- [ ] YOLO 모델 차량 감지 파이프라인
- [ ] 방치 차량 추적 알고리즘
- [ ] 알림 시스템 구축

### Week 5: 가용성 모니터링
- [ ] 비동기 가용성 체크 시스템
- [ ] 대시보드 구축
- [ ] 자동 복구 로직

---

## 💰 비용 정리

| 항목 | 제공기관 | 비용 | API 키 필요 |
|------|---------|------|------------|
| 전국 CCTV 표준데이터 | 행정안전부 | **무료** | ❌ 불필요 |
| ITS 교통 CCTV 실시간 영상 | 국토교통부 | **무료** | ✅ 필요 (즉시 발급) |
| 서울시 CCTV 데이터 | 서울특별시 | **무료** | ✅ 필요 (즉시 발급) |
| 지자체 CCTV 데이터 | 각 지자체 | **무료** | ⚠️ 일부 필요 |

**총 비용: 0원** (모두 무료)

---

## 📞 문의처

### 공공데이터포털
- 웹사이트: https://www.data.go.kr
- 고객센터: 1600-5666

### 국토교통부 ITS
- 웹사이트: https://www.its.go.kr
- 문의: ITS 고객센터

### 서울 열린데이터광장
- 웹사이트: https://data.seoul.go.kr
- 문의: data@seoul.go.kr
