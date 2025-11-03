# AWS Lightsail 배포 가이드

## 비용 및 플랜

### 추천 플랜: $5/월 (Dual-stack)

**⚠️ 중요: 고정 IP를 사용하려면 Dual-stack 필수!**

- **메모리:** 1GB RAM
- **CPU:** 1 vCPU
- **스토리지:** 40GB SSD
- **트래픽:** 2TB/월
- **네트워킹:** Dual-stack (IPv4 + IPv6)
- **고정 IP:** 무료 포함 (IPv4)
- **첫 3개월 무료 체험 가능**

이 플랜으로 MobileNetV2 + FastAPI + SQLite를 충분히 실행할 수 있습니다.

### 왜 $3.50 플랜은 안 되나요?

- $3.50/월 플랜: **IPv6 only** → 고정 IP (IPv4) 사용 불가 ❌
- $5/월 플랜: **Dual-stack** → 고정 IP (IPv4) 사용 가능 ✅

**결론:** 프론트엔드 연결을 위해 고정 IP가 필요하므로 $5/월 플랜이 최소 요구사항입니다.

---

## 배포 단계

### 1단계: AWS 계정 생성 (처음 사용하는 경우)

**AWS 계정이 없다면:**

1. https://aws.amazon.com/ko/ 접속
2. **"AWS 계정 생성"** 클릭
3. **필요한 정보:**
   - 이메일 주소
   - 비밀번호
   - AWS 계정 이름
   - 연락처 정보
   - 신용카드 정보 (첫 3개월 무료, 과금 없음)
   - 전화번호 인증

**중요:** AWS는 첫 12개월 무료 프리티어를 제공합니다!

### 2단계: AWS Lightsail 인스턴스 생성

#### 2-1. Lightsail 콘솔 접속

1. **AWS Lightsail 접속**

   - https://lightsail.aws.amazon.com/
   - AWS 계정으로 로그인

2. **첫 화면에서 "Create instance" 버튼 클릭**
   - 주황색 큰 버튼

#### 2-2. 인스턴스 위치 선택

```
Instance location:
→ Change AWS Region and Availability Zone 클릭

Region: Asia Pacific (Seoul)
Availability Zone: ap-northeast-2a (기본값)

⚠️ 중요: 서울 리전 선택 필수! (가장 빠른 속도)
```

#### 2-3. 플랫폼 및 블루프린트 선택

```
Select a platform:
→ ⭕ Linux/Unix (선택됨)

Select a blueprint:
→ OS Only 탭 선택
→ Ubuntu 22.04 LTS 선택

⚠️ Apps + OS가 아닌 OS Only를 선택하세요!
```

#### 2-4. Launch script (선택 사항)

```
Add launch script (Optional)
→ 비워두기 (나중에 수동으로 설치)

또는 아래 스크립트 붙여넣기 (자동 설치):
```

```bash
#!/bin/bash
apt-get update
apt-get install -y git python3.11 python3.11-venv
```

#### 2-5. SSH 키 페어 선택

```
Change SSH key pair:
→ Default 선택

⚠️ 첫 사용이라면 "Download" 버튼 클릭!
→ LightsailDefaultKey-ap-northeast-2.pem 저장
→ 안전한 곳에 보관 (이 파일 없으면 SSH 접속 불가!)
```

#### 2-6. 네트워킹 설정 (중요!)

**⚠️ IPv4 vs IPv6 vs Dual-stack 선택:**

```
Networking:
→ ⭕ Dual-stack (IPv4 and IPv6) 선택

중요!
- IPv6 only: IPv4 고정 IP 사용 불가 ❌
- IPv4 only: 구형, 추천 안 함 ❌
- Dual-stack: IPv4 + IPv6 둘 다 지원 ✅ (이것 선택!)

⚠️ Dual-stack은 $5/월부터 시작합니다!
```

**왜 Dual-stack이 필요한가?**

- 고정 IP는 **IPv4만 지원**
- 프론트엔드(GitHub Pages)는 IPv4 필요
- IPv6 only 선택 시 고정 IP 할당 불가!

#### 2-7. 인스턴스 플랜 선택

```
Choose your instance plan:

⚠️ Dual-stack 사용 시 최소 플랜:
→ $5.00 USD 플랜 선택 (Dual-stack 지원)
   1 GB RAM
   1 vCPU
   40 GB SSD
   2 TB transfer

⚠️ $3.50 플랜은 IPv6 only라서 고정 IP 사용 불가!
⚠️ 고정 IP 사용하려면 최소 $5 플랜 필요!
```

**비용 정리:**

- IPv6 only + $3.50/월 = 고정 IP 불가 ❌
- Dual-stack + $5/월 = 고정 IP 가능 ✅ (권장)

#### 2-8. 인스턴스 이름 및 태그

```
Identify your instance:
→ satellite-backend

Tags (Optional):
→ Key: Project, Value: Satellite-Vehicle-Tracker (선택 사항)
```

#### 2-9. 인스턴스 생성

```
→ "Create instance" 버튼 클릭 (주황색)

생성 시간: 약 1-2분
상태: Pending → Running
```

### 3단계: 인스턴스 실행 확인

1. **Lightsail 홈페이지에서 인스턴스 확인**

   - 이름: satellite-backend
   - 상태: ✅ Running (초록색)
   - IP: 공용 IP 표시 (예: 13.125.123.45)

2. **⚠️ 이 IP는 임시입니다!**
   - 인스턴스 재시작 시 변경됨
   - 다음 단계에서 고정 IP 할당 필수!

---

### 4단계: 고정 IP 할당 (매우 중요!)

#### 왜 고정 IP가 필요한가?

기본 공용 IP는 인스턴스 재시작 시 변경됩니다!
→ 프론트엔드가 백엔드를 찾지 못함
→ **고정 IP 필수!**

#### 고정 IP 할당 방법

1. **Lightsail 홈 → 인스턴스 (satellite-backend) 클릭**

2. **"Networking" 탭 클릭**

   - 화면 상단 메뉴

3. **"Create static IP" 버튼 클릭**

   - IPv4 Networking 섹션

4. **고정 IP 설정:**

   ```
   Static IP location: ap-northeast-2 (자동 선택됨)

   Attach to an instance: satellite-backend (선택)

   Identify your static IP:
   → satellite-backend-ip
   ```

5. **"Create" 버튼 클릭**

6. **✅ 성공! 고정 IP 할당 완료**
   ```
   Static IP: 3.38.75.221 (할당 받음)
   Status: Attached
   Instance: satellite-backend
   ```

#### ⚠️ 중요: 고정 IP 메모하기

```
📝 메모장에 기록:
고정 IP: 3.38.75.221 (할당 받음)

이 IP는:
- IPv4 주소 (Dual-stack 플랜에서만 가능)
- 절대 변경되지 않음
- 프론트엔드 연결에 사용
- DNS 도메인 연결 가능
```

#### 고정 IP 비용

- **인스턴스 연결 시:** 무료!
- **미연결 시:** $0.005/시간 (약 $3.6/월)
- **주의:** 인스턴스 삭제 전 고정 IP도 함께 삭제해야 과금 없음

---

### 5단계: 방화벽 설정

Lightsail 인스턴스는 기본적으로 SSH(22)만 허용됩니다.
HTTP(80) 포트를 열어야 브라우저에서 접속 가능!

#### 방화벽 규칙 추가

1. **인스턴스 페이지 → "Networking" 탭**

2. **"IPv4 Firewall" 섹션에서 "Add rule" 클릭**

3. **HTTP 포트 열기:**

   ```
   Application: HTTP
   Protocol: TCP
   Port or range: 80
   Restricted to IP address: (비워두기 - 모든 IP 허용)
   ```

   → "Create" 클릭

4. **HTTPS 포트 열기 (향후 SSL 인증서용):**
   ```
   Application: HTTPS
   Protocol: TCP
   Port or range: 443
   Restricted to IP address: (비워두기)
   ```
   → "Create" 클릭

#### ✅ 최종 방화벽 규칙 확인

```
Rule          Application  Protocol  Port range   Source
-------------------------------------------------------------
SSH           SSH          TCP       22           0.0.0.0/0
HTTP          Custom       TCP       80           0.0.0.0/0
HTTPS         Custom       TCP       443          0.0.0.0/0
```

#### 보안 팁

- SSH(22)는 기본 허용, 변경 불필요
- HTTP(80) 필수 (Nginx가 이 포트 사용)
- HTTPS(443)는 나중에 SSL 인증서 설정 시 사용

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
curl http://3.38.75.221/api/health

# 응답 예시:
# {"status":"healthy","timestamp":"2025-10-30T06:15:02.408707","services":{"abandoned_vehicle_detector":"ready","pdf_processor":"ready"}}

# 2. 방치 차량 데이터 확인
curl http://3.38.75.221/api/abandoned-vehicles

# 3. API 문서 확인 (브라우저에서)
# http://Y3.38.75.221/docs
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

| 항목            | AWS Lightsail  | ngrok                 | Render                   |
| --------------- | -------------- | --------------------- | ------------------------ |
| **비용**        | $5/월          | 무료 (제한적)         | 무료 (512MB)             |
| **메모리**      | 1GB RAM        | 로컬 PC 사양          | 512MB RAM                |
| **안정성**      | ⭐⭐⭐⭐⭐     | ⭐⭐⭐ (로컬 PC 필요) | ⭐⭐⭐⭐ (타임아웃 이슈) |
| **고정 IP**     | ✅ IPv4 무료   | ❌ URL 변경됨         | ✅ 고정 URL              |
| **설정 난이도** | 쉬움           | 매우 쉬움             | 쉬움                     |
| **컴퓨터 켜둠** | 불필요         | 필요 ❌               | 불필요                   |
| **SQLite 저장** | ✅ 영구 (40GB) | ✅ 영구               | ❌ 휘발성                |
| **SSH 접속**    | ✅ 가능        | ❌ 불가               | ❌ 불가                  |
| **스케일업**    | ✅ 쉬움        | ❌ 불가               | ⚠️ 유료                  |
| **IPv4 지원**   | ✅ Dual-stack  | ✅                    | ✅                       |

**결론:** Lightsail $5/월 플랜이 장기적으로 가장 안정적이고 비용 효율적입니다.

### 총 비용 비교

```
옵션 1: Lightsail + SQLite
- Lightsail $5/월
- 합계: $5/월 ✅ (추천! RDS 불필요)

옵션 2: Lightsail + RDS (프로덕션 대규모)
- Lightsail $5/월
- RDS PostgreSQL $14/월
- 합계: $19/월 (대규모 트래픽 시)

옵션 3: ngrok (무료)
- 비용: $0
- 단점: 컴퓨터 24/7 켜둬야 함, 전기료, URL 변경

옵션 4: Render (무료)
- 비용: $0
- 단점: 타임아웃 이슈, SQLite 휘발성
```

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
