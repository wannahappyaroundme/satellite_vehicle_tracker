# 더미 데이터 생성 및 확인 가이드

## 개요

장기 방치 차량 탐지 시스템의 모든 기능을 테스트할 수 있도록 **36대의 더미 차량 데이터**를 생성했습니다.

## 데이터 특징

### 차량 구성
- **총 36대** (+ 기존 데이터 포함 시 49대)
- **소형차 (small-vehicle)**: 25대 (69.4%)
- **대형차 (large-vehicle)**: 7대 (19.4%)
- **트럭 (truck)**: 4대 (11.1%)

### 위험도 분포
- **CRITICAL** (95%+ 유사도, 3년+ 방치): 6대 (16.7%)
- **HIGH** (90%+ 유사도, 2년+ 방치): 13대 (36.1%)
- **MEDIUM** (85%+ 유사도): 11대 (30.6%)
- **LOW** (85% 미만): 6대 (16.7%)

### 지역 분포
전국 주요 15개 도시에 분산:
- 서울 (강남구, 종로구, 마포구)
- 부산 (해운대구, 부산진구)
- 대구, 인천, 광주, 대전, 울산
- 경기도 (수원, 성남, 고양)
- 제주, 강원 춘천

## 사용 방법

### 1. 더미 데이터 생성 (로컬)

```bash
# backend 디렉토리로 이동
cd /Users/kyungsbook/Desktop/satellite_project/backend

# 더미 데이터 생성 스크립트 실행
python seed_dummy_data.py
```

**출력 예시:**
```
============================================================
장기 방치 차량 더미 데이터 생성 시작
============================================================

총 36대의 차량 데이터 생성 완료

[차량 타입별 분포]
  - small-vehicle: 25대 (69.4%)
  - large-vehicle: 7대 (19.4%)
  - truck: 4대 (11.1%)

✅ 새로 삽입된 데이터: 36개
✅ 총 데이터: 49개
```

### 2. 데이터 확인

```bash
# DB에 저장된 데이터 확인
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

[최신 데이터 5개 샘플]

1. [VH202511030033] 회색 기아 포터 (화물차)
   위치: 울산 남구
   유사도: 89.27% (위험도: MEDIUM)
   연도: 2021 → 2024 (3년 차이)
```

### 3. 로컬 테스트

```bash
# 터미널 1: FastAPI 서버 시작
cd backend
python fastapi_app.py

# 터미널 2: 프론트엔드 시작
cd frontend
npm start

# 브라우저에서 확인
# http://localhost:3000
```

### 4. AWS Lightsail 배포

Lightsail SSH에 접속 후:

```bash
# 1. 프로젝트 디렉토리로 이동
cd /home/ubuntu/satellite_vehicle_tracker/backend

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 더미 데이터 생성 스크립트 업로드 (로컬에서 scp로 전송)
# 로컬 터미널에서:
scp -i LightsailDefaultKey.pem seed_dummy_data.py ubuntu@3.38.75.221:/home/ubuntu/satellite_vehicle_tracker/backend/

# 4. Lightsail SSH에서 스크립트 실행
python seed_dummy_data.py

# 5. 서비스 재시작
sudo supervisorctl restart satellite-backend

# 6. 확인
curl http://localhost:8000/api/abandoned-vehicles | jq '.[:3]'
```

## 데이터 구조

각 차량 데이터에는 다음 정보가 포함됩니다:

```json
{
  "id": 47,
  "vehicle_id": "VH202511030033",
  "latitude": 35.547457,
  "longitude": 129.333262,
  "city": "울산",
  "district": "남구",
  "address": "울산 남구",
  "vehicle_type": "truck",
  "similarity_score": 0.8927,
  "similarity_percentage": 89.27,
  "risk_level": "MEDIUM",
  "years_difference": 3,
  "first_detected": "2025-11-03T22:14:44.479430",
  "last_detected": "2025-11-03T22:14:44.479430",
  "detection_count": 5,
  "status": "DETECTED",
  "bbox": {
    "x": 453,
    "y": 198,
    "w": 95,
    "h": 65
  },
  "metadata": {
    "year1": 2021,
    "year2": 2024,
    "description": "회색 기아 포터 (화물차)",
    "confidence": 0.8935
  }
}
```

## 프론트엔드에서 확인할 수 있는 기능

### 1. 메인 탐지 페이지
- 지도에 49개 차량 마커 표시
- 위험도별 색상 구분 (빨강/주황/노랑/파랑)
- 클릭 시 차량 상세 정보 팝업

### 2. 통계 대시보드
- 총 차량 수: 49대
- 위험도별 분포 차트
- 지역별 분포 차트 (상위 10개)
- 차량 타입별 파이 차트

### 3. 관리자 대시보드
- 차량 리스트 테이블 (필터링/정렬)
- 상태 관리 (DETECTED → INVESTIGATING → VERIFIED → RESOLVED)
- 검증 노트 작성
- CSV 다운로드

### 4. 필터링
- 위험도별 필터 (CRITICAL/HIGH/MEDIUM/LOW)
- 차량 타입별 필터 (소형/대형/트럭)
- 지역별 필터 (시/도, 구/군)
- 상태별 필터

## 기대 효과

더미 데이터를 통해 다음을 확인할 수 있습니다:

1. ✅ **지도 표시**: 전국 15개 도시에 49개 마커 표시
2. ✅ **통계 차트**: 위험도/지역/타입별 분포 시각화
3. ✅ **필터링**: 다양한 조건으로 데이터 필터링
4. ✅ **관리 기능**: 상태 변경, 노트 작성, CSV 다운로드
5. ✅ **성능 테스트**: 49개 데이터로 로딩 속도 확인

## 데이터 초기화

기존 데이터를 모두 삭제하고 새로 시작하려면:

```bash
# SQLite DB 백업
cp backend/satellite_tracker.db backend/satellite_tracker.db.backup

# DB 파일 삭제
rm backend/satellite_tracker.db

# 새로 생성
python backend/seed_dummy_data.py
```

## 문제 해결

### 에러: "database is locked"

```bash
# SQLite DB 잠금 해제
fuser -k backend/satellite_tracker.db

# 또는 서버 재시작
sudo supervisorctl restart satellite-backend
```

### 데이터가 표시되지 않음

```bash
# 1. DB 확인
python test_db_data.py

# 2. API 확인
curl http://localhost:8000/api/abandoned-vehicles

# 3. 프론트엔드 콘솔 확인 (F12 → Console)
# CORS 에러 또는 네트워크 에러 확인
```

## 추가 참고

- [AWS_LIGHTSAIL_DEPLOYMENT.md](./AWS_LIGHTSAIL_DEPLOYMENT.md) - Lightsail 배포 가이드
- [README.md](./README.md) - 프로젝트 전체 문서

---

**Made with ❤️ for safer and better cities**
