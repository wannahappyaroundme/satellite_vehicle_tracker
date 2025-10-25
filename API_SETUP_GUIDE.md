# 국토정보플랫폼 API 설정 가이드
# NGII (National Geographic Information Institute) API Setup Guide

## 📋 목차
1. [API 키 발급 방법](#api-키-발급-방법)
2. [API 키 설정](#api-키-설정)
3. [테스트 방법](#테스트-방법)
4. [문제 해결](#문제-해결)

---

## 1. API 키 발급 방법

### 단계 1: 국토정보플랫폼 접속
1. [국토정보플랫폼 (vworld.kr)](https://www.vworld.kr) 접속
2. 우측 상단 "로그인" 클릭
3. 회원가입 (없는 경우) 또는 로그인

### 단계 2: 오픈 API 신청
1. 로그인 후 상단 메뉴에서 **"오픈API"** 클릭
2. **"오픈 API 활용신청"** 클릭
3. 신청 양식 작성:
   ```
   API 유형: Open API 2.0
   서비스명: 장기 방치 차량 탐지 시스템
   서비스 URL: http://localhost:3000 (개발용)
   서비스 설명: 항공사진을 이용한 장기 방치 차량 탐지
   ```
4. **"신청하기"** 버튼 클릭

### 단계 3: API 키 확인
1. 신청 후 "마이페이지" → "오픈API 관리" 이동
2. 승인된 API 키 확인 (보통 즉시 승인됨)
3. **API 인증키(KEY)** 복사

**API 키 예시:**
```
12345678-ABCD-1234-EFGH-123456789ABC
```

---

## 2. API 키 설정

### 방법 1: .env 파일 수정 (권장)

1. 프로젝트 루트 디렉토리에서 `.env` 파일 열기:
   ```bash
   cd /Users/kyungsbook/Desktop/satellite_project
   nano .env  # 또는 다른 텍스트 에디터
   ```

2. `NGII_API_KEY` 부분 찾아서 **발급받은 API 키 입력**:
   ```bash
   # 수정 전
   NGII_API_KEY=여기에_발급받은_API_키를_입력하세요

   # 수정 후 (예시)
   NGII_API_KEY=12345678-ABCD-1234-EFGH-123456789ABC
   ```

3. 파일 저장 (Ctrl+O, Enter, Ctrl+X)

### 방법 2: 환경 변수로 직접 설정

```bash
# macOS/Linux
export NGII_API_KEY="12345678-ABCD-1234-EFGH-123456789ABC"

# Windows (PowerShell)
$env:NGII_API_KEY="12345678-ABCD-1234-EFGH-123456789ABC"

# Windows (CMD)
set NGII_API_KEY=12345678-ABCD-1234-EFGH-123456789ABC
```

---

## 3. 테스트 방법

### 테스트 1: API 키 확인

```bash
cd backend
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('NGII_API_KEY'))"
```

**예상 출력:**
```
API Key: 12345678-ABCD-1234-EFGH-123456789ABC
```

### 테스트 2: NGII API 서비스 테스트

```bash
cd backend
python ngii_api_service.py
```

**예상 출력 (성공 시):**
```
============================================================
국토정보플랫폼 API 테스트
============================================================

✓ 주소 검색 성공!
  주소: 제주특별자치도 제주시 일도이동 923
  위도: 33.5102
  경도: 126.5219

  항공사진 URL:
  http://api.vworld.kr/req/wms?service=WMS&request=GetMap&...

============================================================
```

**실패 시:**
```
✗ 검색 실패: API 인증 실패
```
→ API 키를 다시 확인하세요!

### 테스트 3: 전체 시스템 테스트

```bash
# 1. FastAPI 백엔드 시작
cd backend
python fastapi_app.py

# 2. 새 터미널에서 프론트엔드 시작
cd frontend
npm start

# 3. 브라우저에서 접속
# http://localhost:3000
```

**테스트 순서:**
1. "시/도" 드롭다운에서 **"제주특별자치도"** 선택
2. "시/군/구" 드롭다운에서 **"제주시"** 선택
3. "동/읍/면" 입력란에 **"일도이동"** 입력
4. "지번" 입력란에 **"923"** 입력
5. **"위치 검색"** 버튼 클릭
6. 지도가 제주시로 이동하는지 확인
7. **"방치 차량 분석"** 버튼 클릭
8. 분석 결과 확인

---

## 4. 문제 해결

### 문제 1: "API 키가 설정되지 않았습니다" 경고

**원인:** `.env` 파일에 API 키가 제대로 입력되지 않음

**해결:**
```bash
# .env 파일 확인
cat .env | grep NGII_API_KEY

# 올바른 형식인지 확인
# ✓ 좋음: NGII_API_KEY=12345678-ABCD-1234-EFGH-123456789ABC
# ✗ 나쁨: NGII_API_KEY=여기에_발급받은_API_키를_입력하세요
# ✗ 나쁨: NGII_API_KEY="12345678-ABCD-1234-EFGH-123456789ABC" (따옴표 제거)
```

### 문제 2: "주소를 찾을 수 없습니다" 오류

**원인 1:** API 키가 유효하지 않음
- 국토정보플랫폼에서 API 키 상태 확인
- 키가 승인되었는지 확인

**원인 2:** 주소 형식이 잘못됨
- 전체 주소를 정확히 입력
- 예: "서울특별시 강남구 역삼동"

**원인 3:** API 호출 횟수 초과
- 무료 플랜: 일 10,000건
- 초과 시 익일 재시도

### 문제 3: 항공사진이 표시되지 않음

**원인:** vworld WMS 서비스 접근 제한

**임시 해결:**
샘플 이미지로 테스트:
```bash
python test_abandoned_detection.py
```

**장기 해결:**
1. 국토정보플랫폼에서 **"2D지도 API"** 추가 신청
2. 또는 **"항공영상 다운로드 API"** 신청

### 문제 4: CORS 오류

**오류 메시지:**
```
Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**해결:**
1. FastAPI 서버 재시작
2. 프론트엔드 재시작
3. 브라우저 캐시 삭제 (Ctrl+Shift+R)

### 문제 5: "Module not found: ngii_api_service"

**해결:**
```bash
cd backend
pip install python-dotenv requests
```

---

## 5. API 사용량 확인

### 국토정보플랫폼에서 확인
1. [vworld.kr](https://www.vworld.kr) 로그인
2. "마이페이지" → "오픈API 관리"
3. "사용현황" 클릭
4. 일별/월별 사용량 확인

### 무료 플랜 제한
- **오픈 API 2.0:** 일 10,000건
- **2D지도 API:** 일 50,000건
- **항공영상:** 다운로드 제한 있음

### 초과 시 대응
1. 유료 플랜 전환 (기업용)
2. 샘플 이미지로 데모 운영
3. 캐싱 구현으로 API 호출 최소화

---

## 6. 보안 권장사항

### ⚠️ 중요: API 키 보호

1. **절대 GitHub에 업로드하지 마세요!**
   ```bash
   # .gitignore 파일 확인
   cat .gitignore | grep .env

   # .env 파일이 목록에 있어야 함
   ```

2. **환경 변수 파일 권한 설정**
   ```bash
   chmod 600 .env  # 본인만 읽기/쓰기 가능
   ```

3. **프로덕션 배포 시**
   - 서버 환경 변수로 설정
   - AWS Secrets Manager / Azure Key Vault 사용
   - Docker secrets 사용

---

## 7. 추가 리소스

### 공식 문서
- [국토정보플랫폼 오픈API 가이드](https://www.vworld.kr/dev/v4dv_2ddataguide2_s001.do)
- [vworld API 레퍼런스](https://www.vworld.kr/dev/v4dv_apiguide_s001.do)

### 예제 코드
- `backend/ngii_api_service.py` - API 연동 서비스
- `test_abandoned_detection.py` - 테스트 스크립트

### 문의
- 국토정보플랫폼 고객센터: 1588-7906
- 이메일: support@vworld.kr

---

## ✅ 체크리스트

설정 완료 전 확인:

- [ ] 국토정보플랫폼 회원가입 완료
- [ ] 오픈 API 신청 및 승인 완료
- [ ] API 키 발급 받음
- [ ] `.env` 파일에 API 키 입력
- [ ] `python ngii_api_service.py` 테스트 성공
- [ ] 제주시 일도이동 주소 검색 성공
- [ ] FastAPI 서버 정상 시작
- [ ] 프론트엔드에서 주소 검색 성공
- [ ] 지도가 올바른 위치로 이동

**모든 항목에 체크가 되면 시스템 사용 준비 완료!** 🎉

---

**작성일:** 2025-10-23
**버전:** 1.0.0
**문서 상태:** 완료
