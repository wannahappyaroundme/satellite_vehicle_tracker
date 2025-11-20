# 🏗️ 기술 스택 및 아키텍처

## 📊 시스템 개요

**장기 방치 차량 탐지 시스템**은 위성 항공사진을 AI로 분석하여 1년 이상 같은 위치에 방치된 차량을 자동 탐지하는 풀스택 웹 애플리케이션입니다.

---

## 🎯 핵심 기술 스택

### Frontend

- **React 18** - 사용자 인터페이스
- **TypeScript** - 타입 안전성
- **Leaflet** - 지도 시각화 (OpenStreetMap 기반)
- **Recharts** - 통계 차트
- **Axios** - HTTP 클라이언트
- **React Hooks** - 상태 관리 (useState, useEffect)

### Backend

- **FastAPI** - 고성능 Python 웹 프레임워크
- **Python 3.11** - 메인 백엔드 언어
- **SQLAlchemy** - ORM (Object-Relational Mapping)
- **SQLite** - 관계형 데이터베이스 (파일 기반)
- **Uvicorn** - ASGI 서버

### AI/ML

- **PyTorch** - 딥러닝 프레임워크
- **MobileNetV2** - 경량 특징 추출 (1280차원, 14MB)
- **YOLOv8** - 실시간 객체 탐지 (차량 탐지)
- **코사인 유사도** - 차량 이동 여부 판단
- **DBSCAN** - 클러스터링 (차량 밀집 지역 탐지)

### Infrastructure

- **AWS Lightsail** - 클라우드 호스팅 ($5/월, 1GB RAM)
- **Cloudflare Tunnel** - 무료 HTTPS (systemd 서비스)
- **GitHub Pages** - 정적 사이트 호스팅 (무료)
- **GitHub Actions** - CI/CD 파이프라인
- **Supervisor** - 프로세스 관리 (자동 재시작)
- **Nginx** - 리버스 프록시 (포트 80 → 8000)

### APIs

- **VWorld WMTS API** - 12cm 고해상도 항공사진 (5-10배 고속)
- **VWorld POI Search API** - 장소 검색
- **VWorld 2D/Hybrid Map API** - 지도 타일

---

## 🏛️ 아키텍처 구조

### 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    사용자 브라우저                             │
│            (https://wannahappyaroundme.github.io)            │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   GitHub Pages (무료)                         │
│                React + TypeScript 정적 빌드                   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS API 요청
                         ↓
┌─────────────────────────────────────────────────────────────┐
│           Cloudflare Tunnel (무료 HTTPS)                     │
│   https://standings-classification-easy-textbook            │
│              .trycloudflare.com                              │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP (localhost)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              AWS Lightsail ($5/월)                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           Nginx (리버스 프록시)                         │  │
│  │              Port 80 → 8000                           │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         ↓                                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │      Supervisor (프로세스 관리)                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │        FastAPI Server (Port 8000)               │  │  │
│  │  │     - Uvicorn ASGI 서버                         │  │  │
│  │  │     - 36+ API 엔드포인트                        │  │  │
│  │  │     - CORS 설정                                 │  │  │
│  │  └────────────────┬────────────────────────────────┘  │  │
│  └───────────────────┼────────────────────────────────────┘  │
│                      ↓                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            AI/ML 서비스                                │  │
│  │  - AbandonedVehicleDetector (MobileNetV2)           │  │
│  │  - VehicleDetector (YOLOv8)                         │  │
│  │  - StorageAnalyzer (DBSCAN)                         │  │
│  └───────────────────┬───────────────────────────────────┘  │
│                      ↓                                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         SQLite Database (파일 기반)                    │  │
│  │     satellite_tracker.db (40GB SSD)                  │  │
│  │  - abandoned_vehicles 테이블                         │  │
│  │  - analysis_logs 테이블                              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         ↕
                    VWorld API
            (항공사진, 지도, POI 검색)
```

---

## 🔄 데이터 흐름

### 방치 차량 탐지 프로세스

```
1. 사용자 입력
   ↓
2. React Frontend
   - 좌표 선택
   - 필터 설정 (위험도, 타입)
   ↓
3. Cloudflare Tunnel (HTTPS)
   ↓
4. FastAPI Backend
   - API 엔드포인트: /api/abandoned-vehicles
   ↓
5. SQLite Database
   - SQLAlchemy ORM 쿼리
   - 필터링 (risk_level, vehicle_type, city)
   ↓
6. AI 분석 (필요 시)
   - MobileNetV2 특징 추출
   - 코사인 유사도 계산
   - 위험도 분류
   ↓
7. JSON 응답
   ↓
8. Cloudflare Tunnel
   ↓
9. React Frontend
   - Leaflet 지도에 마커 표시
   - 통계 차트 렌더링
   - 차량 리스트 테이블
```

---

## 💾 데이터베이스 스키마

### AbandonedVehicle 테이블

```sql
CREATE TABLE abandoned_vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id VARCHAR(100) UNIQUE NOT NULL,

    -- 위치 정보
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    city VARCHAR(50),
    district VARCHAR(50),
    address VARCHAR(200),

    -- 차량 정보
    vehicle_type VARCHAR(50),  -- small-vehicle, large-vehicle, truck

    -- 탐지 정보
    similarity_score FLOAT,           -- 0.0-1.0
    similarity_percentage FLOAT,      -- 0-100
    risk_level VARCHAR(20),           -- CRITICAL, HIGH, MEDIUM, LOW
    years_difference INTEGER,         -- 경과 년수

    -- 이력 정보
    first_detected DATETIME NOT NULL,
    last_detected DATETIME NOT NULL,
    detection_count INTEGER DEFAULT 1,
    avg_similarity FLOAT,
    max_similarity FLOAT,

    -- 관리 상태
    status VARCHAR(20) DEFAULT 'DETECTED',  -- DETECTED, INVESTIGATING, VERIFIED, RESOLVED
    verification_notes TEXT,

    -- 메타데이터
    bbox_data JSON,          -- Bounding box
    extra_metadata JSON,     -- 연도, 설명, 신뢰도 등

    -- 타임스탬프
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- 인덱스
    INDEX idx_location (latitude, longitude),
    INDEX idx_city_district (city, district),
    INDEX idx_status_risk (status, risk_level),
    INDEX idx_vehicle_id (vehicle_id)
);
```

---

## 🧠 AI 모델 상세

### 1. MobileNetV2 (특징 추출)

**용도:** 차량 이미지에서 특징 벡터 추출

**스펙:**

- **입력:** 224×224 RGB 이미지
- **출력:** 1280차원 특징 벡터
- **모델 크기:** 14MB (경량)
- **사전 학습:** ImageNet
- **추론 속도:** ~50ms/이미지 (CPU)

**코드:**

```python
from torchvision import models
import torch.nn as nn

model = models.mobilenet_v2(pretrained=True)
model.classifier = nn.Identity()  # 분류 레이어 제거
model.eval()

# 특징 추출
features = model(image_tensor)  # [1, 1280]
```

### 2. YOLOv8 (객체 탐지)

**용도:** 위성 항공사진에서 차량 탐지

**스펙:**

- **모델:** YOLOv8n (nano)
- **입력:** 640×640 이미지
- **클래스:** small-vehicle, large-vehicle, truck
- **정확도:** mAP50 ~0.85
- **추론 속도:** ~30ms/이미지 (GPU)

### 3. 코사인 유사도 (차량 매칭)

**용도:** 시간대별 차량 이미지 비교

**알고리즘:**

```python
from sklearn.metrics.pairwise import cosine_similarity

similarity = cosine_similarity(
    features_year1.reshape(1, -1),
    features_year2.reshape(1, -1)
)[0][0]

# 임계값
if similarity >= 0.90:
    status = "ABANDONED"  # 90% 이상 유사 = 방치 차량
```

**위험도 분류:**

- **CRITICAL:** similarity ≥ 95% AND years ≥ 3
- **HIGH:** similarity ≥ 90% AND years ≥ 2
- **MEDIUM:** similarity ≥ 85%
- **LOW:** similarity < 85%

---

## 🚀 배포 파이프라인

### CI/CD 흐름 (GitHub Actions)

```
1. 개발자가 main 브랜치에 push
   ↓
2. GitHub Actions 트리거
   - Workflow: .github/workflows/gh-pages.yml
   ↓
3. Node.js 18 환경 설정
   ↓
4. 의존성 설치
   - npm install (frontend)
   ↓
5. 환경 변수 주입
   - REACT_APP_API_URL
   - REACT_APP_FASTAPI_URL
   ↓
6. 프로덕션 빌드
   - npm run build
   - CRA (Create React App) 빌드
   ↓
7. GitHub Pages에 배포
   - actions/deploy-pages@v4
   - 배포 URL: wannahappyaroundme.github.io
   ↓
8. 배포 완료 (2-3분)
```

### Lightsail 배포

```bash
# 1. 프로젝트 클론
git clone https://github.com/wannahappyaroundme/satellite_vehicle_tracker.git

# 2. 가상환경 생성
python3.11 -m venv venv
source venv/bin/activate

# 3. 의존성 설치
pip install -r backend/requirements.txt

# 4. Supervisor 설정
sudo tee /etc/supervisor/conf.d/satellite-backend.conf
# [program:satellite-backend]
# command=/home/ubuntu/satellite_vehicle_tracker/backend/venv/bin/uvicorn
# directory=/home/ubuntu/satellite_vehicle_tracker/backend
# user=ubuntu
# autostart=true
# autorestart=true

# 5. Nginx 리버스 프록시 설정
sudo tee /etc/nginx/sites-available/satellite-backend
# location / { proxy_pass http://127.0.0.1:8000; }

# 6. 서비스 시작
sudo supervisorctl reread
sudo supervisorctl update
sudo systemctl restart nginx
```

---

## 🔒 보안 및 성능

### CORS 설정

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 캐싱 전략

- **VWorld API 응답:** 24시간 캐싱 (Redis 또는 메모리)
- **정적 자산:** GitHub Pages CDN 캐싱
- **API 응답:** 브라우저 캐시 헤더 설정

### Rate Limiting

```python
from security import rate_limiter

@app.get("/api/abandoned-vehicles")
@rate_limiter(calls=100, period=60)  # 100 calls/min
async def get_vehicles():
    ...
```

---

## 📈 확장 계획

### 단기 (1-3개월)

- AWS RDS PostgreSQL 마이그레이션 (SQLite → PostgreSQL)
- Redis 캐싱 레이어 추가
- WebSocket 실시간 업데이트

### 중기 (3-6개월)

- Kubernetes 배포 (Auto-scaling)
- Elasticsearch 전문 검색
- S3 이미지 저장소

### 장기 (6-12개월)

- 커스텀 YOLOv8 모델 학습 (한국 차량 특화)
- 모바일 앱 (React Native)
- 관리자 대시보드 고도화

---

## 💰 비용 구조

| 항목                  | 서비스            | 비용      |
| --------------------- | ----------------- | --------- |
| **백엔드 호스팅**     | AWS Lightsail     | $5/월     |
| **HTTPS**             | Cloudflare Tunnel | $0 (무료) |
| **프론트엔드 호스팅** | GitHub Pages      | $0 (무료) |
| **CI/CD**             | GitHub Actions    | $0 (무료) |
| **도메인**            | Cloudflare        | $0 (무료) |
| **데이터베이스**      | SQLite (로컬)     | $0 (무료) |
| **총 비용**           |                   | **$5/월** |

---

## 🛠️ 개발 환경

### 로컬 개발

```bash
# Backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn fastapi_app:app --reload --port 8000

# Frontend
cd frontend
npm install
npm start  # Port 3000
```

### 환경 변수

**Frontend (.env.development):**

```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_FASTAPI_URL=http://localhost:8000/api
```

**Frontend (.env.production):**

```
REACT_APP_API_URL=https://standings-classification-easy-textbook.trycloudflare.com/api
REACT_APP_FASTAPI_URL=https://standings-classification-easy-textbook.trycloudflare.com/api
```

---

## 📚 참고 자료

- **FastAPI 문서:** https://fastapi.tiangolo.com/
- **React 문서:** https://react.dev/
- **Leaflet 문서:** https://leafletjs.com/
- **PyTorch 문서:** https://pytorch.org/
- **YOLOv8 문서:** https://docs.ultralytics.com/
- **AWS Lightsail:** https://lightsail.aws.amazon.com/
- **Cloudflare Tunnel:** https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/

---

**Made with ❤️ for safer and better cities**

**The best for a better world**
