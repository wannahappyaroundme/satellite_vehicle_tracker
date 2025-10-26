# 🚀 효율적인 CCTV 데이터 관리 전략

## ❌ 문제점: CSV 파일이 너무 무겁다

전국 CCTV 표준데이터를 전부 다운로드하면:
- **파일 크기**: 10MB ~ 100MB+ (XLSX/CSV)
- **레코드 수**: 수만 ~ 수십만 개
- **Git 저장소에 부적합**: 큰 파일은 Git 성능 저하
- **메모리 문제**: pandas로 전체 로드 시 메모리 부담

---

## ✅ 해결 방법 3가지

### 방법 1: API 직접 호출 (추천) ⭐

**장점**: 파일 다운로드 불필요, 항상 최신 데이터
**단점**: API 호출 제한 있을 수 있음

```python
import requests

def fetch_cctv_from_api(lat, lon, radius=1000):
    """
    실시간 API 호출로 필요한 CCTV만 가져오기
    """
    # 국토교통부 ITS API
    its_url = "http://openapi.its.go.kr:8081/api/NCCTVInfo"
    params = {
        'key': ITS_API_KEY,
        'minX': lon - 0.01,
        'maxX': lon + 0.01,
        'minY': lat - 0.01,
        'maxY': lat + 0.01
    }

    response = requests.get(its_url, params=params)
    return response.json()
```

**이 방법을 사용하면:**
- ✅ 파일 저장 불필요
- ✅ 항상 최신 데이터
- ✅ 필요한 지역만 조회
- ✅ Git 저장소 가벼움

---

### 방법 2: 지역별 분할 저장

**전국 데이터를 지역별로 분할하여 저장**

```bash
# 예시 구조
backend/data/
├── cctv_seoul.db        # 서울 (10MB)
├── cctv_busan.db        # 부산 (5MB)
├── cctv_gyeonggi.db     # 경기 (15MB)
└── cctv_index.json      # 메타데이터 (1KB)
```

```python
def get_regional_database(lat, lon):
    """좌표로 지역 판별 후 해당 DB만 로드"""
    region = get_region_from_coords(lat, lon)
    db_path = f'data/cctv_{region}.db'

    if not os.path.exists(db_path):
        # 해당 지역 데이터만 다운로드
        download_regional_data(region)

    return sqlite3.connect(db_path)
```

**장점:**
- ✅ 필요한 지역 DB만 로드
- ✅ 메모리 효율적
- ✅ 지역별 업데이트 가능

**단점:**
- ⚠️ 여전히 여러 DB 파일 필요
- ⚠️ Git에 포함하면 저장소 커짐

---

### 방법 3: 샘플 데이터 + On-Demand 로딩 (최적) ⭐⭐⭐

**Git에는 샘플만, 실제 데이터는 처음 실행 시 다운로드**

#### 프로젝트 구조:
```
backend/
├── data/
│   ├── .gitignore                    # 실제 데이터 제외
│   └── cctv_sample.db                # 샘플 100개 (Git 포함)
├── public_cctv_integration.py
└── data_downloader.py                # 자동 다운로드 스크립트
```

#### `.gitignore`:
```gitignore
# 대용량 CCTV 데이터 제외
backend/data/cctv_database.db
backend/data/*.csv
backend/data/*.xlsx
backend/data/full_data/

# 샘플 데이터는 포함
!backend/data/cctv_sample.db
```

#### 자동 다운로드 스크립트:
```python
# data_downloader.py
import os
import requests
from pathlib import Path

DATA_SOURCES = {
    'national_cctv': {
        'url': 'https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=FILE_000000002866304',
        'filename': 'national_cctv_data.csv',
        'size_mb': 50,
        'description': '전국 CCTV 표준데이터'
    }
}

def download_data_if_needed():
    """
    첫 실행 시 자동으로 데이터 다운로드
    """
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(exist_ok=True)

    db_path = data_dir / 'cctv_database.db'

    if db_path.exists():
        print("✅ CCTV 데이터베이스가 이미 존재합니다.")
        return

    print("📥 CCTV 데이터 다운로드 중... (첫 실행 시에만)")
    print("⏱️  예상 시간: 1~2분")

    # 사용자에게 선택권 제공
    choice = input("전국 데이터를 다운로드하시겠습니까? (y/n): ")

    if choice.lower() == 'y':
        # CSV 다운로드 및 SQLite 변환
        download_and_import_national_data()
    else:
        # 샘플 데이터 복사
        print("샘플 데이터를 사용합니다 (100개 CCTV)")
        import shutil
        shutil.copy(data_dir / 'cctv_sample.db', db_path)
```

#### FastAPI 시작 시 자동 실행:
```python
# fastapi_app.py
from data_downloader import download_data_if_needed

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 데이터 확인"""
    download_data_if_needed()
    logger.info("CCTV 데이터 준비 완료")
```

---

## 🎯 최종 추천 방안

### 프로덕션 환경 (배포 시):
```python
# 1. API 직접 호출 (방법 1)
# 2. 서버 시작 시 데이터 자동 다운로드 (방법 3)
```

### 개발 환경:
```python
# 샘플 데이터 사용 (Git 포함)
# 필요 시 전체 데이터 다운로드
```

### Git 저장소:
```
✅ 포함:
- 샘플 데이터 (100개, ~100KB)
- 다운로드 스크립트
- 설명 문서

❌ 제외:
- 전체 CCTV CSV (10~100MB)
- 전체 데이터베이스 파일
```

---

## 💾 메모리 최적화 기법

### 1. Lazy Loading (지연 로딩)
```python
class CCTVService:
    def __init__(self):
        self._db = None  # 초기화 시 로드 안 함

    @property
    def db(self):
        """필요할 때만 DB 연결"""
        if self._db is None:
            self._db = sqlite3.connect('data/cctv_database.db')
        return self._db
```

### 2. Chunked Processing (청크 처리)
```python
def load_cctv_csv_chunked(csv_path, chunk_size=10000):
    """대용량 CSV를 청크로 나눠서 처리"""
    for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
        # 청크별로 처리
        process_chunk(chunk)
        # 메모리 해제
        del chunk
```

### 3. Spatial Index (공간 인덱스)
```python
# SQLite에 R-Tree spatial index 사용
conn.execute('''
    CREATE VIRTUAL TABLE cctv_spatial_index
    USING rtree(id, minX, maxX, minY, maxY)
''')

# 빠른 지역 검색
conn.execute('''
    SELECT * FROM cctv_locations
    WHERE id IN (
        SELECT id FROM cctv_spatial_index
        WHERE minX <= ? AND maxX >= ?
          AND minY <= ? AND maxY >= ?
    )
''', (lon+0.01, lon-0.01, lat+0.01, lat-0.01))
```

### 4. 캐싱 전략
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cctvs_in_area(lat, lon, radius):
    """자주 조회되는 지역은 캐시"""
    return query_database(lat, lon, radius)
```

---

## 🔥 실전 구현 예시

```python
# public_cctv_integration.py 개선

class PublicCCTVIntegration:
    def __init__(self):
        self.db_path = self._ensure_database()

    def _ensure_database(self):
        """데이터베이스 확인 및 생성"""
        data_dir = Path(__file__).parent / 'data'
        data_dir.mkdir(exist_ok=True)

        db_path = data_dir / 'cctv_database.db'

        if not db_path.exists():
            # 샘플 데이터 사용
            sample_db = data_dir / 'cctv_sample.db'
            if sample_db.exists():
                shutil.copy(sample_db, db_path)
                logger.info("Using sample CCTV database")
            else:
                # 빈 DB 생성
                self._create_empty_database(db_path)
                logger.warning("No CCTV data available. Use API mode.")

        return db_path

    def search_nearby_cctvs(self, lat, lon, radius=1000):
        """
        하이브리드 방식: 로컬 DB 우선, 없으면 API 호출
        """
        # 1. 로컬 DB 검색
        local_results = self._search_local_db(lat, lon, radius)

        if len(local_results) > 0:
            return local_results

        # 2. 로컬에 없으면 API 호출
        logger.info("Fetching from ITS API...")
        api_results = self.fetch_its_cctvs(
            lat - 0.01, lat + 0.01,
            lon - 0.01, lon + 0.01
        )

        # 3. API 결과를 로컬 DB에 캐싱
        self._cache_api_results(api_results)

        return api_results
```

---

## 📊 데이터 크기 비교

| 방법 | Git 저장소 크기 | 메모리 사용 | 응답 속도 |
|------|----------------|------------|----------|
| **전체 CSV 포함** | 🔴 50~100MB | 🔴 높음 | 🟢 빠름 |
| **SQLite 전체** | 🟡 30~50MB | 🟡 중간 | 🟢 빠름 |
| **샘플 + API** | 🟢 <1MB | 🟢 낮음 | 🟡 중간 |
| **API 직접** | 🟢 0MB | 🟢 최저 | 🟡 네트워크 의존 |

---

## 🎯 결론

**최적 전략 조합:**

1. **Git 저장소**: 샘플 데이터만 (100개, ~100KB)
2. **프로덕션**: API 직접 호출 + 로컬 캐싱
3. **개발 환경**: 샘플 데이터 사용
4. **첫 배포 시**: 자동 데이터 다운로드 옵션 제공

이렇게 하면:
- ✅ Git 저장소 가벼움 (<1MB)
- ✅ 메모리 효율적
- ✅ 항상 최신 데이터
- ✅ 개발 환경에서도 즉시 테스트 가능
