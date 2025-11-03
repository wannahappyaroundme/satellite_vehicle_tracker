# 🚀 원클릭 배포 가이드

## Lightsail에 더미 데이터 36대 배포하기

### 방법 1: 원클릭 배포 (가장 쉬움!) ⭐

```bash
./quick_deploy.sh
```

**이것만 실행하면 끝!** 자동으로:
1. ✅ Lightsail SSH 접속
2. ✅ 더미 데이터 생성 스크립트 업로드
3. ✅ 36대 차량 데이터 DB에 저장
4. ✅ FastAPI 서비스 재시작
5. ✅ 배포 확인

**실행 시간:** 약 30초

---

### 방법 2: 전체 자동 배포 (Git 커밋 포함)

```bash
./deploy_dummy_data.sh
```

위 작업 + 추가로:
1. ✅ Git 커밋 및 푸시
2. ✅ GitHub Actions 자동 트리거
3. ✅ GitHub Pages 배포

**실행 시간:** 약 3분 (GitHub Actions 포함)

---

### 방법 3: 수동 배포 (단계별)

#### 3-1. 스크립트 전송

```bash
scp -i ~/LightsailDefaultKey.pem \
    backend/seed_dummy_data.py \
    ubuntu@3.38.75.221:/home/ubuntu/satellite_vehicle_tracker/backend/
```

#### 3-2. Lightsail SSH 접속

```bash
ssh -i ~/LightsailDefaultKey.pem ubuntu@3.38.75.221
```

#### 3-3. 스크립트 실행

```bash
cd /home/ubuntu/satellite_vehicle_tracker/backend
source venv/bin/activate
python seed_dummy_data.py
```

#### 3-4. 서비스 재시작

```bash
sudo supervisorctl restart satellite-backend
```

#### 3-5. 확인

```bash
curl http://localhost:8000/api/abandoned-vehicles | jq 'length'
```

---

## 배포 후 확인

### 1️⃣ Cloudflare Tunnel API (즉시 확인)

```bash
curl https://standings-classification-easy-textbook.trycloudflare.com/api/abandoned-vehicles | jq 'length'
```

**예상 출력:** `49` (기존 13 + 새로운 36)

### 2️⃣ 브라우저에서 확인

**GitHub Pages:**
- https://wannahappyaroundme.github.io/satellite_vehicle_tracker/

**확인 사항:**
- ✅ 지도에 49개 마커 표시
- ✅ 통계 대시보드에서 위험도/타입별 차트 확인
- ✅ 관리자 대시보드에서 49개 차량 리스트 확인

### 3️⃣ 상세 통계 확인

```bash
# Lightsail SSH에서
python test_db_data.py
```

**출력 예시:**
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

## 문제 해결

### SSH 키를 찾을 수 없음

```bash
# SSH 키 위치 확인
ls ~/LightsailDefaultKey.pem

# 없으면 Lightsail 콘솔에서 다운로드
# Account → SSH keys → Download
```

### 서비스 재시작 실패

```bash
# Lightsail SSH에서
sudo supervisorctl status satellite-backend

# 에러 로그 확인
sudo tail -f /var/log/satellite-backend.err.log

# 수동 재시작
sudo supervisorctl restart satellite-backend
```

### 데이터가 표시되지 않음

```bash
# 1. DB 파일 확인
ls -lh /home/ubuntu/satellite_vehicle_tracker/backend/satellite_tracker.db

# 2. 데이터 개수 확인
cd /home/ubuntu/satellite_vehicle_tracker/backend
source venv/bin/activate
python -c "from database import get_db; from models_sqlalchemy import AbandonedVehicle; db=next(get_db()); print(f'{db.query(AbandonedVehicle).count()}개')"

# 3. API 테스트
curl http://localhost:8000/api/abandoned-vehicles | jq '.[0]'
```

---

## 데이터 초기화 (필요 시)

**⚠️ 주의: 모든 데이터가 삭제됩니다!**

```bash
# Lightsail SSH에서
cd /home/ubuntu/satellite_vehicle_tracker/backend

# 백업
cp satellite_tracker.db satellite_tracker.db.backup

# 삭제
rm satellite_tracker.db

# 새로 생성
python seed_dummy_data.py

# 서비스 재시작
sudo supervisorctl restart satellite-backend
```

---

## 추가 배포

### 더 많은 데이터 추가 (36대 더)

```bash
# quick_deploy.sh를 다시 실행하면 36대가 추가됩니다
./quick_deploy.sh

# 총 85개 (기존 49 + 새로운 36)
```

### GitHub Pages 수동 배포

```bash
# 변경사항 커밋
git add .
git commit -m "Update data"
git push origin main

# GitHub Actions가 자동으로 배포 (2-3분 소요)
# https://github.com/wannahappyaroundme/satellite_vehicle_tracker/actions
```

---

## 배포 체크리스트

- [ ] SSH 키 준비됨 (`~/LightsailDefaultKey.pem`)
- [ ] Lightsail 인스턴스 실행 중
- [ ] Cloudflare Tunnel 실행 중 (`sudo systemctl status cloudflared`)
- [ ] `./quick_deploy.sh` 실행
- [ ] API 응답 확인 (49개 차량)
- [ ] GitHub Pages에서 지도 확인
- [ ] 통계 대시보드 확인

---

## 성공 메시지 예시

```
✅ Lightsail 배포 완료!

🌐 Cloudflare Tunnel로 즉시 확인:
   https://standings-classification-easy-textbook.trycloudflare.com/api/abandoned-vehicles

📱 GitHub Pages는 자동으로 최신 데이터를 표시합니다:
   https://wannahappyaroundme.github.io/satellite_vehicle_tracker/

✅ 완료!
```

---

**Made with ❤️ for safer and better cities**
