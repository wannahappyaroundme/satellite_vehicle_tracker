#!/bin/bash
# Named Tunnel 설정 스크립트
# Lightsail SSH에서 실행하세요

echo "=== 1단계: 기존 Quick Tunnel 서비스 중지 ==="
sudo systemctl stop cloudflared-tunnel
sudo systemctl disable cloudflared-tunnel

echo ""
echo "=== 2단계: Named Tunnel 설치 (토큰 사용) ==="
echo "다음 명령어를 실행하세요:"
echo ""
echo "sudo cloudflared service install eyJhIjoiNDA4MjFlZjgzYTUwODk1MDhjYjlhMGRhZWM1ZTIyOTAiLCJ0IjoiY2M0ZTE0YTMtMTdkOC00NjBjLWFiNmUtNTA3ZTI4ZjYwNjE1IiwicyI6IllUUXhZMll4TmprdE56azRPQzAwWlRJNUxXSmtNRE10TWpnM01ESXpOVEUwTVdNMCJ9"
echo ""
echo "=== 3단계: 서비스 확인 ==="
echo "sudo systemctl status cloudflared"
echo ""
echo "=== 4단계: Cloudflare 대시보드에서 Public Hostname 추가 ==="
echo "https://one.dash.cloudflare.com/ → Networks → Tunnels → 생성한 터널 선택"
echo "→ Public Hostname 탭 → Add a public hostname"
echo ""
echo "설정:"
echo "  Subdomain: satellite-api (또는 원하는 이름)"
echo "  Domain: 드롭다운에서 선택 (trycloudflare.com 도메인)"
echo "  Service Type: HTTP"
echo "  URL: localhost:8000"
echo ""
echo "저장 후 생성된 URL (예: https://satellite-api-abc123.trycloudflare.com)을 확인하세요!"
