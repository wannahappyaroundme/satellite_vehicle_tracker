# 🚀 더미 데이터 배포 완벽 가이드

## 3가지 배포 방법 중 선택하세요

### ⭐ 방법 1: 브라우저 SSH (가장 쉬움, SSH 키 불필요)

**추천:** SSH 키 파일이 없거나 처음 배포하는 경우

👉 **[deploy_browser_ssh.md](./deploy_browser_ssh.md)** 참고

**단계:**
1. Lightsail 콘솔 → "Connect using SSH" 클릭
2. 스크립트 복사 붙여넣기
3. 실행
4. 완료!

**소요 시간:** 2분

---

### 🚀 방법 2: 원클릭 자동 배포 (SSH 키 있는 경우)

**추천:** SSH 키가 있고 빠르게 배포하고 싶은 경우

```bash
./quick_deploy.sh
```

**자동으로 실행:**
- ✅ Lightsail SSH 접속
- ✅ 스크립트 업로드
- ✅ 36대 차량 데이터 생성
- ✅ 서비스 재시작
- ✅ 배포 확인

**소요 시간:** 30초

---

### 📦 방법 3: Git 커밋 포함 전체 배포

**추천:** 코드 변경도 함께 배포하고 싶은 경우

```bash
./deploy_dummy_data.sh
```

**자동으로 실행:**
- 방법 2의 모든 작업 +
- ✅ Git 커밋 및 푸시
- ✅ GitHub Actions 트리거
- ✅ GitHub Pages 자동 배포

**소요 시간:** 3분 (GitHub Actions 포함)

---

## 배포 후 확인

### 1. API 응답 확인 (즉시)

```bash
curl https://standings-classification-easy-textbook.trycloudflare.com/api/abandoned-vehicles | jq 'length'
```

**예상 결과:** `49` (기존 13 + 새로운 36)

### 2. GitHub Pages 확인 (즉시)

**URL:** https://wannahappyaroundme.github.io/satellite_vehicle_tracker/

**확인 사항:**
- ✅ 지도에 49개 마커 표시
- ✅ 통계 대시보드: 위험도/지역/타입별 차트
- ✅ 관리자 대시보드: 49개 차량 테이블

### 3. 상세 통계 확인 (Lightsail SSH)

```bash
cd /home/ubuntu/satellite_vehicle_tracker/backend
source venv/bin/activate
python test_db_data.py
```

**예상 출력:**
```
총 차량 수: 49개

[위험도별 분포]
  CRITICAL: 7대 (14.3%)
  HIGH: 25대 (51.0%)
  MEDIUM: 11대 (22.4%)
  LOW: 6대 (12.2%)

[차량 타입별 분포]
  small-vehicle: 25대 (51.0%)
  large-vehicle: 7대 (14.3%)
  truck: 4대 (8.2%)
```

---

## 데이터 구성

### 차량 타입 (70% 소형차)
- **소형차 (small-vehicle):** 25대 (69.4%)
- **대형차 (large-vehicle):** 7대 (19.4%)
- **트럭 (truck):** 4대 (11.1%)

### 위험도 분포
- **CRITICAL** (95%+ 유사도, 3년+ 방치): ~15%
- **HIGH** (90%+ 유사도, 2년+ 방치): ~35%
- **MEDIUM** (85%+ 유사도): ~30%
- **LOW** (85% 미만): ~15%

### 지역 분포
전국 15개 도시에 분산:
- 서울 3개구 (강남, 종로, 마포)
- 부산 2개구 (해운대, 부산진)
- 대구, 인천, 광주, 대전, 울산
- 경기 3개시 (수원, 성남, 고양)
- 제주, 강원 춘천

---

## 생성되는 파일

### Lightsail 서버

```
/home/ubuntu/satellite_vehicle_tracker/backend/
├── seed_dummy_data.py      # 더미 데이터 생성 스크립트
├── test_db_data.py          # 데이터 확인 스크립트
└── satellite_tracker.db     # SQLite 데이터베이스 (49개 차량)
```

### 로컬 프로젝트

```
/Users/kyungsbook/Desktop/satellite_project/
├── backend/
│   ├── seed_dummy_data.py   # 더미 데이터 생성 스크립트
│   └── test_db_data.py      # 데이터 확인 스크립트
├── deploy_dummy_data.sh     # Git 커밋 포함 전체 배포
├── quick_deploy.sh          # 원클릭 배포
├── deploy_browser_ssh.md    # 브라우저 SSH 가이드
├── DUMMY_DATA_GUIDE.md      # 더미 데이터 상세 가이드
├── DEPLOYMENT_QUICK_START.md # 빠른 시작 가이드
└── README_DEPLOY.md         # 이 파일
```

---

## 문제 해결

### SSH 키를 찾을 수 없음

```bash
# SSH 키 위치 확인
find ~ -name "LightsailDefaultKey.pem" 2>/dev/null

# 없으면 브라우저 SSH 사용
# → deploy_browser_ssh.md 참고
```

### 데이터가 표시되지 않음

```bash
# 1. Lightsail SSH에서 데이터 개수 확인
cd /home/ubuntu/satellite_vehicle_tracker/backend
source venv/bin/activate
python3 -c "from database import get_db; from models_sqlalchemy import AbandonedVehicle; db=next(get_db()); print(f'{db.query(AbandonedVehicle).count()}개')"

# 2. API 테스트
curl http://localhost:8000/api/abandoned-vehicles | jq '.[0]'

# 3. 서비스 상태 확인
sudo supervisorctl status satellite-backend
```

### 서비스 재시작 실패

```bash
# 에러 로그 확인
sudo tail -50 /var/log/satellite-backend.err.log

# 수동 재시작
sudo supervisorctl restart satellite-backend

# 강제 재시작
sudo supervisorctl stop satellite-backend
sleep 3
sudo supervisorctl start satellite-backend
```

---

## 데이터 초기화 (전체 삭제)

**⚠️ 주의: 모든 데이터가 삭제됩니다!**

```bash
# Lightsail SSH에서
cd /home/ubuntu/satellite_vehicle_tracker/backend

# 1. 백업
cp satellite_tracker.db satellite_tracker.db.backup

# 2. 삭제
rm satellite_tracker.db

# 3. 서비스 재시작 (자동으로 빈 DB 생성)
sudo supervisorctl restart satellite-backend

# 4. 새로 생성
source venv/bin/activate
python seed_dummy_data.py
```

---

## 추가 데이터 생성 (36대 더)

```bash
# 스크립트를 다시 실행하면 36대가 추가됩니다
python seed_dummy_data.py

# 총 85개 (기존 49 + 새로운 36)
```

---

## 체크리스트

배포 전 확인사항:

- [ ] Lightsail 인스턴스 실행 중
- [ ] Cloudflare Tunnel 실행 중 (`sudo systemctl status cloudflared`)
- [ ] Supervisor 실행 중 (`sudo supervisorctl status`)
- [ ] 배포 방법 선택 (브라우저 SSH / 원클릭 / Git 포함)
- [ ] 배포 실행
- [ ] API 응답 확인 (49개)
- [ ] GitHub Pages 확인
- [ ] 통계 대시보드 확인

---

## 관련 문서

- **[deploy_browser_ssh.md](./deploy_browser_ssh.md)** - 브라우저 SSH 상세 가이드
- **[DUMMY_DATA_GUIDE.md](./DUMMY_DATA_GUIDE.md)** - 더미 데이터 상세 설명
- **[DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md)** - 빠른 시작 가이드
- **[AWS_LIGHTSAIL_DEPLOYMENT.md](./AWS_LIGHTSAIL_DEPLOYMENT.md)** - Lightsail 초기 설정

---

## 성공 예시

```
✅ Lightsail 배포 완료!

🌐 Cloudflare Tunnel로 즉시 확인:
   https://standings-classification-easy-textbook.trycloudflare.com/api/abandoned-vehicles

📱 GitHub Pages:
   https://wannahappyaroundme.github.io/satellite_vehicle_tracker/

📊 데이터:
   총 49대 (소형차 25대, 대형차 7대, 트럭 4대)
   CRITICAL 7대, HIGH 25대, MEDIUM 11대, LOW 6대

✅ 완료!
```

---

**Made with ❤️ for safer and better cities**

**The best for a better world**
