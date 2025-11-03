# Cloudflare Tunnel로 무료 HTTPS 설정하기

## 문제 상황

GitHub Pages(HTTPS)에서 AWS Lightsail(HTTP)로 API 요청 시 **Mixed Content Error** 발생:
```
Mixed Content: The page at 'https://wannahappyaroundme.github.io/...' was loaded over HTTPS,
but requested an insecure XMLHttpRequest endpoint 'http://3.38.75.221/api/...'
This request has been blocked
```

## 해결 방법: Cloudflare Tunnel (무료)

Cloudflare Tunnel을 사용하면:
- ✅ **무료 HTTPS** 자동 제공
- ✅ **무료 도메인** (예: `satellite-api.trycloudflare.com`)
- ✅ **인증서 관리 자동**
- ✅ **10분 내 설정 완료**

---

## 1단계: Cloudflare 계정 생성 (무료)

1. https://dash.cloudflare.com/sign-up 접속
2. 이메일 주소와 비밀번호 입력
3. 이메일 인증 완료

**비용:** 완전 무료 (Tunnel 기능은 Free 플랜에 포함)

---

## 2단계: Lightsail에 Cloudflared 설치

SSH로 Lightsail 인스턴스에 접속:

```bash
# 1. Lightsail SSH 접속
ssh -i LightsailDefaultKey.pem ubuntu@3.38.75.221

# 또는 Lightsail 콘솔에서 "Connect using SSH" 클릭
```

### Cloudflared 설치:

```bash
# 1. Cloudflared 다운로드 (Linux AMD64)
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# 2. 패키지 설치
sudo dpkg -i cloudflared-linux-amd64.deb

# 3. 설치 확인
cloudflared --version
# 출력 예시: cloudflared version 2024.x.x
```

---

## 3단계: Cloudflare Tunnel 생성

### 옵션 A: Cloudflare 대시보드 사용 (추천 - 쉬움)

1. **Cloudflare 대시보드 접속**
   - https://one.dash.cloudflare.com/

2. **Zero Trust 선택**
   - 좌측 메뉴에서 "Zero Trust" 클릭
   - 처음이라면 Free 플랜 선택 (카드 입력 불필요)

3. **Tunnel 생성**
   ```
   Networks → Tunnels → Create a tunnel

   Tunnel 이름: satellite-backend
   → Save tunnel
   ```

4. **Connector 설치**
   - 화면에 나오는 설치 명령어 복사 (자동 생성됨)
   - 예시:
   ```bash
   sudo cloudflared service install <YOUR_TOKEN>
   ```

   - Lightsail SSH에서 위 명령어 실행

5. **Public Hostname 설정**
   ```
   Public Hostname 탭 → Add a public hostname

   Subdomain: satellite-api (원하는 이름)
   Domain: (Cloudflare가 자동 제공하는 도메인 선택)
   Path: (비워두기)

   Service:
   Type: HTTP
   URL: localhost:8000

   → Save hostname
   ```

6. **✅ 완료!**
   - 생성된 URL: `https://satellite-api.trycloudflare.com` (예시)
   - 이 URL이 GitHub Pages에서 사용할 HTTPS API 주소입니다!

### 옵션 B: CLI로 빠른 테스트 (임시 URL, 테스트용)

Lightsail SSH에서:

```bash
# 임시 터널 생성 (빠른 테스트용)
cloudflared tunnel --url http://localhost:8000
```

출력 예시:
```
Your quick Tunnel has been created! Visit it at:
https://random-word-1234.trycloudflare.com
```

**주의:** 이 방법은 **임시 URL**이며, cloudflared 종료 시 URL이 사라집니다. 프로덕션에서는 **옵션 A** 사용 권장!

---

## 4단계: Cloudflared를 서비스로 등록 (자동 시작)

옵션 A를 사용했다면 이미 서비스로 등록되었습니다. 확인:

```bash
# 서비스 상태 확인
sudo systemctl status cloudflared

# 서비스가 실행 중이 아니면:
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

**자동 재시작 설정:**
- Supervisor처럼 Lightsail 재부팅 시 자동 실행
- 서비스 크래시 시 자동 재시작

---

## 5단계: Cloudflare Tunnel 작동 확인

### 로컬 백엔드 확인:

```bash
# Lightsail에서 로컬 백엔드 확인
curl http://localhost:8000/api/health
```

### Cloudflare Tunnel 확인:

```bash
# 생성된 HTTPS URL로 확인 (로컬에서 실행)
curl https://satellite-api.trycloudflare.com/api/health
```

**예상 출력:**
```json
{"status":"healthy","timestamp":"2025-11-03T09:00:00.000000","services":{"abandoned_vehicle_detector":"ready","pdf_processor":"ready"}}
```

✅ 이제 HTTPS로 API가 작동합니다!

---

## 6단계: 프론트엔드 환경 변수 업데이트

로컬 프로젝트에서:

### A. `.env.production` 파일 수정:

```bash
# frontend/.env.production
REACT_APP_API_URL=https://satellite-api.trycloudflare.com/api
REACT_APP_FASTAPI_URL=https://satellite-api.trycloudflare.com/api
```

### B. GitHub Actions 워크플로우 수정:

```yaml
# .github/workflows/gh-pages.yml
- name: Build
  run: |
    cd frontend
    npm run build
  env:
    REACT_APP_API_URL: https://satellite-api.trycloudflare.com/api
    REACT_APP_FASTAPI_URL: https://satellite-api.trycloudflare.com/api
```

**주의:** `satellite-api.trycloudflare.com`을 실제로 생성된 Cloudflare Tunnel URL로 교체하세요!

---

## 7단계: Git 커밋 및 배포

```bash
# 변경 사항 커밋
git add frontend/.env.production .github/workflows/gh-pages.yml
git commit -m "✨ Add HTTPS support via Cloudflare Tunnel

- Switch from HTTP (3.38.75.221) to HTTPS (Cloudflare Tunnel)
- Fix Mixed Content Error on GitHub Pages
- Update API URLs to use Cloudflare Tunnel endpoint

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# GitHub에 푸시 (자동 배포)
git push origin main
```

GitHub Actions가 자동으로:
1. 새로운 HTTPS URL로 프론트엔드 빌드
2. GitHub Pages에 배포

**배포 완료 시간:** 약 2-3분

---

## 8단계: 테스트

1. **GitHub Pages 접속**
   - https://wannahappyaroundme.github.io/satellite_vehicle_tracker/

2. **"방치 차량 표시" 버튼 클릭**
   - Network error가 사라지고 정상 작동!

3. **개발자 도구 확인** (F12)
   - Network 탭에서 `https://satellite-api.trycloudflare.com/api/...` 요청 확인
   - Status: 200 OK ✅

---

## Cloudflare Tunnel 관리

### Tunnel 상태 확인:

```bash
# Lightsail SSH
sudo systemctl status cloudflared
```

### Tunnel 재시작:

```bash
sudo systemctl restart cloudflared
```

### Tunnel 중지:

```bash
sudo systemctl stop cloudflared
```

### Tunnel 삭제:

1. Cloudflare 대시보드 → Tunnels
2. 해당 Tunnel 선택 → Delete

---

## 비용 비교

| 항목 | Cloudflare Tunnel | Let's Encrypt + 도메인 |
|------|-------------------|------------------------|
| **비용** | **$0 (무료)** | 도메인 $12/년 |
| **HTTPS** | ✅ 자동 | ✅ 자동 (certbot) |
| **도메인** | ✅ 무료 제공 | ❌ 구매 필요 |
| **설정 시간** | **10분** | 30분+ |
| **인증서 갱신** | ✅ 자동 | ✅ 자동 |
| **추천** | ✅ **개인 프로젝트** | 🏢 프로덕션 |

---

## 문제 해결

### 1. Cloudflared 설치 실패

```bash
# Ubuntu 22.04에서 권한 오류 시:
sudo apt-get update
sudo apt-get install -y debian-archive-keyring
sudo dpkg -i cloudflared-linux-amd64.deb
```

### 2. Tunnel 연결 실패

```bash
# 로그 확인
sudo journalctl -u cloudflared -f

# Cloudflared 재설치
sudo cloudflared service uninstall
sudo cloudflared service install <YOUR_TOKEN>
```

### 3. Lightsail 방화벽 이슈

Cloudflare Tunnel은 **outbound** 연결만 사용하므로 방화벽 설정 변경 불필요!
- HTTP(80) 포트는 그대로 유지
- Cloudflare가 Lightsail **내부에서** localhost:8000에 연결

### 4. GitHub Pages에서 여전히 에러 발생

브라우저 캐시 삭제:
- Chrome: `Ctrl+Shift+R` (Windows) / `Cmd+Shift+R` (Mac)
- 개발자 도구 → Application → Clear storage

---

## 커스텀 도메인 사용 (선택 사항)

자신의 도메인이 있다면:

1. **Cloudflare에 도메인 추가**
   - Cloudflare 대시보드 → Add a site
   - 도메인 입력 (예: `example.com`)

2. **DNS 레코드 자동 생성**
   - Tunnel 생성 시 자동으로 CNAME 레코드 추가됨

3. **프론트엔드 환경 변수 업데이트**
   ```bash
   REACT_APP_API_URL=https://api.example.com/api
   ```

---

## 다음 단계

1. ✅ **Cloudflare Tunnel 설정 완료**
2. ✅ **HTTPS로 API 제공**
3. ✅ **GitHub Pages에서 정상 작동**

**선택 사항:**
- 커스텀 도메인 연결
- Cloudflare Analytics 활성화
- Rate limiting 설정

---

**Made with ❤️ for safer and better cities**

**The best for a better world**
