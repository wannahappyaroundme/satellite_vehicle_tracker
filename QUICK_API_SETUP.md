# 🚀 빠른 API 설정 가이드

## 1️⃣ API 키 발급 (5분)

1. https://www.vworld.kr 접속 → 로그인
2. 상단 **"오픈API"** → **"오픈 API 활용신청"**
3. 양식 작성 후 신청
4. "마이페이지" → "오픈API 관리"에서 키 복사

## 2️⃣ API 키 입력 (1분)

```bash
# 프로젝트 폴더의 .env 파일 열기
cd /Users/kyungsbook/Desktop/satellite_project
nano .env

# 이 부분 찾아서 수정:
NGII_API_KEY=여기에_발급받은_API_키를_입력하세요
          ↓
NGII_API_KEY=12345678-ABCD-1234-EFGH-123456789ABC
          (실제 발급받은 키 입력)

# 저장: Ctrl+O, Enter, Ctrl+X
```

## 3️⃣ 테스트 (1분)

```bash
cd backend
python ngii_api_service.py

# ✓ 성공: "주소 검색 성공!" 메시지 확인
# ✗ 실패: API 키 다시 확인
```

## 4️⃣ 실행 (2분)

```bash
# Terminal 1 - 백엔드
cd backend
python fastapi_app.py

# Terminal 2 - 프론트엔드
cd frontend
npm start

# 브라우저: http://localhost:3000
```

---

**API 키는 반드시 .env 파일에 입력하세요!**

상세 가이드: [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md)
