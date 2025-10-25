# UI 변경 사항 요약

## 📅 변경 날짜
2025-10-25

## 🎯 변경 목적
사용자 친화적인 장기 방치 차량 탐지 시스템 UI 개선

## ✅ 주요 변경 사항

### 1. **홈페이지 단순화**
- **변경 전**: 복잡한 사이드바 + 여러 탭 메뉴
- **변경 후**: `MainDetectionPage`를 기본 홈페이지로 설정
- **파일**: `frontend/src/App.tsx`

```typescript
// 이전: 복잡한 사이드바 구조
<AppContainer>
  <Sidebar>
    <TabContainer>...</TabContainer>
    {renderTabContent()}
  </Sidebar>
  <ContentArea>...</ContentArea>
</AppContainer>

// 현재: 단순한 구조
const App: React.FC = () => {
  return <MainDetectionPage />;
};
```

### 2. **위도/경도 입력 제거** ✅
- 사용자가 직접 위도/경도를 입력할 필요 없음
- 주소 기반 검색만 제공
- 이미 `MainDetectionPage`에 구현되어 있음

### 3. **차량 종류별 디텍팅 필터 제거** ✅
- 모든 방치 차량을 동일하게 표시
- 복잡한 필터링 옵션 제거
- 이미 `MainDetectionPage`에 구현되어 있음

### 4. **메뉴를 최상단 중앙으로 이동** ✅
- **위치**: 화면 최상단 중앙
- **스타일**: 반투명 블랙 + 파란색 테두리
- **구조**: 지역 → 시/군/구 → 동 → 지번 (계층적 주소 선택)

```typescript
<SearchBar>
  <Logo>장기 방치 차량 탐지 시스템</Logo>
  <SearchControls>
    <Select>시/도 선택</Select>
    <Select>시/군/구 선택</Select>
    <Input>동/읍/면 (선택)</Input>
    <Input>지번 (선택)</Input>
    <SearchButton>위치 검색</SearchButton>
    <AnalyzeButton>방치 차량 분석</AnalyzeButton>
  </SearchControls>
</SearchBar>
```

### 5. **실시간 주소 표시 기능 추가** ✨ (NEW)
- **위치**: 좌측 하단
- **트리거**: 지도 확대/이동 시 자동 실행
- **조건**: 줌 레벨 14 이상에서만 표시
- **API**: Nominatim Reverse Geocoding (OpenStreetMap)

#### 구현 코드:
```typescript
// MapEventHandler 컴포넌트 추가
const MapEventHandler: React.FC<{ onMapMove: (center: [number, number], zoom: number) => void }> = ({ onMapMove }) => {
  const map = useMapEvents({
    moveend: () => {
      const center = map.getCenter();
      const zoom = map.getZoom();
      onMapMove([center.lat, center.lng], zoom);
    },
    zoomend: () => {
      const center = map.getCenter();
      const zoom = map.getZoom();
      onMapMove([center.lat, center.lng], zoom);
    }
  });
  return null;
};

// 역지오코딩 함수
const handleMapMove = async (center: [number, number], zoom: number) => {
  if (zoom >= 14) {
    setAddressLoading(true);
    try {
      const response = await axios.get('https://nominatim.openstreetmap.org/reverse', {
        params: {
          lat: center[0],
          lon: center[1],
          format: 'json',
          'accept-language': 'ko',
          addressdetails: 1
        },
        headers: {
          'User-Agent': 'AbandonedVehicleDetection/1.0'
        }
      });

      if (response.data && response.data.display_name) {
        setCurrentAddress(response.data.display_name);
      }
    } catch (error) {
      setCurrentAddress(`위도: ${center[0].toFixed(6)}, 경도: ${center[1].toFixed(6)}`);
    } finally {
      setAddressLoading(false);
    }
  } else {
    setCurrentAddress('');
  }
};
```

#### UI 스타일:
```typescript
const AddressOverlay = styled.div`
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(0,0,0,0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 12px;
  padding: 12px 20px;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 500px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.8);
`;
```

### 6. **통계 오버레이 위치 조정**
- **변경 전**: 우측 하단 (주소 오버레이와 겹칠 수 있음)
- **변경 후**: 우측 상단 (top: 140px, right: 20px)
- 모바일에서는 우측 하단 유지 (주소 위)

## 📱 반응형 디자인
- 모바일에서도 잘 보이도록 미디어 쿼리 추가
- 주소 오버레이: `max-width: calc(100% - 40px)` on mobile
- 통계 오버레이: 모바일에서 `bottom: 80px` (주소 바로 위)

## 🎨 디자인 테마
- **배경**: 검정색 (#000)
- **메뉴**: 반투명 검정 + 파란색 테두리 (#3B82F6)
- **강조색**: 파란색 (#3B82F6)
- **텍스트**: 흰색 (#fff) / 회색 (#999, #666)
- **효과**: backdrop-filter: blur(), box-shadow

## 🚀 사용 방법

### 개발 서버 실행:
```bash
# 프론트엔드 실행
cd frontend
npm start

# 백엔드 실행 (FastAPI - 데모 모드)
cd backend
python fastapi_app.py
```

### 사용자 워크플로우:
1. **주소 검색**:
   - 시/도 선택 (예: 서울특별시)
   - 시/군/구 선택 (예: 강남구)
   - 동 입력 (선택, 예: 역삼동)
   - 지번 입력 (선택, 예: 123)
   - "위치 검색" 클릭

2. **지도 확인**:
   - 지도가 해당 위치로 이동
   - 확대하면 좌측 하단에 정확한 주소 표시
   - 줌 레벨 14 이상에서 주소 자동 갱신

3. **방치 차량 분석**:
   - "방치 차량 분석" 버튼 클릭
   - 데모 모드에서 샘플 데이터 생성
   - 파란색 마커로 방치 차량 표시

4. **상세 정보 확인**:
   - 마커 클릭 시 팝업 표시
   - "상세보기" 클릭 시 위성사진 팝업

## 📦 수정된 파일

### Frontend:
1. **`frontend/src/App.tsx`** (완전 재작성)
   - 기존 복잡한 사이드바 제거
   - `MainDetectionPage`만 렌더링

2. **`frontend/src/components/MainDetectionPage.tsx`** (대폭 개선)
   - `MapEventHandler` 컴포넌트 추가
   - `handleMapMove` 함수 추가 (역지오코딩)
   - `currentAddress` 상태 추가
   - `AddressOverlay` UI 컴포넌트 추가
   - `StatsOverlay` 위치 조정

### Backend:
- 백엔드 변경 없음
- 역지오코딩은 프론트엔드에서 Nominatim API 직접 사용

## 🔧 기술 스택

### 주요 라이브러리:
- **React**: UI 프레임워크
- **TypeScript**: 타입 안정성
- **Leaflet**: 지도 라이브러리
- **react-leaflet**: React Leaflet 바인딩
- **styled-components**: CSS-in-JS
- **axios**: HTTP 클라이언트
- **lucide-react**: 아이콘

### 외부 API:
- **Nominatim (OpenStreetMap)**: 무료 역지오코딩
  - URL: `https://nominatim.openstreetmap.org/reverse`
  - 파라미터: `lat`, `lon`, `format=json`, `accept-language=ko`
  - User-Agent 필수

## ⚠️ 주의사항

1. **Nominatim Usage Policy**:
   - 초당 1회 요청 제한 (자동으로 디바운스 처리 권장)
   - User-Agent 헤더 필수
   - 상업적 사용 시 자체 서버 구축 권장

2. **줌 레벨**:
   - 줌 레벨 14 미만: 주소 표시 안 함
   - 줌 레벨 14 이상: 주소 자동 표시

3. **데모 모드**:
   - `USE_DEMO_MODE = true`로 설정되어 있음
   - 실제 API 키 없이 샘플 데이터로 테스트 가능

## 🎯 향후 개선 사항

1. **Nominatim 디바운스 처리**:
   ```typescript
   // 지도 이동 시 너무 자주 API 호출하지 않도록
   const debouncedHandleMapMove = debounce(handleMapMove, 500);
   ```

2. **자체 역지오코딩 API**:
   - 백엔드에 `/api/reverse-geocode` 엔드포인트 추가
   - Kakao Local API 또는 VWorld API 사용

3. **주소 캐싱**:
   - 같은 좌표에 대한 반복 요청 방지
   - localStorage에 최근 주소 저장

4. **오프라인 지원**:
   - Service Worker로 지도 타일 캐싱
   - 오프라인 모드에서도 기본 기능 동작

## 📝 테스트 방법

### 1. 프론트엔드 실행:
```bash
cd frontend
npm start
```
브라우저에서 `http://localhost:3000` 접속

### 2. 주소 검색 테스트:
- 서울특별시 → 강남구 선택
- "위치 검색" 클릭
- 지도가 강남구로 이동하는지 확인

### 3. 실시간 주소 표시 테스트:
- 지도 확대 (줌 레벨 14+)
- 지도 드래그로 이동
- 좌측 하단에 주소가 실시간으로 바뀌는지 확인

### 4. 방치 차량 분석 테스트:
- "방치 차량 분석" 클릭
- 파란색 마커가 표시되는지 확인
- 마커 클릭 → 팝업 → "상세보기" → 위성사진 팝업 확인

## 🎉 완료!
모든 요구사항이 구현되었습니다:
- ✅ 위도/경도 입력 제거
- ✅ 차량 종류별 필터 제거
- ✅ 메뉴 최상단 중앙 배치
- ✅ 계층적 주소 선택 (지역 → 동 → 지번)
- ✅ 실시간 주소 표시 (지도 확대 시)
