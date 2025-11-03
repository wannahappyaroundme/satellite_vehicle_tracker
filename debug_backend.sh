#!/bin/bash
# 백엔드 에러 로그 확인 스크립트

echo "=== 백엔드 에러 로그 확인 ==="
sudo tail -50 /var/log/satellite-backend.err.log

echo ""
echo "=== 백엔드 출력 로그 확인 ==="
sudo tail -50 /var/log/satellite-backend.out.log

echo ""
echo "=== Supervisor 프로세스 상태 ==="
sudo supervisorctl status

echo ""
echo "=== 수동으로 FastAPI 실행 테스트 ==="
cd /home/ubuntu/satellite_vehicle_tracker/backend
source venv/bin/activate
python -c "from fastapi_app import app; print('Import successful!')"
