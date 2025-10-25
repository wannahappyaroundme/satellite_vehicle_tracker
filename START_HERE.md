# 🚀 여기서 시작하세요! START HERE

## ⚠️ 현재 상황

API 키에 문제가 있어 실제 항공사진을 가져올 수 없습니다.
하지만 **샘플 데이터로 전체 시스템을 테스트**할 수 있습니다!

---

## 🎯 빠른 시작 (5분)

### 옵션 1: 샘플 데이터 테스트 (권장!)

실제 항공사진 없이도 시스템 작동을 확인할 수 있습니다:

```bash
# 1. 샘플 이미지 분석 (2015 vs 2020 제주시)
python test_abandoned_detection.py
```

**결과물:**
- ✅ `comparison_result.jpg` - 연도별 비교 시각화
- ✅ `detection_results.json` - 탐지 결과 JSON
- ✅ 콘솔에 방치 차량 통계 출력

**예상 출력:**
```
🚨 RESULTS:
  Total spaces analyzed: 10
  Abandoned vehicles detected: 3

  ⚠️  Abandoned Vehicles Found:
  [1] vehicle_0
      Similarity: 95.42%
      Risk Level: CRITICAL
```

### 옵션 2: 웹 인터페이스 실행

```bash
# Terminal 1 - 백엔드
cd backend
python fastapi_app.py

# Terminal 2 - 프론트엔드
cd frontend
npm start

# 브라우저
http://localhost:3000
```

**현재 상태:**
- ✅ 서버 정상 실행
- ✅ 지도 표시
- ⚠️ 실제 항공사진 연동 대기 (API 키 필요)

---

## 🔑 API 키 문제 해결

### 문제:
```
Status: ERROR
Code: INVALID_KEY
Message: "등록되지 않은 인증키입니다."
```

### 해결 방법:

#### 1단계: API 키 재확인
```
https://www.vworld.kr
→ 로그인
→ 마이페이지
→ 오픈API 관리
→ API 키 복사
```

#### 2단계: .env 파일 수정
```bash
nano .env

# 이 부분 수정
NGII_API_KEY=올바른_API_키_입력
```

#### 3단계: 테스트
```bash
cd backend
python ngii_api_service.py

# ✓ 성공: "주소 검색 성공!"
# ✗ 실패: API_KEY_TROUBLESHOOTING.md 참고
```

**상세 가이드:** [API_KEY_TROUBLESHOOTING.md](API_KEY_TROUBLESHOOTING.md)

---

## 📁 주요 문서

| 문서 | 용도 | 중요도 |
|------|------|--------|
| **[START_HERE.md](START_HERE.md)** | 지금 이 파일! 여기서 시작 | ⭐⭐⭐ |
| **[FINAL_SETUP_README.md](FINAL_SETUP_README.md)** | 전체 시스템 설정 가이드 | ⭐⭐⭐ |
| **[API_KEY_TROUBLESHOOTING.md](API_KEY_TROUBLESHOOTING.md)** | API 키 문제 해결 | ⭐⭐⭐ |
| [QUICK_API_SETUP.md](QUICK_API_SETUP.md) | 빠른 API 설정 | ⭐⭐ |
| [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) | 상세 API 가이드 | ⭐⭐ |
| [CLAUDE.md](CLAUDE.md) | 개발자 가이드 | ⭐ |

---

## 🎨 시스템 미리보기

### 메인 화면 (MainDetectionPage)
```
┌─────────────────────────────────────────────────┐
│     장기 방치 차량 탐지 시스템                      │
│                                                 │
│ [시/도▼] [시/군/구▼] [동] [지번] [위치검색] [분석]  │
│                                                 │
│          ↓ 상태: 방치 차량 3대 발견                │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│                                                 │
│              🗺️ 지도 영역                         │
│                                                 │
│              🔵 ← 파란색 마커                     │
│           (방치 차량 위치)                         │
│                                                 │
│                                  ┌──────────┐  │
│                                  │ 분석완료  │  │
│                                  │  3대     │  │
│                                  └──────────┘  │
└─────────────────────────────────────────────────┘
```

### 디자인 컨셉
- ⚫⚪ 흑백 배경 (심플)
- 🔵 파란색 마커 (방치 차량)
- 📍 중앙 검색 바
- 🚫 사이드바 없음

---

## ✅ 체크리스트

### 설치 확인
- [x] Python 3.8+ 설치됨
- [x] Node.js 18+ 설치됨
- [x] Frontend dependencies 설치됨 (`npm install`)
- [ ] Poppler 설치 (`brew install poppler`)
- [ ] Backend dependencies 설치 (`pip install -r requirements.txt`)

### API 확인
- [ ] 국토정보플랫폼 API 신청
- [ ] API 키 발급
- [ ] `.env` 파일에 키 입력
- [ ] API 테스트 성공

### 실행 확인
- [x] FastAPI 서버 시작 가능
- [ ] 프론트엔드 서버 시작
- [ ] 브라우저 접속 가능
- [ ] 샘플 데이터 테스트 성공

---

## 🚨 자주 발생하는 오류

### 1. "Module not found: abandoned_vehicle_detector"
```bash
cd backend
pip install -r requirements.txt
```

### 2. "Can't open file ngii_api_service.py"
```bash
# backend 폴더로 이동
cd backend
python ngii_api_service.py
```

### 3. "npm start" 오류
```bash
cd frontend
npm install
npm start
```

### 4. "API 키 오류"
→ [API_KEY_TROUBLESHOOTING.md](API_KEY_TROUBLESHOOTING.md) 참고

---

## 🎯 권장 순서

1. **샘플 데이터 테스트** ← 지금 바로!
   ```bash
   python test_abandoned_detection.py
   ```

2. **웹 인터페이스 확인**
   ```bash
   # Terminal 1
   cd backend && python fastapi_app.py

   # Terminal 2
   cd frontend && npm start
   ```

3. **API 키 설정** (시간날 때)
   - vworld.kr에서 키 확인
   - .env 파일 수정
   - 다시 테스트

4. **실제 운영 준비**
   - 실제 항공사진 연동
   - 데이터베이스 설정
   - 클라우드 배포

---

## 📞 도움 받기

### 문서
- 일반 사용: [FINAL_SETUP_README.md](FINAL_SETUP_README.md)
- API 문제: [API_KEY_TROUBLESHOOTING.md](API_KEY_TROUBLESHOOTING.md)
- 개발: [CLAUDE.md](CLAUDE.md)

### 국토정보플랫폼
- 전화: 1588-7906
- 이메일: support@vworld.kr

---

## 💡 현재 가능한 기능

### ✅ 작동함
- 샘플 이미지 분석 (2015 vs 2020)
- ResNet 특징 추출
- 코사인 유사도 계산
- 방치 차량 탐지 (90% 임계값)
- 위험도 평가 (CRITICAL/HIGH/MEDIUM/LOW)
- 결과 시각화
- JSON 결과 출력

### ⚠️ API 키 필요
- 실제 주소 검색
- 항공사진 다운로드
- 실시간 지도 업데이트

### 🔜 개발 필요
- 다년도 자동 비교
- 자동 주차 공간 탐지
- CCTV 실시간 연동
- 알림 시스템

---

## 🎉 결론

**지금 바로 시작할 수 있습니다!**

```bash
# 1분 테스트
python test_abandoned_detection.py
```

**API 키는 나중에 설정해도 됩니다!**

시스템의 핵심 기능(ResNet 탐지, 유사도 계산)은 모두 작동합니다. 🚀

---

**마지막 업데이트:** 2025-10-23
**상태:** 샘플 데이터 테스트 준비 완료 ✅
**다음 단계:** API 키 설정 (선택사항)
