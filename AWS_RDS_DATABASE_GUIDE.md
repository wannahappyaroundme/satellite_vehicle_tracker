# AWS RDS 데이터베이스 설정 완벽 가이드

## 목차
1. [RDS란 무엇인가?](#rds란-무엇인가)
2. [언제 RDS를 사용해야 하나?](#언제-rds를-사용해야-하나)
3. [PostgreSQL RDS 생성 (단계별)](#postgresql-rds-생성-단계별)
4. [Lightsail에서 RDS 연결](#lightsail에서-rds-연결)
5. [환경 변수 설정](#환경-변수-설정)
6. [보안 설정](#보안-설정)
7. [비용 및 최적화](#비용-및-최적화)
8. [문제 해결](#문제-해결)

---

## RDS란 무엇인가?

**AWS RDS (Relational Database Service)**는 AWS가 관리하는 관계형 데이터베이스 서비스입니다.

### SQLite vs RDS 비교

| 특징 | SQLite | AWS RDS |
|------|--------|---------|
| **위치** | 로컬 파일 | 클라우드 서버 |
| **비용** | 무료 | $12~30/월 |
| **확장성** | 단일 서버만 | 수평/수직 확장 가능 |
| **백업** | 수동 (파일 복사) | 자동 일일 백업 |
| **복구** | 수동 | Point-in-time 복구 |
| **동시 접속** | 수십 명 제한 | 수천 명 가능 |
| **고가용성** | 없음 | Multi-AZ 지원 |
| **모니터링** | 없음 | CloudWatch 내장 |
| **적합한 경우** | 개발/테스트/소규모 | 프로덕션/대규모 |

### 언제 SQLite를 사용하나?

✅ **SQLite 사용 권장:**
- 개발 및 테스트 환경
- 하루 방문자 100명 미만
- 단일 서버 운영
- 비용 절감이 최우선

### 언제 RDS를 사용해야 하나?

✅ **RDS 사용 권장:**
- 프로덕션 환경 (실제 서비스)
- 하루 방문자 100명 이상
- 여러 서버에서 동시 접속
- 데이터 백업 및 복구 필요
- 고가용성 필요 (99.95% 가동 시간)
- 자동 확장 필요

---

## PostgreSQL RDS 생성 (단계별)

### 1단계: AWS RDS 콘솔 접속

1. **AWS Management Console 로그인**
   - https://console.aws.amazon.com

2. **RDS 서비스 검색**
   - 상단 검색창에 "RDS" 입력
   - "RDS" 클릭

3. **리전 선택**
   - 우측 상단에서 **Asia Pacific (Seoul) ap-northeast-2** 선택
   - Lightsail 인스턴스와 동일한 리전이어야 함!

### 2단계: 데이터베이스 생성

1. **"Create database" 버튼 클릭**

2. **Engine 선택**
   ```
   Engine type: PostgreSQL
   Engine Version: PostgreSQL 16.x (최신 버전)
   ```

3. **Template 선택**

   **개발/테스트용:**
   ```
   Template: Free tier
   → 1년 무료 (db.t2.micro, 20GB)
   ```

   **프로덕션용:**
   ```
   Template: Production
   → Multi-AZ 고가용성
   → db.t4g.micro 또는 db.t3.micro 선택 가능
   ```

4. **Settings (중요!)**
   ```
   DB instance identifier: satellite-tracker-db

   Credentials Settings:
   Master username: postgres
   Master password: [강력한 비밀번호]
                     예: SatelliteDB2024!@#

   ⚠️ 비밀번호를 꼭 메모하세요! 나중에 변경 어려움
   ```

5. **DB instance class**

   **Free Tier:**
   ```
   Instance class: db.t2.micro
   vCPUs: 1
   RAM: 1 GB
   비용: 무료 (1년)
   ```

   **프로덕션 (권장):**
   ```
   Instance class: db.t4g.micro
   vCPUs: 2
   RAM: 1 GB
   비용: $12.26/월

   또는

   Instance class: db.t3.micro
   vCPUs: 2
   RAM: 1 GB
   비용: $14.88/월
   ```

6. **Storage**
   ```
   Storage type: General Purpose SSD (gp3)
   Allocated storage: 20 GB (Free Tier) 또는 40 GB (프로덕션)

   ✅ Enable storage autoscaling (체크)
   Maximum storage threshold: 100 GB
   ```

7. **Connectivity (중요!)**
   ```
   Compute resource: Don't connect to an EC2 compute resource

   Network type: IPv4

   Virtual private cloud (VPC): Default VPC

   DB subnet group: default

   Public access: Yes ✅ (Lightsail에서 접속하려면 필수!)

   VPC security group: Choose existing
   → default 선택

   Availability Zone: No preference
   ```

8. **Database authentication**
   ```
   Database authentication: Password authentication
   ```

9. **Additional configuration**
   ```
   Initial database name: satellite_tracker

   Backup:
   ✅ Enable automated backups
   Backup retention period: 7 days

   Encryption:
   ✅ Enable encryption (Free Tier에서는 사용 불가)

   Monitoring:
   ✅ Enable Enhanced monitoring (선택 사항)
   ```

10. **"Create database" 클릭**
    - 생성 시간: 약 5-10분

### 3단계: RDS 엔드포인트 확인

1. **RDS 콘솔에서 "Databases" 클릭**
2. **생성한 DB (satellite-tracker-db) 클릭**
3. **"Connectivity & security" 탭에서 확인:**
   ```
   Endpoint: satellite-tracker-db.c1a2b3c4d5e6.ap-northeast-2.rds.amazonaws.com
   Port: 5432

   ⚠️ 이 엔드포인트를 메모하세요!
   ```

---

## 보안 설정

### 4단계: 보안 그룹 설정 (중요!)

RDS는 기본적으로 외부 접속이 차단되어 있습니다. Lightsail에서 접속하려면 보안 그룹을 수정해야 합니다.

1. **RDS 콘솔에서 "Connectivity & security" 탭**
2. **VPC security groups 섹션에서 보안 그룹 클릭**
   - 예: `default` 또는 `rds-launch-wizard-1`

3. **"Inbound rules" 탭 클릭**
4. **"Edit inbound rules" 클릭**

5. **규칙 추가:**
   ```
   Type: PostgreSQL
   Protocol: TCP
   Port range: 5432
   Source: Custom

   ⚠️ Source 입력:
   [Lightsail 고정 IP]/32

   예: 13.125.123.45/32

   Description: Lightsail satellite-backend access
   ```

6. **"Save rules" 클릭**

### 보안 팁

**❌ 절대 하지 말 것:**
```
Source: 0.0.0.0/0  ← 전 세계 누구나 접속 가능! 위험!
```

**✅ 권장 방법:**
```
Source: [Lightsail IP]/32  ← Lightsail 인스턴스만 접속 가능
```

**✅ 추가 보안 (선택 사항):**
- 내 컴퓨터 IP도 추가 (로컬에서 DB 관리 도구 사용 시)
- VPN 사용 시 VPN IP 추가

---

## Lightsail에서 RDS 연결

### 5단계: 환경 변수 설정

Lightsail 인스턴스에 SSH 접속:

```bash
ssh -i ~/Downloads/LightsailDefaultKey-ap-northeast-2.pem ubuntu@YOUR_LIGHTSAIL_IP
```

**백엔드 디렉토리로 이동:**
```bash
cd /home/ubuntu/satellite_vehicle_tracker/backend
```

**환경 변수 파일 수정:**
```bash
nano .env
```

**다음 내용 추가/수정:**
```env
# PostgreSQL RDS 연결
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_RDS_ENDPOINT:5432/satellite_tracker

# 실제 예시:
# DATABASE_URL=postgresql://postgres:SatelliteDB2024!@#@satellite-tracker-db.c1a2b3c4d5e6.ap-northeast-2.rds.amazonaws.com:5432/satellite_tracker

# ⚠️ 주의:
# - postgres = Master username
# - SatelliteDB2024!@# = Master password (RDS 생성 시 설정한 것)
# - satellite-tracker-db.c1a2b3c4d5e6.ap-northeast-2.rds.amazonaws.com = RDS Endpoint
# - satellite_tracker = Initial database name
```

**저장하고 나가기:**
```
Ctrl + X → Y → Enter
```

### 6단계: PostgreSQL 드라이버 설치

```bash
# 가상환경 활성화
source venv/bin/activate

# PostgreSQL 드라이버 설치
pip install psycopg2-binary

# requirements.txt에 추가 (향후 재배포 시 자동 설치)
echo "psycopg2-binary==2.9.9" >> requirements.txt
```

### 7단계: 서비스 재시작

```bash
# Supervisor로 백엔드 재시작
sudo supervisorctl restart satellite-backend

# 로그 확인 (에러 없는지 체크)
sudo tail -f /var/log/satellite-backend.out.log
```

**성공 메시지:**
```
✅ 데이터베이스 연결 성공
✅ 테이블 생성 완료
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**실패 시:**
```
❌ Connection refused
❌ password authentication failed
```
→ [문제 해결](#문제-해결) 섹션 참고

---

## 연결 테스트

### 방법 1: API 헬스 체크

```bash
curl http://localhost:8000/api/health
```

**응답:**
```json
{
  "status": "healthy",
  "database": "postgresql",
  "timestamp": "2025-10-30T12:00:00"
}
```

### 방법 2: psql 직접 연결

Lightsail 인스턴스에서:

```bash
# PostgreSQL 클라이언트 설치
sudo apt-get install -y postgresql-client

# RDS 연결 테스트
psql -h YOUR_RDS_ENDPOINT -U postgres -d satellite_tracker

# 비밀번호 입력 후 접속 성공 시:
satellite_tracker=> \dt
# 테이블 목록 표시

satellite_tracker=> SELECT COUNT(*) FROM abandoned_vehicles;
# 방치 차량 수 확인

satellite_tracker=> \q
# 종료
```

### 방법 3: 로컬 컴퓨터에서 연결 (선택 사항)

**Mac/Linux:**
```bash
# PostgreSQL 클라이언트 설치
brew install postgresql  # Mac
sudo apt-get install postgresql-client  # Linux

# 연결
psql -h YOUR_RDS_ENDPOINT -U postgres -d satellite_tracker
```

**Windows:**
- pgAdmin 설치: https://www.pgadmin.org/
- 연결 정보 입력:
  - Host: RDS Endpoint
  - Port: 5432
  - Username: postgres
  - Password: [설정한 비밀번호]
  - Database: satellite_tracker

---

## SQLite에서 RDS로 데이터 마이그레이션

기존 SQLite 데이터를 RDS로 이전하려면:

### 방법 1: 자동 마이그레이션 (향후 제공 예정)

```bash
cd /home/ubuntu/satellite_vehicle_tracker/backend
python migrate_sqlite_to_rds.py
```

### 방법 2: 수동 마이그레이션

```bash
# 1. SQLite 데이터 백업
sqlite3 satellite_tracker.db .dump > backup.sql

# 2. PostgreSQL에 임포트
psql -h YOUR_RDS_ENDPOINT -U postgres -d satellite_tracker < backup.sql
```

---

## 비용 및 최적화

### RDS 요금제

#### Free Tier (1년 무료)
```
인스턴스: db.t2.micro
vCPU: 1
RAM: 1 GB
스토리지: 20 GB SSD
백업: 20 GB
월 비용: $0 (첫 12개월)
13개월째부터: $15/월
```

#### 프로덕션 권장 (db.t4g.micro)
```
인스턴스: db.t4g.micro (ARM 기반, 20% 저렴)
vCPU: 2
RAM: 1 GB
스토리지: 40 GB gp3 SSD
비용 분석:
- 인스턴스: $9.36/월
- 스토리지: $4.60/월 (40GB)
- 백업: $0 (자동 백업 무료)
합계: $13.96/월
```

#### 프로덕션 대안 (db.t3.micro)
```
인스턴스: db.t3.micro (Intel 기반)
vCPU: 2
RAM: 1 GB
스토리지: 40 GB gp3 SSD
비용 분석:
- 인스턴스: $12.41/월
- 스토리지: $4.60/월
- 백업: $0
합계: $17.01/월
```

### 비용 절감 팁

1. **Reserved Instances (예약 인스턴스)**
   - 1년 약정: 40% 할인
   - 3년 약정: 60% 할인

2. **Auto Scaling Storage**
   - 초기 20GB로 시작
   - 필요 시 자동 확장
   - 사용한 만큼만 과금

3. **Backup 최적화**
   - 보존 기간 7일로 제한
   - 스냅샷은 수동으로 필요시에만

4. **모니터링**
   - CloudWatch로 사용량 추적
   - CPU/메모리 50% 미만이면 다운그레이드 고려

### 총 운영 비용 (AWS Lightsail + RDS)

```
Lightsail 인스턴스: $3.50/월
RDS PostgreSQL: $14/월
합계: $17.50/월

vs

Render (무료 티어): 타임아웃 이슈
ngrok: 컴퓨터 24/7 켜둬야 함

결론: AWS가 가장 안정적이고 비용 효율적
```

---

## 문제 해결

### 연결 실패: "Connection refused"

**원인:** 보안 그룹 설정 문제

**해결:**
1. RDS 콘솔 → Security groups
2. Inbound rules에 Lightsail IP 추가 확인
3. Port 5432 열림 확인

### 인증 실패: "password authentication failed"

**원인:** 비밀번호 오류

**해결:**
```bash
# .env 파일 확인
cat .env | grep DATABASE_URL

# 비밀번호 특수문자 URL 인코딩 필요
# 예: @ → %40, # → %23

# 올바른 형식:
DATABASE_URL=postgresql://postgres:MyPass%40123@endpoint:5432/db
```

### 테이블 없음: "relation does not exist"

**원인:** 테이블 자동 생성 실패

**해결:**
```bash
# Python 콘솔에서 수동 생성
cd /home/ubuntu/satellite_vehicle_tracker/backend
source venv/bin/activate
python

>>> from database import engine, Base
>>> from models_sqlalchemy import AbandonedVehicle, AnalysisLog
>>> Base.metadata.create_all(bind=engine)
>>> exit()

# 서비스 재시작
sudo supervisorctl restart satellite-backend
```

### 느린 쿼리

**해결:**
```sql
-- 인덱스 추가 (이미 models_sqlalchemy.py에 설정됨)
CREATE INDEX idx_city_district ON abandoned_vehicles(city, district);
CREATE INDEX idx_risk_level ON abandoned_vehicles(risk_level);

-- 쿼리 실행 계획 확인
EXPLAIN ANALYZE SELECT * FROM abandoned_vehicles WHERE city = '서울특별시';
```

### RDS 삭제 방법

테스트 후 삭제하려면:

```
RDS 콘솔 → Databases → satellite-tracker-db 선택
→ Actions → Delete
→ ✅ Create final snapshot (선택 사항)
→ ❌ Retain automated backups (체크 해제)
→ "delete me" 입력
→ Delete
```

---

## MySQL 사용 시 (PostgreSQL 대신)

### RDS MySQL 생성

```
Engine: MySQL 8.0
Instance class: db.t3.micro
Initial database name: satellite_tracker
```

### 환경 변수

```bash
DATABASE_URL=mysql+pymysql://admin:YOUR_PASSWORD@YOUR_RDS_ENDPOINT:3306/satellite_tracker
```

### 드라이버 설치

```bash
pip install pymysql cryptography
```

### 보안 그룹

```
Type: MySQL/Aurora
Port: 3306
Source: [Lightsail IP]/32
```

---

## 다음 단계

1. ✅ **RDS 생성 완료**
   - PostgreSQL 16.x
   - db.t4g.micro ($14/월)

2. ✅ **Lightsail 연결**
   - DATABASE_URL 설정
   - psycopg2-binary 설치

3. ✅ **테스트**
   - API 헬스 체크
   - 방치 차량 조회

4. 📊 **모니터링**
   - RDS CloudWatch 대시보드
   - 성능 최적화

5. 🔒 **보안 강화**
   - SSL/TLS 연결 (선택 사항)
   - 주기적 비밀번호 변경
   - 백업 정기 확인

---

## 참고 자료

- [AWS RDS 공식 문서](https://docs.aws.amazon.com/rds/)
- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)
- [SQLAlchemy ORM 가이드](https://docs.sqlalchemy.org/)
