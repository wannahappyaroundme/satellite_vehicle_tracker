# 🚀 빠른 시작 - 데모 모드

**API 키 없이 즉시 실행 가능!** ✅

---

## ⚡ 1분 안에 시작하기

### Terminal 1 - Backend 실행

```bash
cd backend
python fastapi_app.py
```

**출력 확인:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Terminal 2 - Frontend 실행

```bash
cd frontend
npm start
```

**자동으로 브라우저가 열립니다:** http://localhost:3000

---

## 🎯 데모 시나리오

### 1️⃣ 서울 강남구 검색

1. **시/도**: `서울특별시` 선택
2. **시/군/구**: `강남구` 선택
3. **"위치 검색"** 버튼 클릭

**결과:**
- ✅ 지도가 강남구로 이동
- ✅ 상태: "위치 찾음: 서울특별시 강남구 🎭 (데모 모드)"

### 2️⃣ 방치 차량 분석

1. **"방치 차량 분석"** 버튼 클릭
2. 1-2초 대기

**결과:**
- 🔵 파란색 마커 0-5개 생성 (랜덤)
- 📊 우측 하단에 통계 표시

### 3️⃣ 차량 상세 정보

1. 🔵 **파란색 마커** 클릭

**팝업 표시:**
```
🚗 방치 의심 차량
유사도: 96.36%
위험도: CRITICAL
경과: 3년
```

---

## 🌆 지원 도시 (60+)

### 서울 (25개구)
강남, 강동, 강북, 강서, 관악, 광진, 구로, 금천, 노원, 도봉, 동대문, 동작, 마포, 서대문, 서초, 성동, 성북, 송파, 양천, 영등포, 용산, 은평, 종로, 중, 중랑

### 광역시
- **부산**: 강서, 금정, 남, 동, 해운대
- **인천**: 계양, 남동, 연수
- **대전**: 대덕, 동, 서, 유성, 중

### 특별자치도
- **제주**: 제주시, 서귀포시

### 경기도
수원, 성남, 안양, 용인, 고양, 화성

---

## ✅ 테스트 검증

### 자동 테스트 실행

```bash
python test_demo_endpoints.py
```

**예상 출력:**
```
✅ 모든 테스트 통과!
  - 주소 검색: ✅ 정상
  - 방치 차량 분석: ✅ 정상
  - 데이터 구조: ✅ 정상
```

---

## 🔧 문제 해결

### Frontend 빌드 오류

**문제:** TypeScript 오류
**해결:** ✅ 이미 수정됨
- [frontend/src/components/AbandonedVehiclePanel.tsx:451](frontend/src/components/AbandonedVehiclePanel.tsx#L451)
- [frontend/src/App.tsx:1-5](frontend/src/App.tsx#L1-L5)

### Backend 시작 오류

**문제:** `ModuleNotFoundError`
**해결:**
```bash
cd backend
pip install -r requirements.txt
```

### Port 충돌

**Backend (8000번 포트):**
```bash
lsof -ti:8000 | xargs kill -9
```

**Frontend (3000번 포트):**
```bash
lsof -ti:3000 | xargs kill -9
```

---

## 📊 데모 vs 실제 비교

| 기능 | 데모 모드 | 실제 모드 |
|------|-----------|-----------|
| API 키 | ❌ 불필요 | ✅ 필요 |
| 주소 검색 | Mock 좌표 | NGII API |
| 항공사진 | 샘플 이미지 | 실제 GeoTIFF |
| 방치 차량 | 랜덤 생성 (0-5대) | ResNet 분석 |
| 지도 이동 | ✅ 작동 | ✅ 작동 |
| 마커 표시 | ✅ 작동 | ✅ 작동 |
| 팝업 | ✅ 작동 | ✅ 작동 |

---

## 🔄 실제 모드 전환

API 키 승인 후:

### 1️⃣ `.env` 업데이트

```bash
NGII_API_KEY=여기에_실제_API_키_입력
```

### 2️⃣ Frontend 플래그 변경

```typescript
// frontend/src/components/MainDetectionPage.tsx:9
const USE_DEMO_MODE = false;  // true → false
```

### 3️⃣ 재시작

```bash
# Backend & Frontend 재시작
# 이제 실제 항공사진 사용!
```

---

## 📝 주요 파일

### Backend
- [backend/demo_mode.py](backend/demo_mode.py) - Mock 데이터
- [backend/fastapi_app.py:390-416](backend/fastapi_app.py#L390-L416) - 데모 엔드포인트
- [backend/abandoned_vehicle_detector.py](backend/abandoned_vehicle_detector.py) - ResNet 검출기

### Frontend
- [frontend/src/components/MainDetectionPage.tsx](frontend/src/components/MainDetectionPage.tsx) - 메인 UI
- [frontend/src/components/MainDetectionPage.tsx:9](frontend/src/components/MainDetectionPage.tsx#L9) - `USE_DEMO_MODE` 플래그

### 테스트
- [test_demo_endpoints.py](test_demo_endpoints.py) - 자동 테스트

### 문서
- [DEMO_MODE_README.md](DEMO_MODE_README.md) - 전체 가이드
- [DEMO_READY.md](DEMO_READY.md) - 완료 요약
- 이 문서 - 빠른 시작

---

## 🎉 완료!

**모든 준비 완료:**
- ✅ TypeScript 오류 수정
- ✅ 데모 모드 테스트 통과
- ✅ 60+ 도시 지원
- ✅ API 키 불필요
- ✅ GitHub Actions 준비

**지금 바로 시작:**
```bash
# Terminal 1
cd backend && python fastapi_app.py

# Terminal 2
cd frontend && npm start

# 브라우저: http://localhost:3000
```

**작동 확인:**
1. 주소 검색 ✅
2. 지도 이동 ✅
3. 차량 분석 ✅
4. 마커 클릭 ✅
5. 🎭 데모 모드 표시 ✅

---

**문의:** [DEMO_MODE_README.md](DEMO_MODE_README.md) 참조
