# 장기 방치 차량 탐지 시스템
# Abandoned Vehicle Detection System

국토정보플랫폼의 무료 항공사진을 이용한 1년 이상 장기 방치 차량 탐지 시스템

## 🎯 프로젝트 개요

**핵심 목적:** 연도별 항공사진 비교를 통해 1년 이상 같은 위치에 방치된 차량을 자동으로 탐지하고, CCTV를 통해 검증할 수 있는 Full-Stack 시스템

**데이터 출처:** 국토지리정보원(NGII) 항공사진 (국토정보플랫폼 무료 제공)

## 🔬 핵심 기술

### 1. 데이터 처리 (Data Processing)
- **입력 형식:** GeoTIFF 항공사진 또는 PDF
- **비교 단위:** 연(年) 단위 (예: 2015년 vs 2020년)
- **처리 라이브러리:** rasterio, pdf2image, OpenCV

### 2. AI/ML 알고리즘
```
항공사진 (Year 1) → PDF/GeoTIFF 파싱 → 이미지 정렬
                                           ↓
                                    주차 공간 탐지 (GeoJSON 또는 자동)
                                           ↓
                                    ResNet50 특징 추출
                                           ↓
                                    2048차원 특징 벡터

항공사진 (Year 2) → PDF/GeoTIFF 파싱 → 이미지 정렬
                                           ↓
                                    주차 공간 탐지
                                           ↓
                                    ResNet50 특징 추출
                                           ↓
                                    2048차원 특징 벡터

        특징 벡터 1 + 특징 벡터 2 → 코사인 유사도 계산
                                           ↓
                                  유사도 >= 90% ?
                                           ↓
                                        방치 의심!
```

**핵심 로직:**
1. **GeoTIFF 크로핑:** rasterio로 주차 공간(GeoJSON 좌표)에 해당하는 이미지를 추출
2. **특징 추출:** ResNet50 (ImageNet pretrained)로 차량 이미지를 2048차원 특징 벡터로 변환
3. **유사도 계산:** 두 연도의 특징 벡터 간 코사인 유사도 측정
4. **판정:** 90% 이상 유사 → 같은 차량이 그대로 있음 → **방치 의심**

### 3. 시스템 구조

**Backend (FastAPI + Python)**
- ResNet50 기반 특징 추출 엔진
- 코사인 유사도 계산
- RESTful API 제공
- CCTV 위치 정보 관리

**Frontend (React + TypeScript)**
- Leaflet.js 기반 지도 인터페이스
- 방치 의심 차량 빨간색 표시
- CCTV 실시간 검증 팝업
- 연도별 비교 시각화

**검증 (Verification)**
- 관리자가 방치 의심 구역 클릭
- 사전 매핑된 공개 CCTV 영상 팝업
- 실시간 현장 상태 확인

## 📦 설치 및 실행

### 필수 요구사항
- Python 3.8+ (3.11 권장)
- Node.js 18+
- Poppler (PDF 변환용)
- GDAL (GeoTIFF 처리용)

### 1. 시스템 라이브러리 설치

**macOS:**
```bash
brew install poppler gdal
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install poppler-utils gdal-bin libgdal-dev
```

### 2. 프로젝트 설치

```bash
# 저장소 클론
git clone <repository-url>
cd satellite_project

# 의존성 설치
npm run install:all

# 또는 개별 설치
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### 3. 서버 실행

**방법 1: 자동 실행 (권장)**
```bash
npm run dev
```

**방법 2: 수동 실행**

터미널 1 - FastAPI 백엔드:
```bash
cd backend
python fastapi_app.py
```

터미널 2 - Flask 백엔드 (선택사항, 레거시 기능용):
```bash
cd backend
python app.py
```

터미널 3 - 프론트엔드:
```bash
cd frontend
npm start
```

### 4. 접속
- **프론트엔드:** http://localhost:3000
- **FastAPI 백엔드:** http://localhost:8000
- **FastAPI 문서:** http://localhost:8000/docs
- **Flask 백엔드:** http://localhost:5000

## 🚀 샘플 데이터로 테스트

프로젝트에는 제주시 일도이동 지역의 샘플 항공사진이 포함되어 있습니다:

- **sample_image1.pdf:** 2015년 4월 17일 촬영
- **sample_image2.pdf:** 2020년 4월 29일 촬영 (5년 후)

### 방법 1: 웹 UI 사용 (가장 쉬움)

1. 프론트엔드 접속: http://localhost:3000
2. "방치 차량 탐지 (New!)" 탭 클릭
3. "샘플 이미지 분석 시작" 버튼 클릭
4. 결과 확인:
   - 방치 의심 차량 빨간색 카드로 표시
   - 위험도 레벨 (CRITICAL/HIGH/MEDIUM/LOW)
   - 유사도 퍼센트
   - CCTV 검증 버튼

### 방법 2: 테스트 스크립트 사용

```bash
python test_abandoned_detection.py
```

**출력 파일:**
- `comparison_result.jpg` - 연도별 비교 시각화 (방치 차량 빨간 박스)
- `detection_results.json` - 탐지 결과 JSON

### 방법 3: API 직접 호출

```bash
# 샘플 이미지 비교
curl -X POST http://localhost:8000/api/compare-samples | jq

# CCTV 위치 조회
curl http://localhost:8000/api/cctv-locations | jq
```

## 📊 API 엔드포인트

### 방치 차량 탐지 API (FastAPI - Port 8000)

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/compare-samples` | 샘플 이미지 비교 (2015 vs 2020) |
| POST | `/api/upload-aerial-photos` | 커스텀 항공사진 업로드 및 비교 |
| GET | `/api/abandoned-vehicles` | 방치 차량 목록 조회 (필터링) |
| GET | `/api/cctv-locations` | 검증용 CCTV 위치 조회 |
| GET | `/api/cctv/{id}/stream` | CCTV 스트림 URL 조회 |
| GET | `/api/visualization/{filename}` | 비교 시각화 이미지 다운로드 |
| GET | `/api/statistics` | 시스템 통계 |
| GET | `/api/health` | 헬스 체크 |

### 샘플 요청/응답

**POST /api/compare-samples**

응답 예시:
```json
{
  "success": true,
  "metadata": {
    "image1": {
      "year": 2015,
      "date": "2015-04-17",
      "location": "제주특별자치도 제주시 일도이동 923"
    },
    "image2": {
      "year": 2020,
      "date": "2020-04-29",
      "location": "제주특별자치도 제주시 일도이동 923"
    },
    "years_difference": 5
  },
  "analysis": {
    "total_parking_spaces_detected": 15,
    "spaces_analyzed": 10,
    "abandoned_vehicles_found": 3,
    "detection_threshold": 0.9
  },
  "abandoned_vehicles": [
    {
      "parking_space_id": "vehicle_0",
      "year1": 2015,
      "year2": 2020,
      "years_difference": 5,
      "similarity_score": 0.9542,
      "similarity_percentage": 95.42,
      "threshold": 0.9,
      "is_abandoned": true,
      "risk_level": "CRITICAL",
      "status": "ABANDONED_SUSPECTED",
      "bbox": {
        "x": 120,
        "y": 340,
        "w": 80,
        "h": 60
      }
    }
  ],
  "cctv_locations": [
    {
      "id": "cctv_001",
      "name": "제주시 일도이동 주차장 1번",
      "latitude": 33.5102,
      "longitude": 126.5219,
      "stream_url": "https://example.com/stream/cctv_001",
      "is_public": true
    }
  ]
}
```

## 🔧 설정 및 조정

### 탐지 민감도 조정

**유사도 임계값 (Similarity Threshold):**
- 기본값: 0.90 (90%)
- 높일수록 (0.95): 오탐 감소, 일부 방치 차량 놓칠 수 있음
- 낮출수록 (0.85): 탐지 증가, 오탐 증가

```python
# abandoned_vehicle_detector.py 에서
detector = AbandonedVehicleDetector(similarity_threshold=0.95)
```

### 위험도 레벨 기준

```python
CRITICAL: 유사도 >= 95% AND 연도 차이 >= 3년
HIGH:     유사도 >= 90% AND 연도 차이 >= 2년
MEDIUM:   유사도 >= 85%
LOW:      유사도 < 85%
```

### PDF 변환 품질

```python
# pdf_processor.py 에서
processor = PDFProcessor(dpi=300)  # 기본값: 300 DPI
# 더 높은 품질: dpi=600 (느리지만 정확)
# 더 빠른 처리: dpi=150 (빠르지만 부정확)
```

## 🗺️ 실제 데이터 사용하기

### GeoTIFF 파일 처리

```python
from abandoned_vehicle_detector import AbandonedVehicleDetector

detector = AbandonedVehicleDetector()

# GeoJSON 주차 공간 정의
parking_spaces = [
    {
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[126.52, 33.51], [126.521, 33.51], ...]]
        },
        "properties": {"id": "parking_001"}
    }
]

# 배치 탐지
results = detector.batch_detect_abandoned_vehicles(
    parking_spaces=parking_spaces,
    geotiff_year1='path/to/2015.tif',
    geotiff_year2='path/to/2020.tif',
    year1=2015,
    year2=2020
)
```

### 국토정보플랫폼 데이터 다운로드

1. [국토정보플랫폼](https://map.ngii.go.kr) 접속
2. 항공사진 검색 및 다운로드
3. GeoTIFF 또는 PDF 형식 선택
4. 시스템에 업로드

## 🎨 프론트엔드 UI

### 주요 기능

1. **방치 차량 카드** (방치 차량 발견 시)
   - 빨간색 테두리로 강조
   - 위험도 배지 (색상 코딩)
   - 유사도 퍼센트 표시
   - 위치 정보

2. **정상 상태 표시** (방치 차량 없을 시)
   - ✅ 초록색 성공 메시지
   - "방치 차량이 발견되지 않았습니다"
   - 분석된 주차 공간 통계
   - 해당 지역 정상 관리 확인

3. **CCTV 검증 팝업**
   - 클릭 시 자동 팝업
   - CCTV 위치 정보
   - 실시간 스트림 (운영 시)

4. **통계 대시보드**
   - 탐지된 주차 공간 수
   - 분석된 공간 수
   - 방치 차량 발견 수
   - 탐지 임계값

## 🏗️ 프로젝트 구조

```
satellite_project/
├── backend/
│   ├── abandoned_vehicle_detector.py  # ResNet 기반 탐지 엔진
│   ├── pdf_processor.py               # PDF/이미지 처리
│   ├── fastapi_app.py                 # FastAPI 서버
│   ├── app.py                         # Flask 서버 (레거시)
│   ├── models.py                      # DB 모델
│   └── requirements.txt               # Python 의존성
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AbandonedVehiclePanel.tsx  # 방치 차량 UI
│   │   │   └── ...
│   │   ├── App.tsx
│   │   └── types.ts
│   └── package.json
├── sample_image1.pdf                  # 2015년 샘플
├── sample_image2.pdf                  # 2020년 샘플
├── test_abandoned_detection.py        # 테스트 스크립트
├── CLAUDE.md                          # 개발자 가이드
└── README_ABANDONED_DETECTION.md      # 이 파일
```

## 📈 성능 및 최적화

### GPU 가속
```python
# 자동으로 CUDA 사용 가능 시 GPU 활용
detector.device  # cuda 또는 cpu
```

### 배치 처리
```python
# 여러 주차 공간 동시 처리
results = detector.batch_detect_abandoned_vehicles(
    parking_spaces=large_parking_list,  # 100개 이상 가능
    ...
)
```

### 메모리 최적화
- 이미지 해상도 조정 (DPI 설정)
- 배치 크기 제한
- 모델 한 번 로드 후 재사용

## 🔒 보안 고려사항

### CCTV 접근
- 공개 CCTV만 표시
- 인증/인가 시스템 필요 (운영 시)
- HTTPS 스트리밍 권장

### 개인정보
- 차량 번호판 자동 블러 처리 (추가 개발 필요)
- GDPR/개인정보보호법 준수

## 🚧 개발 로드맵

- [ ] 차량 번호판 자동 인식 (OCR)
- [ ] 실시간 알림 시스템 (이메일/SMS)
- [ ] 관리자 대시보드
- [ ] 모바일 앱 (React Native)
- [ ] 다중 지역 동시 모니터링
- [ ] 머신러닝 모델 fine-tuning
- [ ] 클라우드 배포 (AWS/Azure)

## 📄 라이센스

MIT License

## 🙏 감사의 말

- 국토지리정보원 (항공사진 제공)
- PyTorch/torchvision (ResNet 모델)
- FastAPI 프레임워크
- React 커뮤니티

## 📞 문의

이슈 및 질문은 GitHub Issues를 이용해 주세요.

---

**Made with ❤️ for safer parking management**
