# 🚀 Render.com 무료 배포 가이드

> **GitHub Pages 네트워크 에러 해결 완료!**
> 이제 다른 사람들도 당신의 앱에 접속할 수 있습니다! 🎉

---

## 📋 준비물

- ✅ GitHub 계정 (이미 있음)
- ✅ Render.com 계정 (무료, 신용카드 불필요)
- ✅ 5-10분의 시간

---

## 🎯 Step 1: GitHub에 변경사항 푸시

```bash
# 프로젝트 루트 디렉토리에서
git add .
git commit -m "Add Render.com deployment configuration"
git push origin main
```

**변경된 파일:**
- ✅ `render.yaml` - Render 배포 설정
- ✅ `frontend/.env.production` - 프로덕션 환경 변수
- ✅ `.github/workflows/gh-pages.yml` - GitHub Actions 업데이트

---

## 🎯 Step 2: Render.com 가입 및 배포

### 2-1. Render.com 가입
1. https://render.com 접속
2. **"Sign Up"** 클릭
3. **"Continue with GitHub"** 선택
4. GitHub 로그인 및 권한 승인

### 2-2. 웹 서비스 생성
1. 대시보드에서 **"New +"** 클릭
2. **"Web Service"** 선택
3. GitHub 저장소 연결:
   - **"Connect repository"** 클릭
   - `satellite_project` 저장소 찾기
   - **"Connect"** 클릭

### 2-3. 배포 설정 (자동 완료!)
`render.yaml` 파일이 있으면 Render가 자동으로 설정을 읽습니다:
- ✅ Service Name: `satellite-vehicle-backend`
- ✅ Environment: `Python`
- ✅ Build Command: 자동 설정됨
- ✅ Start Command: 자동 설정됨
- ✅ Plan: `Free`

**아무것도 입력하지 않고** 그냥 **"Create Web Service"** 클릭!

### 2-4. 배포 완료 기다리기
- ⏱️ 첫 배포: 10-15분 소요 (PyTorch, OpenCV 등 설치)
- 📊 로그에서 진행 상황 확인 가능
- ✅ "Your service is live" 메시지가 나오면 완료!

**배포 URL:**
```
https://satellite-vehicle-backend.onrender.com
```

---

## 🎯 Step 3: GitHub Pages 재배포

GitHub Actions가 자동으로 프론트엔드를 재배포합니다:

1. GitHub 저장소 → **"Actions"** 탭 확인
2. "Deploy to GitHub Pages" 워크플로우가 실행됨
3. 5분 정도 대기
4. ✅ 완료되면 자동으로 배포됨!

**또는 수동 재배포:**
```bash
cd frontend
npm run build
npm run deploy
```

---

## 🎯 Step 4: 테스트 및 확인

### 4-1. 백엔드 Health Check
```bash
curl https://satellite-vehicle-backend.onrender.com/api/health
```

**예상 응답:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-29T...",
  "services": {
    "abandoned_vehicle_detector": "ready",
    "pdf_processor": "ready"
  }
}
```

### 4-2. 프론트엔드 테스트
1. https://wannahappyaroundme.github.io/satellite_vehicle_tracker/ 접속
2. **"방치 차량 탐지"** 탭 클릭
3. **"샘플 이미지 분석 시작"** 버튼 클릭

**⚠️ 첫 요청은 20초 정도 걸립니다!**
- Render 무료 플랜은 15분 미사용 시 슬립 모드
- 첫 요청 시 서버를 깨우는 시간 필요
- 이후 요청은 정상 속도 (2-3초)

### 4-3. 정상 동작 확인
- ✅ Network Error 없음
- ✅ API 응답 정상
- ✅ 방치 차량 데이터 표시
- ✅ 다른 사람도 접속 가능!

---

## ⚠️ Render 무료 플랜 제약사항

### 1. 15분 슬립 모드
- **문제:** 15분 미사용 시 서버가 슬립 모드로 전환
- **증상:** 첫 요청 시 10-20초 대기
- **해결:**
  - 방법 1: 그냥 첫 요청만 기다리기 (가장 간단)
  - 방법 2: UptimeRobot으로 5분마다 핑 보내기 (슬립 방지)

### 2. 매월 750시간 제한
- **계산:** 31일 × 24시간 = 744시간
- **결론:** 한 달 내내 24시간 운영 가능!

### 3. 매월 1일 자동 재시작
- **문제:** 매월 1일에 서버가 자동 재시작됨
- **증상:** 3-5분 다운타임
- **해결:** 데이터는 유지되며 자동으로 재시작됨

### 4. 메모리 제한 (512MB)
- **문제:** 대용량 PyTorch 모델 사용 시 메모리 부족 가능
- **해결:**
  - ResNet 모델은 괜찮음 (200MB 정도)
  - YOLOv8n (nano) 사용 중이면 문제 없음
  - 큰 모델 사용 시 유료 플랜 고려

---

## 🔧 문제 해결 (Troubleshooting)

### 문제 1: 배포 실패 (Build Failed)
**증상:** Render 로그에 "Build failed" 표시

**해결:**
1. `backend/requirements.txt` 확인
2. 특히 `gdal==3.8.0` 문제 발생 가능
3. 필요 없으면 `gdal` 제거:
   ```bash
   cd backend
   # requirements.txt에서 gdal 줄 삭제
   git commit -am "Remove gdal dependency"
   git push
   ```

### 문제 2: 슬립 모드 방지하고 싶음
**해결:** UptimeRobot 무료 모니터링 사용

1. https://uptimerobot.com 가입
2. "Add New Monitor" 클릭
3. 설정:
   - Monitor Type: `HTTP(s)`
   - URL: `https://satellite-vehicle-backend.onrender.com/api/health`
   - Monitoring Interval: `5 minutes`
4. 저장 → 5분마다 자동으로 핑 보냄 → 슬립 방지!

### 문제 3: CORS 에러
**증상:** 브라우저 콘솔에 "CORS policy" 에러

**해결:**
```python
# backend/fastapi_app.py에서 CORS 설정 확인
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인 지정 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 문제 4: 여전히 localhost 연결 시도
**증상:** 프론트엔드가 `localhost:8000`에 연결 시도

**해결:**
1. 브라우저 캐시 삭제 (Ctrl+Shift+Del)
2. GitHub Pages 재배포 확인
3. `.env.production` 파일 확인:
   ```bash
   cd frontend
   cat .env.production
   # REACT_APP_API_URL이 Render URL인지 확인
   ```

---

## 📈 성능 최적화 팁

### 1. 첫 요청 속도 개선
**문제:** 슬립 모드 깨우기에 20초 소요

**해결:**
- 프론트엔드에 로딩 메시지 표시:
  ```
  "서버를 시작하는 중... (최초 20초 소요)"
  ```

### 2. DB 디스크 용량 관리
**Render 무료 플랜:** 1GB 디스크

**모니터링:**
```python
# backend에서 DB 크기 확인
import os
db_size = os.path.getsize('abandoned_vehicles.db') / (1024*1024)
print(f"DB Size: {db_size:.2f} MB")
```

### 3. 로그 관리
**문제:** 로그 파일이 너무 커지면 디스크 부족

**해결:**
```python
# backend/logging_config.py에서 로그 파일 로테이션 설정
handlers:
  file:
    maxBytes: 10485760  # 10MB
    backupCount: 3
```

---

## 🎉 완료!

이제 당신의 앱은 전 세계 어디서든 접속 가능합니다!

**프론트엔드:** https://wannahappyaroundme.github.io/satellite_vehicle_tracker/
**백엔드:** https://satellite-vehicle-backend.onrender.com

**공유하세요!** 🚀
- 친구들에게 링크 공유
- 포트폴리오에 추가
- 이력서에 프로젝트 링크 포함

---

## 📞 문제가 생기면?

1. **Render 로그 확인:** https://dashboard.render.com → Your Service → Logs
2. **GitHub Actions 확인:** GitHub 저장소 → Actions 탭
3. **브라우저 콘솔 확인:** F12 → Console 탭

**여전히 문제가 있다면:**
- Email: bu5119@hanyang.ac.kr
- Phone: 010-5616-5119

---

## 🔗 유용한 링크

- **Render Dashboard:** https://dashboard.render.com
- **Render Docs:** https://render.com/docs
- **UptimeRobot:** https://uptimerobot.com (슬립 모드 방지)
- **GitHub Pages:** https://pages.github.com

---

**작성일:** 2025-10-29
**버전:** 1.0.0
**작성자:** Claude Code (claude.ai/code)
