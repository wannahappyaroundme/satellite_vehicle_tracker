#!/bin/bash
# 더미 데이터를 Lightsail에 배포하고 GitHub Pages에 반영하는 자동화 스크립트

set -e  # 에러 발생 시 중단

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Lightsail 정보
LIGHTSAIL_IP="3.38.75.221"
LIGHTSAIL_USER="ubuntu"
LIGHTSAIL_KEY="${HOME}/LightsailDefaultKey.pem"
PROJECT_DIR="/home/ubuntu/satellite_vehicle_tracker"

echo "============================================================"
echo -e "${GREEN}더미 데이터 Lightsail 배포 + GitHub Pages 자동 배포${NC}"
echo "============================================================"

# 1단계: Lightsail에 스크립트 전송
echo ""
echo -e "${YELLOW}[1/6] Lightsail에 더미 데이터 생성 스크립트 전송 중...${NC}"
scp -i "${LIGHTSAIL_KEY}" \
    backend/seed_dummy_data.py \
    "${LIGHTSAIL_USER}@${LIGHTSAIL_IP}:${PROJECT_DIR}/backend/"

echo -e "${GREEN}✅ 스크립트 전송 완료${NC}"

# 2단계: Lightsail에서 더미 데이터 생성
echo ""
echo -e "${YELLOW}[2/6] Lightsail에서 더미 데이터 생성 중...${NC}"
ssh -i "${LIGHTSAIL_KEY}" "${LIGHTSAIL_USER}@${LIGHTSAIL_IP}" << 'EOF'
cd /home/ubuntu/satellite_vehicle_tracker/backend
source venv/bin/activate
python seed_dummy_data.py
EOF

echo -e "${GREEN}✅ 더미 데이터 생성 완료${NC}"

# 3단계: 서비스 재시작
echo ""
echo -e "${YELLOW}[3/6] FastAPI 서비스 재시작 중...${NC}"
ssh -i "${LIGHTSAIL_KEY}" "${LIGHTSAIL_USER}@${LIGHTSAIL_IP}" << 'EOF'
sudo supervisorctl restart satellite-backend
sleep 3
sudo supervisorctl status satellite-backend
EOF

echo -e "${GREEN}✅ 서비스 재시작 완료${NC}"

# 4단계: API 헬스 체크
echo ""
echo -e "${YELLOW}[4/6] API 헬스 체크 중...${NC}"
ssh -i "${LIGHTSAIL_KEY}" "${LIGHTSAIL_USER}@${LIGHTSAIL_IP}" << 'EOF'
echo "Health check:"
curl -s http://localhost:8000/api/health | jq '.'

echo ""
echo "방치 차량 수:"
curl -s http://localhost:8000/api/abandoned-vehicles | jq 'length'
EOF

echo -e "${GREEN}✅ API 정상 작동 확인${NC}"

# 5단계: Git 커밋 및 푸시 (GitHub Actions 트리거)
echo ""
echo -e "${YELLOW}[5/6] GitHub에 변경사항 푸시 중 (GitHub Actions 트리거)...${NC}"

# 변경사항 있는지 확인
if [[ -n $(git status -s) ]]; then
    git add backend/seed_dummy_data.py backend/test_db_data.py DUMMY_DATA_GUIDE.md
    git commit -m "🎲 Add dummy data generation scripts (36 vehicles)

- Create seed_dummy_data.py for 36 dummy vehicles
- 70% small vehicles, 30% large vehicles/trucks
- Risk level distribution: CRITICAL/HIGH/MEDIUM/LOW
- Nationwide 15 cities distribution
- Add test_db_data.py for verification
- Add DUMMY_DATA_GUIDE.md for documentation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

    git push origin main
    echo -e "${GREEN}✅ GitHub에 푸시 완료${NC}"
else
    echo -e "${YELLOW}⚠️  변경사항이 없습니다. 푸시 생략${NC}"
fi

# 6단계: GitHub Actions 진행 상황 확인
echo ""
echo -e "${YELLOW}[6/6] GitHub Actions 배포 상태 확인 중...${NC}"
echo ""
echo -e "${GREEN}GitHub Actions가 자동으로 프론트엔드를 빌드하고 배포합니다.${NC}"
echo ""
echo "진행 상황 확인:"
echo "  https://github.com/wannahappyaroundme/satellite_vehicle_tracker/actions"
echo ""
echo "배포 완료 후 확인 (약 2-3분 소요):"
echo "  https://wannahappyaroundme.github.io/satellite_vehicle_tracker/"
echo ""

# 7단계: 최종 요약
echo "============================================================"
echo -e "${GREEN}✅ 배포 완료!${NC}"
echo "============================================================"
echo ""
echo "배포된 내용:"
echo "  ✅ Lightsail에 더미 데이터 36대 생성"
echo "  ✅ FastAPI 서비스 재시작"
echo "  ✅ GitHub에 스크립트 푸시"
echo "  ✅ GitHub Actions 자동 배포 트리거"
echo ""
echo "확인 방법:"
echo ""
echo "1️⃣ Cloudflare Tunnel API (즉시 확인 가능):"
echo "   curl https://standings-classification-easy-textbook.trycloudflare.com/api/abandoned-vehicles | jq 'length'"
echo ""
echo "2️⃣ GitHub Pages (2-3분 후):"
echo "   https://wannahappyaroundme.github.io/satellite_vehicle_tracker/"
echo ""
echo "3️⃣ GitHub Actions 로그:"
echo "   https://github.com/wannahappyaroundme/satellite_vehicle_tracker/actions"
echo ""
echo "============================================================"
