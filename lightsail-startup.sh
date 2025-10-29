#!/bin/bash
# AWS Lightsail 배포 스크립트
# 인스턴스 생성 후 첫 실행 시 사용

set -e

echo "======================================"
echo "🚀 AWS Lightsail 배포 시작"
echo "======================================"

# 1. 시스템 업데이트
echo "1️⃣ 시스템 업데이트..."
sudo apt-get update
sudo apt-get upgrade -y

# 2. Python 3.11 설치
echo "2️⃣ Python 3.11 설치..."
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev

# 3. 시스템 의존성 설치
echo "3️⃣ 시스템 의존성 설치..."
sudo apt-get install -y \
    poppler-utils \
    git \
    nginx \
    supervisor

# 4. 프로젝트 클론
echo "4️⃣ 프로젝트 클론..."
cd /home/ubuntu
git clone https://github.com/wannahappyaroundme/satellite_vehicle_tracker.git
cd satellite_vehicle_tracker/backend

# 5. Python 가상환경 생성
echo "5️⃣ Python 가상환경 생성..."
python3.11 -m venv venv
source venv/bin/activate

# 6. Python 패키지 설치
echo "6️⃣ Python 패키지 설치..."
pip install --upgrade pip
pip install -r requirements.txt

# 7. 환경 변수 설정
echo "7️⃣ 환경 변수 설정..."
cat > .env << EOF
DATABASE_URL=sqlite:///./satellite_tracker.db
FASTAPI_PORT=8000
PDF_DPI=300
ABANDONED_SIMILARITY_THRESHOLD=0.90
EOF

# 8. Supervisor 설정 (자동 재시작)
echo "8️⃣ Supervisor 설정..."
sudo tee /etc/supervisor/conf.d/satellite-backend.conf > /dev/null << EOF
[program:satellite-backend]
directory=/home/ubuntu/satellite_vehicle_tracker/backend
command=/home/ubuntu/satellite_vehicle_tracker/backend/venv/bin/uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/satellite-backend.err.log
stdout_logfile=/var/log/satellite-backend.out.log
environment=PATH="/home/ubuntu/satellite_vehicle_tracker/backend/venv/bin"
EOF

# 9. Nginx 설정 (리버스 프록시)
echo "9️⃣ Nginx 설정..."
sudo tee /etc/nginx/sites-available/satellite-backend > /dev/null << EOF
server {
    listen 80;
    server_name _;

    # CORS 헤더
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # OPTIONS 요청 처리
        if (\$request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization';
            add_header 'Content-Length' 0;
            add_header 'Content-Type' 'text/plain';
            return 204;
        }
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/satellite-backend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# 10. 서비스 시작
echo "🔟 서비스 시작..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start satellite-backend
sudo systemctl restart nginx

echo ""
echo "======================================"
echo "✅ 배포 완료!"
echo "======================================"
echo ""
echo "📍 백엔드 API: http://$(curl -s ifconfig.me)/api/health"
echo "📍 API 문서: http://$(curl -s ifconfig.me)/docs"
echo ""
echo "🔍 로그 확인:"
echo "  sudo tail -f /var/log/satellite-backend.out.log"
echo ""
echo "🔄 서비스 재시작:"
echo "  sudo supervisorctl restart satellite-backend"
echo ""
