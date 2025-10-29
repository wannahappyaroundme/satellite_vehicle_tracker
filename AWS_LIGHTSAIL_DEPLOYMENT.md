# AWS Lightsail 배포 가이드

## 비용 및 플랜

### 추천 플랜: $3.50/월
- **메모리:** 512MB RAM
- **CPU:** 1 vCPU
- **스토리지:** 20GB SSD
- **트래픽:** 1TB/월
- **고정 IP:** 무료 포함
- **첫 3개월 무료 체험 가능**

이 플랜으로 MobileNetV2 + FastAPI를 충분히 실행할 수 있습니다.

---

## 배포 단계

### 1단계: AWS Lightsail 인스턴스 생성

1. **AWS Lightsail 콘솔 접속**
   - https://lightsail.aws.amazon.com/
   - AWS 계정으로 로그인

2. **인스턴스 생성**
   - "Create instance" 클릭
   - **리전 선택:** Asia Pacific (Seoul) ap-northeast-2
   - **플랫폼:** Linux/Unix
   - **운영체제:** Ubuntu 22.04 LTS
   - **플랜:** $3.50/월 (512MB RAM)
   - **인스턴스 이름:** satellite-backend

3. **SSH 키 다운로드**
   - "Download default key" 클릭
   - `LightsailDefaultKey-ap-northeast-2.pem` 파일 저장

4. **인스턴스 시작 대기**
   - 약 1-2분 소요
   - 상태가 "Running"이 될 때까지 대기

---

### 2단계: 고정 IP 할당 (중요!)

1. **Networking 탭 클릭**
2. **"Create static IP" 클릭**
3. **인스턴스 선택:** satellite-backend
4. **이름:** satellite-backend-ip
5. **Create 클릭**

> **왜 필요한가?** 인스턴스를 재시작해도 IP가 바뀌지 않아 프론트엔드 연결이 안정적입니다.

**고정 IP 주소를 메모하세요!** (예: 13.125.123.45)

---

### 3단계: 방화벽 설정

1. **Networking 탭에서 "Add rule" 클릭**
2. **포트 80 (HTTP) 열기:**
   - Application: HTTP
   - Protocol: TCP
   - Port: 80
3. **포트 443 (HTTPS) 열기 (나중을 위해):**
   - Application: HTTPS
   - Protocol: TCP
   - Port: 443

---

### 4단계: SSH 접속 및 배포

#### 옵션 A: Lightsail 브라우저 SSH (간단)

1. 인스턴스 페이지에서 **"Connect using SSH" 클릭**
2. 터미널 창이 열림

#### 옵션 B: 로컬 터미널에서 SSH (추천)

```bash
# 1. SSH 키 권한 설정 (Mac/Linux)
chmod 400 ~/Downloads/LightsailDefaultKey-ap-northeast-2.pem

# 2. SSH 접속 (고정 IP 사용)
ssh -i ~/Downloads/LightsailDefaultKey-ap-northeast-2.pem ubuntu@YOUR_STATIC_IP
```

---

### 5단계: 배포 스크립트 실행

SSH 접속 후:

```bash
# 1. 배포 스크립트 다운로드
wget https://raw.githubusercontent.com/wannahappyaroundme/satellite_vehicle_tracker/main/lightsail-startup.sh

# 2. 실행 권한 부여
chmod +x lightsail-startup.sh

# 3. 배포 실행 (약 5-10분 소요)
./lightsail-startup.sh
```

스크립트가 자동으로 다음을 수행합니다:
- Python 3.11 설치
- 시스템 의존성 설치 (poppler 등)
- 프로젝트 클론
- Python 패키지 설치
- Supervisor 설정 (자동 재시작)
- Nginx 설정 (리버스 프록시)
- 서비스 시작

---

### 6단계: 배포 확인

```bash
# 1. 백엔드 헬스 체크
curl http://YOUR_STATIC_IP/api/health

# 응답 예시:
# {"status":"healthy","timestamp":"2025-10-30T06:15:02.408707","services":{"abandoned_vehicle_detector":"ready","pdf_processor":"ready"}}

# 2. 방치 차량 데이터 확인
curl http://YOUR_STATIC_IP/api/abandoned-vehicles

# 3. API 문서 확인 (브라우저에서)
# http://YOUR_STATIC_IP/docs
```

---

### 7단계: 프론트엔드 연결

#### A. 환경 변수 파일 업데이트

`frontend/.env.production` 파일 수정:

```env
# AWS Lightsail 고정 IP 사용
REACT_APP_API_URL=http://YOUR_STATIC_IP/api
REACT_APP_FASTAPI_URL=http://YOUR_STATIC_IP/api
```

#### B. GitHub 워크플로우 업데이트

`.github/workflows/gh-pages.yml` 파일 수정:

```yaml
- name: Build
  run: |
    cd frontend
    npm run build
  env:
    REACT_APP_API_URL: http://YOUR_STATIC_IP/api
    REACT_APP_FASTAPI_URL: http://YOUR_STATIC_IP/api
```

#### C. 변경 사항 푸시

```bash
git add frontend/.env.production .github/workflows/gh-pages.yml
git commit -m "Update backend URL to AWS Lightsail"
git push origin main
```

약 2-3분 후 GitHub Actions가 자동으로 프론트엔드를 재배포합니다.

---

## 운영 가이드

### 로그 확인

```bash
# 실시간 로그 보기
sudo tail -f /var/log/satellite-backend.out.log

# 에러 로그 보기
sudo tail -f /var/log/satellite-backend.err.log
```

### 서비스 재시작

```bash
# 백엔드만 재시작
sudo supervisorctl restart satellite-backend

# Nginx 재시작
sudo systemctl restart nginx

# 서비스 상태 확인
sudo supervisorctl status
```

### 코드 업데이트

```bash
# 1. SSH 접속
ssh -i ~/Downloads/LightsailDefaultKey-ap-northeast-2.pem ubuntu@YOUR_STATIC_IP

# 2. 최신 코드 가져오기
cd /home/ubuntu/satellite_vehicle_tracker
git pull origin main

# 3. 패키지 업데이트 (필요시)
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 4. 서비스 재시작
sudo supervisorctl restart satellite-backend
```

### 데이터베이스 백업

```bash
# SQLite DB 백업
cd /home/ubuntu/satellite_vehicle_tracker/backend
cp satellite_tracker.db satellite_tracker.db.backup_$(date +%Y%m%d)

# 로컬로 다운로드
scp -i ~/Downloads/LightsailDefaultKey-ap-northeast-2.pem \
  ubuntu@YOUR_STATIC_IP:/home/ubuntu/satellite_vehicle_tracker/backend/satellite_tracker.db \
  ./satellite_tracker_backup.db
```

---

## 비용 최적화

### 스냅샷 활용

인스턴스 스냅샷을 생성하면:
- 설정이 완료된 상태를 저장
- 문제 발생 시 빠르게 복구
- 다른 리전으로 복사 가능

```
Lightsail 콘솔 → Snapshots 탭 → Create snapshot
```

### 모니터링

Lightsail 콘솔에서 무료로 제공:
- CPU 사용률
- 네트워크 트래픽
- 디스크 사용량

알림 설정:
- Alarms 탭에서 CPU/네트워크 임계값 설정
- 이메일 알림 받기

---

## HTTPS 설정 (선택 사항)

무료 SSL 인증서 사용 (Let's Encrypt):

```bash
# 1. Certbot 설치
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# 2. 도메인 필요 (예: yourdomain.com)
# Lightsail 고정 IP를 도메인에 연결

# 3. SSL 인증서 발급
sudo certbot --nginx -d yourdomain.com

# 4. 자동 갱신 설정
sudo certbot renew --dry-run
```

---

## 문제 해결

### 서비스가 시작되지 않을 때

```bash
# 상세 로그 확인
sudo supervisorctl tail -f satellite-backend stderr

# Python 환경 확인
cd /home/ubuntu/satellite_vehicle_tracker/backend
source venv/bin/activate
python --version  # Python 3.11이어야 함

# 수동으로 실행해보기
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

### 메모리 부족 시

```bash
# 메모리 사용량 확인
free -h

# 프로세스 메모리 확인
ps aux --sort=-%mem | head -10
```

**해결 방법:**
- $5/월 플랜으로 업그레이드 (1GB RAM)
- Lightsail 콘솔에서 "Upgrade" 클릭

### CORS 에러 발생 시

Nginx 설정 확인:

```bash
sudo nano /etc/nginx/sites-available/satellite-backend

# CORS 헤더가 있는지 확인
# add_header 'Access-Control-Allow-Origin' '*' always;

sudo nginx -t  # 설정 문법 검사
sudo systemctl restart nginx
```

---

## 비교: Lightsail vs ngrok vs Render

| 항목 | AWS Lightsail | ngrok | Render |
|------|--------------|-------|--------|
| **비용** | $3.50/월 | 무료 (제한적) | 무료 (512MB) |
| **안정성** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ (로컬 PC 필요) | ⭐⭐⭐⭐ (타임아웃 이슈) |
| **고정 IP** | ✅ 무료 | ❌ URL 변경됨 | ✅ 고정 URL |
| **설정 난이도** | 쉬움 | 매우 쉬움 | 쉬움 |
| **컴퓨터 켜둠** | 불필요 | 필요 | 불필요 |
| **SQLite 저장** | ✅ 영구 | ✅ 영구 | ❌ 휘발성 |
| **SSH 접속** | ✅ 가능 | ❌ 불가 | ❌ 불가 |
| **스케일업** | ✅ 쉬움 | ❌ 불가 | ⚠️ 유료 |

**결론:** Lightsail이 장기적으로 가장 안정적이고 비용 효율적입니다.

---

## 다음 단계

1. ✅ **배포 완료**
   - http://YOUR_STATIC_IP/api/health 접속 확인

2. 📱 **프론트엔드 연결**
   - GitHub Pages가 Lightsail IP로 API 호출

3. 🔒 **HTTPS 설정 (선택)**
   - 도메인 구매 후 SSL 인증서 발급

4. 📊 **모니터링**
   - Lightsail 알림 설정
   - 로그 정기 확인

5. 🚀 **최적화**
   - 트래픽 증가 시 플랜 업그레이드
   - 필요시 RDS로 DB 마이그레이션

---

## 지원

문제가 발생하면:
1. 로그 확인: `sudo tail -f /var/log/satellite-backend.err.log`
2. GitHub Issues에 문의
3. AWS 지원 센터 (유료 플랜에서 제공)
