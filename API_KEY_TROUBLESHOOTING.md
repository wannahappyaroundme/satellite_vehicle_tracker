# 🔧 API 키 문제 해결 가이드

## ⚠️ 발생한 오류

```
Status: ERROR
Code: INVALID_KEY
Message: "등록되지 않은 인증키입니다."
```

---

## 🔍 원인 분석

현재 `.env` 파일에 입력된 API 키가 국토정보플랫폼에 등록되지 않았거나 비활성 상태입니다.

---

## ✅ 해결 방법

### 방법 1: API 키 재확인 (권장)

1. **국토정보플랫폼 로그인**
   ```
   https://www.vworld.kr
   ```

2. **마이페이지 → 오픈API 관리**
   - 승인된 API 키 목록 확인
   - 상태가 "승인" 또는 "사용중"인지 확인

3. **올바른 API 키 복사**
   - 전체 키를 정확히 복사 (공백 없이)
   - 형식: `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

4. **.env 파일 업데이트**
   ```bash
   nano .env

   # 이 부분 수정
   NGII_API_KEY=새로운_올바른_API_키
   ```

5. **다시 테스트**
   ```bash
   cd backend
   python ngii_api_service.py
   ```

---

### 방법 2: API 재신청

API 키가 만료되었거나 삭제된 경우:

1. https://www.vworld.kr → 로그인
2. "오픈API" → "오픈 API 활용신청"
3. 새로 신청:
   ```
   API 유형: Open API 2.0
   서비스명: 장기 방치 차량 탐지
   서비스 URL: http://localhost:3000
   ```
4. 승인 후 새 키 복사 → `.env` 업데이트

---

### 방법 3: 샘플 데이터로 테스트 (API 없이)

API 키 없이도 시스템을 테스트할 수 있습니다!

#### 옵션 A: 샘플 이미지 분석
```bash
# 2015 vs 2020 제주시 항공사진 비교
python test_abandoned_detection.py
```

**결과:**
- `comparison_result.jpg` - 비교 시각화
- `detection_results.json` - 탐지 결과
- 콘솔에 방치 차량 통계 출력

#### 옵션 B: 데모 모드로 프론트엔드 실행

Mock 데이터를 사용하도록 수정하겠습니다:

```bash
# 1. FastAPI 서버 (데모 모드)
cd backend
python fastapi_app.py

# 2. 프론트엔드
cd frontend
npm start

# 3. 브라우저
http://localhost:3000
```

**데모 모드 기능:**
- 주소 검색: 고정 좌표 사용
- 방치 차량: 샘플 데이터 표시
- 지도: 정상 작동

---

## 🧪 API 키 검증 스크립트

API 키가 올바른지 빠르게 확인:

```bash
python << 'EOF'
import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('NGII_API_KEY')

if not api_key or api_key == '여기에_발급받은_API_키를_입력하세요':
    print("❌ API 키가 설정되지 않았습니다!")
    print("   .env 파일을 확인하세요.")
    exit(1)

print(f"🔑 API 키: {api_key[:20]}...")

# 간단한 테스트
url = 'http://api.vworld.kr/req/address'
params = {
    'service': 'address',
    'request': 'getCoord',
    'version': '2.0',
    'crs': 'epsg:4326',
    'address': '서울특별시',
    'format': 'json',
    'type': 'parcel',
    'key': api_key
}

response = requests.get(url, params=params, timeout=10)
data = response.json()

if data.get('response', {}).get('status') == 'OK':
    print("✅ API 키가 정상적으로 작동합니다!")
    print(f"   테스트 주소: 서울특별시")
    result = data['response']['result']
    if result.get('point'):
        print(f"   좌표: {result['point']['x']}, {result['point']['y']}")
elif data.get('response', {}).get('status') == 'ERROR':
    error = data['response']['error']
    print(f"❌ API 오류:")
    print(f"   코드: {error.get('code')}")
    print(f"   메시지: {error.get('text')}")
    print(f"\n해결 방법:")
    if error.get('code') == 'INVALID_KEY':
        print("   1. vworld.kr에서 API 키 재확인")
        print("   2. 올바른 키를 .env 파일에 입력")
        print("   3. 또는 샘플 데이터로 테스트 (python test_abandoned_detection.py)")
else:
    print("❓ 알 수 없는 응답")
    print(f"   {data}")
EOF
```

---

## 📱 국토정보플랫폼 고객센터

도움이 필요하면:
- **전화:** 1588-7906
- **이메일:** support@vworld.kr
- **운영시간:** 평일 09:00-18:00

---

## 🎯 권장 순서

1. **먼저 샘플 데이터 테스트**
   ```bash
   python test_abandoned_detection.py
   ```
   → 시스템이 정상 작동하는지 확인

2. **API 키 재확인**
   - vworld.kr → 마이페이지
   - 올바른 키 복사

3. **`.env` 파일 업데이트**

4. **다시 테스트**
   ```bash
   cd backend
   python ngii_api_service.py
   ```

5. **전체 시스템 실행**

---

## 💡 추가 팁

### API 키 형식 확인
```bash
# 올바른 형식 (길이 40자 정도, 대문자+숫자)
NGII_API_KEY=8F1EC6DE4CEE080AFD35D0977224F153D04CAAFFFA

# 잘못된 형식
NGII_API_KEY="8F1EC6DE..." (따옴표 X)
NGII_API_KEY=여기에_발급... (미입력)
NGII_API_KEY= (공백)
```

### .env 파일 저장 확인
```bash
# 파일 내용 확인
cat .env | grep NGII_API_KEY

# 변경사항 적용 (서버 재시작)
# Ctrl+C로 중단 후 다시 시작
python fastapi_app.py
```

---

**현재 상황:** API 키 오류로 실제 항공사진을 가져올 수 없음

**해결 완료 시:** 주소 검색 + 실시간 지도 + 방치 차량 탐지 모두 작동

**임시 대안:** 샘플 데이터로 시스템 테스트 가능 ✅
