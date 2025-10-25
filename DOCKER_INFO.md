# Docker 배포 정보

## 📦 Docker가 필요한 이유

### 현재 상태: **사용 안 함** ❌

**로컬 개발만 하는 경우:**
- 데모 모드로 충분
- `npm start`, `python fastapi_app.py`로 실행
- Docker 불필요

---

## 🚀 Docker가 필요한 경우

### 프로덕션 배포 시:

**장점:**
1. **일관된 환경**: 개발/테스트/프로덕션 환경 통일
2. **쉬운 배포**: 서버에 Docker만 설치하면 실행
3. **확장성**: 여러 서버에 동일하게 배포
4. **의존성 관리**: Python, Node.js 버전 고정

**사용 시나리오:**
- AWS, GCP, Azure 등 클라우드 배포
- 여러 서버에 동시 배포
- CI/CD 자동화
- 팀 협업 (동일 환경)

---

## 📁 현재 Docker 파일

### 파일 목록:
- `docker-compose.yml` - 전체 서비스 orchestration
- `backend/Dockerfile` - Backend (FastAPI) 이미지
- `frontend/Dockerfile` - Frontend (React) 이미지

### 상태:
✅ **파일 유지** (나중에 배포 시 사용)
❌ **현재 미사용** (로컬 개발만)
❌ **GitHub Actions에서 제거됨** (빌드 오류 방지)

---

## 🔧 Docker 사용 방법 (배포 시)

### 1️⃣ 로컬에서 Docker로 실행

```bash
# 전체 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

**접속:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

---

### 2️⃣ Docker Hub에 배포

#### 사전 준비:
1. [Docker Hub](https://hub.docker.com) 계정 생성
2. GitHub Secrets 설정:
   - `DOCKER_USERNAME`: Docker Hub 사용자명
   - `DOCKER_PASSWORD`: Docker Hub 비밀번호

#### GitHub Actions 활성화:

`.github/workflows/deploy.yml` 수정:

```yaml
# 현재 (Docker 비활성화):
name: CI - Test and Build

# 배포 시 (Docker 활성화):
name: CI/CD - Test, Build and Deploy

jobs:
  test:
    # ... 테스트 단계 ...

  deploy:  # ← 이 부분 추가
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v4

    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Build and push backend
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        push: true
        tags: username/satellite-tracker-backend:latest

    - name: Build and push frontend
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        push: true
        tags: username/satellite-tracker-frontend:latest
```

---

### 3️⃣ 서버에 배포

#### AWS EC2 예시:

```bash
# 1. 서버 SSH 접속
ssh user@your-server.com

# 2. Docker 설치
sudo apt-get update
sudo apt-get install docker.io docker-compose

# 3. 프로젝트 클론
git clone https://github.com/username/satellite_project.git
cd satellite_project

# 4. 환경 변수 설정
echo "NGII_API_KEY=your_api_key" > .env

# 5. Docker Compose 실행
docker-compose up -d

# 6. 확인
docker-compose ps
```

**접속:**
- Frontend: http://your-server.com:3000
- Backend: http://your-server.com:8000

---

### 4️⃣ 클라우드 플랫폼 배포

#### Heroku:

```bash
# 1. Heroku 로그인
heroku login

# 2. 앱 생성
heroku create satellite-tracker-backend
heroku create satellite-tracker-frontend

# 3. Docker 배포
heroku container:push web -a satellite-tracker-backend
heroku container:release web -a satellite-tracker-backend
```

#### Google Cloud Run:

```bash
# 1. 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID

# 2. Backend 배포
gcloud builds submit --tag gcr.io/PROJECT_ID/backend
gcloud run deploy --image gcr.io/PROJECT_ID/backend

# 3. Frontend 배포
gcloud builds submit --tag gcr.io/PROJECT_ID/frontend
gcloud run deploy --image gcr.io/PROJECT_ID/frontend
```

---

## 🔄 현재 개발 워크플로우 (Docker 없음)

### 로컬 개발:

```bash
# Terminal 1 - Backend
cd backend
python fastapi_app.py

# Terminal 2 - Frontend
cd frontend
npm start
```

### GitHub Actions:

```yaml
✅ 테스트: Python lint, TypeScript lint
✅ 빌드: Frontend build
✅ 데모 모드 테스트
❌ Docker 빌드: 비활성화 (현재 불필요)
```

---

## 📊 비교표

| 항목 | 로컬 실행 | Docker 실행 |
|------|-----------|-------------|
| **설치 시간** | 5분 | 10분 |
| **시작 속도** | 빠름 (5초) | 느림 (30초) |
| **메모리 사용** | 낮음 | 높음 |
| **환경 일관성** | 낮음 | 높음 |
| **배포 용이성** | 어려움 | 쉬움 |
| **적합 용도** | 개발/테스트 | 프로덕션 |

---

## 🎯 권장 사항

### 현재 (개발 단계):
✅ **로컬 실행 권장**
- 빠른 개발
- 적은 리소스 사용
- 데모 모드로 충분

### 배포 시점:
✅ **Docker 사용 권장**
- API 키 승인 후
- 실제 서비스 오픈
- 팀 협업 필요
- 클라우드 배포

---

## 🛠️ Docker 재활성화 방법

### 1단계: GitHub Secrets 설정

GitHub Repository → Settings → Secrets and variables → Actions

- `DOCKER_USERNAME` 추가
- `DOCKER_PASSWORD` 추가

### 2단계: Workflow 수정

`.github/workflows/deploy.yml`에 deploy job 추가 (위 예시 참조)

### 3단계: Push

```bash
git add .
git commit -m "Enable Docker deployment"
git push origin main
```

→ 자동으로 Docker Hub에 이미지 업로드

---

## 📝 요약

**현재 상태:**
- Docker 파일: ✅ 존재 (유지)
- GitHub Actions: ❌ Docker 배포 비활성화
- 개발 방식: 로컬 실행 (`npm start`, `python fastapi_app.py`)

**Docker 사용 시점:**
- 프로덕션 배포 결정 후
- API 키 승인 후
- 실제 서비스 오픈 시

**현재 권장:**
- 로컬 개발 계속
- 데모 모드 활용
- 배포 필요 시 Docker 재활성화

---

**작성일:** 2025-10-23
**상태:** Docker 비활성화 (개발 단계)
