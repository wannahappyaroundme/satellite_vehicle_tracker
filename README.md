# 🚗 장기 방치 차량 탐지 시스템

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.120-009688.svg)](https://fastapi.tiangolo.com/)

> VWorld 항공사진과 AI를 활용한 장기 방치 차량 자동 탐지 시스템

[English](./README_EN.md) | **한국어**

---

## 📖 목차

- [개요](#-개요)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [빠른 시작](#-빠른-시작)
- [VWorld API 설정](#-vworld-api-설정)
- [사용 방법](#-사용-방법)
- [캐싱 시스템](#-캐싱-시스템)
- [프로젝트 구조](#-프로젝트-구조)
- [라이선스](#-라이선스)

---

## 🎯 개요

장기 방치 차량 탐지 시스템은 **VWorld API**로부터 실시간 항공사진을 받아, **ResNet50 딥러닝 모델**을 사용하여 장기간 같은 위치에 방치된 차량을 자동으로 탐지합니다.

### 핵심 원리

1. 📍 사용자가 주소 또는 좌표 입력
2. 🛰️ VWorld API에서 고해상도 항공사진 다운로드 (12cm GSD)
3. 🤖 ResNet50으로 차량 특징 추출
4. 📊 시계열 비교로 방치 여부 판단 (유사도 90% 이상)
5. ⚠️ 위험도 분류 (CRITICAL / HIGH / MEDIUM / LOW)

### 왜 이 시스템이 필요한가?

- **공공 안전**: 장기 방치 차량은 도난/유기 차량일 가능성
- **도시 미관**: 방치 차량으로 인한 주차 공간 낭비
- **자동화**: 수작업 대신 AI로 24/7 자동 모니터링
- **비용 효율**: VWorld API 무료 + 24시간 캐싱으로 월 40원

---

## ✨ 주요 기능

### 1. 실시간 항공사진 분석
- ✅ VWorld WMTS API 연동 (12cm 해상도)
- ✅ 주소 자동 변환 (지오코더 API)
- ✅ 3×3 타일 자동 병합 (768×768 픽셀)

### 2. AI 기반 방치 차량 탐지
- ✅ ResNet50 특징 추출 (ImageNet 사전학습)
- ✅ 코사인 유사도 기반 비교
- ✅ 자동 위험도 분류:
  - **CRITICAL**: 유사도 95%+ & 3년+
  - **HIGH**: 유사도 90%+ & 2년+
  - **MEDIUM**: 유사도 85%+
  - **LOW**: 85% 미만

### 3. 24시간 캐싱 시스템 ⭐
- ✅ 서버 사이드 디스크 캐싱
- ✅ 첫 요청: VWorld API 호출 (5초)
- ✅ 재요청: 캐시에서 즉시 (0.1초, **100배 빠름**)
- ✅ 자동 만료 및 정리 (24시간 TTL)
- ✅ API 호출 80% 절감

### 4. 사용자 친화적 UI
- ✅ 반응형 웹 디자인 (React + TypeScript)
- ✅ 실시간 지도 표시 (Leaflet)
- ✅ 샘플 데이터 분석 (데모 모드)
- ✅ 실제 위치 분석
- ✅ CCTV 검증 기능 (플레이스홀더)

---

## 🛠️ 기술 스택

### Backend
- **FastAPI** 0.120.0 - 고성능 Python 웹 프레임워크
- **PyTorch** 2.1.1 - ResNet50 딥러닝 모델
- **OpenCV** 4.8.1 - 이미지 처리
- **Pillow** 10.1.0 - 타일 병합
- **SQLAlchemy** 2.0.23 - ORM (선택적)

### Frontend
- **React** 18 - UI 라이브러리
- **TypeScript** - 타입 안전성
- **Leaflet** - 지도 표시
- **Styled Components** - CSS-in-JS
- **Axios** - HTTP 클라이언트

### AI/ML
- **ResNet50** - 특징 추출 (torchvision)
- **YOLOv8** - 차량 탐지 (선택적)
- **scikit-learn** - 코사인 유사도

### API & 데이터
- **VWorld API** - 항공사진, 지오코딩 (무료)
- **국토정보플랫폼** - 한국 지리 데이터

---

## 🚀 빠른 시작

### 필수 요구사항

- **Node.js** 18+
- **Python** 3.11+
- **VWorld API 키** ([신청 방법](#-vworld-api-설정))
- **Git**

### 1. 저장소 클론

```bash
git clone https://github.com/wannahappyaroundme/satellite_vehicle_tracker.git
cd satellite_vehicle_tracker
```

### 2. Backend 설정

```bash
cd backend

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. Frontend 설정

```bash
cd frontend

# 의존성 설치
npm install
```

### 4. 환경 변수 설정

프로젝트 루트의 `.env` 파일에 VWorld API 키 입력:

```bash
# 국토정보플랫폼 API 설정
NGII_API_KEY=여기에-발급받은-API-키-입력

# Backend 설정
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///satellite_tracker.db

# 캐싱 설정 (선택)
CACHE_TTL_HOURS=24
CACHE_MAX_SIZE_GB=5
```

### 5. 서버 실행

**Backend (FastAPI):**
```bash
cd backend
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

**Frontend (React):**
```bash
cd frontend
npm start
```

**브라우저에서 접속:**
```
http://localhost:3000
```

---

## 🔑 VWorld API 설정

### 1. VWorld 가입 및 API 신청

1. **https://www.vworld.kr** 접속
2. 회원가입 및 로그인
3. **마이페이지** → **오픈API 관리** → **활용신청**

### 2. 신청 정보 입력

```
서비스명: 장기방치차량탐지시스템
서비스 URL: http://localhost:3000
이용 목적: 공공안전 / 차량 관리
```

### 3. API 선택 (3개만!)

- ☑️ **WMTS/TMS API** (필수) - 항공사진 타일
- ☑️ **지오코더 API** (필수) - 주소 → 좌표
- ☑️ **WMS/WFS API** (선택) - 큰 영역 다운로드

### 4. 승인 대기

- 보통 **1~2일** 내 승인 (이메일 통지)
- 승인 후 1~2시간 내 활성화

### 5. API 키 확인 및 설정

```bash
# .env 파일 수정
NGII_API_KEY=8F1EC6DE-5BBA-329A-94AE-BD66BE1DB672
```

### 6. 테스트

```bash
cd backend
python test_ngii_api.py

# 성공 시 출력:
# ✓ 주소 검색 성공!
# ✓ 항공사진 다운로드 성공!
```

**자세한 가이드**: [VWORLD_API_GUIDE.md](./VWORLD_API_GUIDE.md)

---

## 📱 사용 방법

### 샘플 이미지 분석 (데모)

1. **"방치 차량 탐지"** 탭 클릭
2. **"샘플 이미지 분석 시작"** 버튼 클릭
3. 2015년 vs 2020년 제주시 항공사진 비교 결과 확인

### 실제 위치 분석 ⭐

1. **"방치 차량 탐지"** 탭 클릭
2. **"실제 위치 분석하기"** 버튼 클릭
3. 주소 입력 (예: `서울특별시 강남구`)
4. **"분석 시작"** 클릭
5. VWorld 항공사진 자동 다운로드 → AI 분석 → 결과 표시

### 방치 차량 확인

분석 결과에서:
- **빨간 테두리**: 방치 의심 차량
- **위험도 배지**: CRITICAL / HIGH / MEDIUM / LOW
- **유사도**: 90% 이상 = 방치 가능성 높음
- **CCTV 검증**: 실시간 확인 (플레이스홀더)

---

## 💾 캐싱 시스템

### 왜 캐싱이 필요한가?

VWorld API 호출은 **5~10초** 소요되지만, 캐싱을 사용하면 **0.1초**로 단축!

### 작동 원리

```python
# 첫 번째 요청 (강남역)
result = service.download_aerial_image(37.4979, 127.0276)
# → VWorld API 호출 (5초)
# → 결과를 cache/aerial_images/ 에 저장

# 두 번째 요청 (같은 위치)
result = service.download_aerial_image(37.4979, 127.0276)
# → 캐시에서 즉시 반환 (0.1초) ⚡
```

### 캐시 통계 확인

```bash
curl http://localhost:8000/api/cache/stats

# 결과:
# {
#   "total_requests": 100,
#   "cache_hits": 85,
#   "hit_rate_percent": 85.0,
#   "total_size_mb": 42.5
# }
```

### 캐시 관리

```bash
# 만료된 캐시 정리 (24시간 이상)
curl -X POST http://localhost:8000/api/cache/cleanup

# 전체 캐시 삭제
curl -X DELETE http://localhost:8000/api/cache/clear
```

### 비용 및 용량

- **하루 100회 요청**: 50MB
- **월간 사용량**: 1.5GB
- **스토리지 비용**: $0.03/월 (약 40원)
- **API 절감**: 80% (캐시 히트율 기준)

---

## 📂 프로젝트 구조

```
satellite_project/
├── backend/
│   ├── fastapi_app.py              # FastAPI 메인 서버
│   ├── ngii_api_service.py         # VWorld API 연동 + 캐싱
│   ├── aerial_image_cache.py       # 캐싱 시스템
│   ├── abandoned_vehicle_detector.py  # ResNet50 탐지기
│   ├── pdf_processor.py            # 이미지 처리
│   ├── demo_mode.py                # 데모 데이터
│   ├── test_ngii_api.py            # API 테스트
│   ├── test_cache_system.py        # 캐싱 테스트
│   ├── cache/                      # 캐시 저장소
│   │   └── aerial_images/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AbandonedVehiclePanel.tsx  # 방치차량 UI
│   │   │   └── SearchPanel.tsx            # 위치 검색 UI
│   │   ├── services/
│   │   │   └── api.ts              # API 클라이언트
│   │   └── App.tsx
│   ├── package.json
│   └── tsconfig.json
│
├── sample_image1.pdf               # 샘플 항공사진 (2015년)
├── sample_image2.pdf               # 샘플 항공사진 (2020년)
├── .env                            # 환경 변수 (API 키)
├── CLAUDE.md                       # 개발 가이드
├── VWORLD_API_GUIDE.md             # VWorld API 가이드
├── README.md                       # 한국어 문서 (이 파일)
└── README_EN.md                    # 영어 문서
```

---

## 🧪 테스트

### Backend 테스트

```bash
cd backend

# VWorld API 연결 테스트
python test_ngii_api.py

# 캐싱 시스템 성능 테스트
python test_cache_system.py
```

### Frontend 테스트

```bash
cd frontend

# TypeScript 타입 체크
npm run lint

# 테스트 실행
npm test
```

---

## 🤝 기여

기여를 환영합니다! Pull Request를 보내주세요.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 지원

### VWorld API 관련
- 📞 **1661-0115** (평일 09:00~18:00)
- 🌐 https://www.vworld.kr
- 📧 support@vworld.kr

### 프로젝트 관련
- 🐛 **Issues**: [GitHub Issues](https://github.com/wannahappyaroundme/satellite_vehicle_tracker/issues)

---

## 📄 라이선스

MIT License - 자유롭게 사용하세요!

---

## 🙏 감사의 말

- **VWorld (브이월드)** - 무료 항공사진 API 제공
- **국토지리정보원 (NGII)** - 한국 지리 데이터
- **FastAPI** - 훌륭한 Python 웹 프레임워크
- **PyTorch** - ResNet50 사전학습 모델

---

**Made with ❤️ for safer streets**

[⬆ 맨 위로](#-장기-방치-차량-탐지-시스템)
