pyt# 🎭 데모 모드 사용 가이드

## ✨ API 키 없이 전체 시스템 작동!

데모 모드는 **국토정보플랫폼 API 키 없이** 전체 시스템을 테스트할 수 있도록 Mock 데이터를 제공합니다.

---

## 🚀 빠른 시작 (2분)

### 1️⃣ 백엔드 시작

```bash
cd backend
python fastapi_app.py
```

**예상 출력:**

```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
🎭 데모 모드 활성화됨
```

### 2️⃣ 프론트엔드 시작

새 터미널:

```bash
cd frontend
npm start
```

브라우저 자동 오픈: **http://localhost:3000**

### 3️⃣ 사용하기

1. **주소 선택**

   - 시/도: 서울특별시
   - 시/군/구: 강남구
   - "위치 검색" 클릭

2. **지도 확인**

   - 지도가 강남구로 이동
   - 상태 메시지: "위치 찾음: 서울특별시 강남구 🎭 (데모 모드)"

3. **분석 실행**

   - "방치 차량 분석" 버튼 클릭
   - 1-2초 후 결과 표시

4. **결과 확인**
   - 🔵 파란색 마커: 방치 차량 위치
   - 마커 클릭 → 상세 정보 팝업
   - 우측 하단: 통계 (0-5대)

---

## 🎯 데모 모드 특징

### ✅ 작동하는 기능

1. **주소 검색**

   - 17개 시/도 지원
   - 주요 시/군/구 좌표 제공
   - 실제 API와 동일한 응답 형식

2. **지도 이동**

   - 선택한 지역으로 자동 이동
   - Leaflet 지도 정상 작동
   - 줌 레벨 자동 조정 (17)

3. **방치 차량 생성**

   - 랜덤 0-5대 생성
   - 실제와 동일한 데이터 구조
   - 유사도, 위험도, 경과년수 포함

4. **상세 정보**
   - 차량 클릭 시 팝업
   - 유사도 (85-98%)
   - 위험도 (CRITICAL/HIGH/MEDIUM/LOW)
   - 경과 시간 (1-5년)

### 📊 Mock 데이터

#### 지원 도시 (서울 25개구 + 부산, 인천, 대전, 제주 등)

```javascript
서울특별시: 25개 구 (강남, 강북, 강동, ...)
부산광역시: 5개 구
인천광역시: 3개 구
대전광역시: 5개 구
제주특별자치도: 2개 시
경기도: 6개 시
```

#### 방치 차량 데이터

```json
{
  "id": "demo_vehicle_0",
  "latitude": 37.5172,
  "longitude": 127.0473,
  "similarity_percentage": 95.42,
  "risk_level": "CRITICAL",
  "years_difference": 3
}
```

---

## 🔄 실제 API로 전환

### 방법 1: 코드 수정

**frontend/src/components/MainDetectionPage.tsx**

```typescript
// 9번째 줄
const USE_DEMO_MODE = false; // true → false
```

### 방법 2: 환경 변수

```bash
# .env 파일에 추가
REACT_APP_USE_DEMO_MODE=false
```

**그 후:**

1. API 키 설정 (.env 파일의 NGII_API_KEY)
2. 백엔드/프론트엔드 재시작
3. 실제 항공사진 사용 가능

---

## 🧪 테스트 시나리오

### 시나리오 1: 방치 차량 발견

```bash
1. 시/도: 서울특별시
2. 시/군/구: 강남구
3. 위치 검색 → 분석
4. 결과: 0-5대 랜덤 생성
5. 파란색 마커 클릭 → 상세 정보
```

### 시나리오 2: 다른 지역 비교

```bash
1. 제주특별자치도 → 제주시 → 분석
2. 부산광역시 → 해운대구 → 분석
3. 각 지역별 다른 결과 확인
```

### 시나리오 3: 업데이트 기능

```bash
1. 첫 번째 분석 실행
2. "업데이트" 버튼 클릭
3. 새로운 랜덤 데이터 생성
```

---

## 📡 API 엔드포인트

### 데모 모드 전용

| Method | Endpoint                     | 설명                  |
| ------ | ---------------------------- | --------------------- |
| GET    | `/api/demo/address/search`   | 주소 검색 (Mock)      |
| POST   | `/api/demo/analyze-location` | 방치 차량 분석 (Mock) |

### 실제 API

| Method | Endpoint                | 설명                    |
| ------ | ----------------------- | ----------------------- |
| GET    | `/api/address/search`   | 주소 검색 (NGII API)    |
| POST   | `/api/analyze-location` | 방치 차량 분석 (ResNet) |

---

## 🎨 UI 확인 사항

### 데모 모드 표시

- ✅ "🎭 (데모 모드)" 문구
- ✅ 상태 메시지에 표시
- ✅ 실제와 구분 가능

### 기능 동작

- ✅ 드롭다운 선택
- ✅ 지도 이동
- ✅ 마커 표시 (파란색)
- ✅ 팝업 열기
- ✅ 통계 표시

### 색상 테마

- ⚫ 배경: 검은색
- ⚪ 텍스트: 흰색
- 🔵 마커: 파란색 (#3B82F6)
- 🟢 정상: 초록색 (#10B981)

---

## 🐛 문제 해결

### 문제 1: "Cannot connect to backend"

```bash
# 백엔드 실행 확인
cd backend
python fastapi_app.py

# 포트 8000 사용 중인지 확인
lsof -i :8000
```

### 문제 2: 지도가 표시되지 않음

```bash
# 프론트엔드 재시작
cd frontend
npm start
```

### 문제 3: 마커가 클릭되지 않음

- 브라우저 콘솔 확인 (F12)
- 페이지 새로고침 (Ctrl+Shift+R)

### 문제 4: "Module not found: demo_mode"

```bash
cd backend
pip install python-dotenv requests
```

---

## 📝 코드 구조

### Backend

```
backend/
├── demo_mode.py          ← 🆕 데모 데이터 생성
├── fastapi_app.py        ← /api/demo/* 엔드포인트 추가
├── ngii_api_service.py   ← 실제 API (데모 시 미사용)
└── abandoned_vehicle_detector.py
```

### Frontend

```
frontend/src/components/
└── MainDetectionPage.tsx  ← USE_DEMO_MODE 플래그
```

---

## 🎬 데모 영상 (가상)

```
1. [00:00] 시작 화면
2. [00:10] 서울 강남구 검색
3. [00:15] 지도 이동 확인
4. [00:20] 분석 버튼 클릭
5. [00:25] 방치 차량 3대 발견
6. [00:30] 파란색 마커 클릭
7. [00:35] 상세 정보 팝업
8. [00:40] 위성사진 영역 (준비 중)
```

---

## ✅ 체크리스트

### 데모 모드 작동 확인

- [ ] 백엔드 서버 시작 (port 8000)
- [ ] 프론트엔드 서버 시작 (port 3000)
- [ ] 브라우저 접속 (localhost:3000)
- [ ] 시/도 드롭다운 정상
- [ ] 위치 검색 성공
- [ ] 지도 이동 확인
- [ ] 분석 버튼 클릭
- [ ] 파란색 마커 표시
- [ ] 마커 클릭 시 팝업
- [ ] 통계 표시 정상
- [ ] "🎭 데모 모드" 문구 확인

### GitHub Actions 확인

- [ ] `.github/workflows/deploy.yml` 존재
- [ ] Python 의존성 설치
- [ ] Node.js 의존성 설치
- [ ] Frontend 빌드 성공
- [ ] Linting 통과

---

## 🎉 결론

**데모 모드로 API 키 없이 전체 시스템을 완벽하게 테스트할 수 있습니다!**

### 즉시 가능:

- ✅ 주소 검색 (17개 시/도)
- ✅ 지도 이동
- ✅ 방치 차량 표시
- ✅ 상세 정보 확인
- ✅ UI/UX 검증

### API 키 설정 후:

- ✨ 실제 항공사진
- ✨ 정확한 좌표
- ✨ ResNet 탐지

---

**지금 바로 시작하세요!** 🚀

```bash
# Terminal 1
cd backend && python fastapi_app.py

# Terminal 2
cd frontend && npm start

# 브라우저: http://localhost:3000
```

**작성일:** 2025-10-23
**버전:** 1.0.0
**모드:** 데모 (API 키 불필요)
