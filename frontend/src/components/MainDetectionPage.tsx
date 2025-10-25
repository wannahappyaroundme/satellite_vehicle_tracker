import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { Search, RefreshCw, Loader, MapPin } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_FASTAPI_URL || 'http://localhost:8000/api';
const USE_DEMO_MODE = true; // 🎭 데모 모드 활성화 (API 키 불필요)

// 파란색 마커 아이콘 (방치 차량용)
const blueIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg width="25" height="41" viewBox="0 0 25 41" xmlns="http://www.w3.org/2000/svg">
      <path d="M12.5 0C5.6 0 0 5.6 0 12.5c0 9.4 12.5 28.5 12.5 28.5S25 21.9 25 12.5C25 5.6 19.4 0 12.5 0z" fill="#3B82F6"/>
      <circle cx="12.5" cy="12.5" r="6" fill="white"/>
    </svg>
  `),
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

interface AbandonedVehicle {
  id: string;
  latitude: number;
  longitude: number;
  similarity_percentage: number;
  risk_level: string;
  years_difference: number;
  bbox?: {
    x: number;
    y: number;
    w: number;
    h: number;
  };
}

// 지도 이벤트 컴포넌트 (지도 이동/확대 감지)
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

const MainDetectionPage: React.FC = () => {
  const [sido, setSido] = useState('');
  const [sigungu, setSigungu] = useState('');
  const [dong, setDong] = useState('');
  const [jibun, setJibun] = useState('');

  const [sidoList] = useState([
    '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시',
    '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원도',
    '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도'
  ]);

  const [sigunguList, setSigunguList] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);

  const [mapCenter, setMapCenter] = useState<[number, number]>([37.5665, 126.9780]); // 서울 기본
  const [mapZoom, setMapZoom] = useState(13);

  const [vehicles, setVehicles] = useState<AbandonedVehicle[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<AbandonedVehicle | null>(null);
  const [showSatellitePopup, setShowSatellitePopup] = useState(false);

  const [statusMessage, setStatusMessage] = useState('');
  const [currentAddress, setCurrentAddress] = useState(''); // 실시간 주소
  const [addressLoading, setAddressLoading] = useState(false);

  // 시/군/구 목록 가져오기
  useEffect(() => {
    if (sido) {
      const sigunguMap: { [key: string]: string[] } = {
        '서울특별시': ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'],
        '제주특별자치도': ['제주시', '서귀포시'],
        '경기도': ['수원시', '성남시', '의정부시', '안양시', '부천시', '광명시', '평택시', '용인시', '고양시', '화성시', '안산시', '남양주시', '시흥시', '파주시', '김포시'],
      };
      setSigunguList(sigunguMap[sido] || []);
      setSigungu('');
      setDong('');
      setJibun('');
    }
  }, [sido]);

  // 주소 검색 및 지도 이동
  const handleSearch = async () => {
    if (!sido) {
      alert('시/도를 선택해주세요');
      return;
    }

    setLoading(true);
    setStatusMessage('주소 검색 중...');

    try {
      // 데모 모드 또는 실제 API
      const endpoint = USE_DEMO_MODE ? '/demo/address/search' : '/address/search';

      const response = await axios.get(`${API_BASE_URL}${endpoint}`, {
        params: {
          sido,
          sigungu: sigungu || undefined,
          dong: dong || undefined,
          jibun: jibun || undefined
        }
      });

      if (response.data.success) {
        const { latitude, longitude, address } = response.data;
        const displayAddress = response.data.full_address || address;

        setMapCenter([latitude, longitude]);
        setMapZoom(17);

        const modeMsg = USE_DEMO_MODE ? ' 🎭 (데모 모드)' : '';
        setStatusMessage(`위치 찾음: ${displayAddress}${modeMsg}`);
        setAnalyzed(false);
        setVehicles([]);
      } else {
        setStatusMessage(`주소를 찾을 수 없습니다: ${response.data.error}`);
      }
    } catch (error: any) {
      console.error('Search error:', error);
      setStatusMessage(`검색 실패: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 방치 차량 분석
  const handleAnalyze = async () => {
    if (!mapCenter) {
      alert('먼저 주소를 검색해주세요');
      return;
    }

    setAnalyzing(true);
    const modeText = USE_DEMO_MODE ? ' 🎭 (데모 데이터 생성 중...)' : '';
    setStatusMessage(`방치 차량 분석 중...${modeText}`);

    try {
      // 데모 모드 또는 실제 API
      const endpoint = USE_DEMO_MODE ? '/demo/analyze-location' : '/analyze-location';

      const response = await axios.post(`${API_BASE_URL}${endpoint}?latitude=${mapCenter[0]}&longitude=${mapCenter[1]}&address=${encodeURIComponent(statusMessage)}`);

      if (response.data.success) {
        const abandonedVehicles = response.data.abandoned_vehicles || [];
        setVehicles(abandonedVehicles);
        setAnalyzed(true);

        const modeMsg = USE_DEMO_MODE ? ' 🎭' : '';
        if (abandonedVehicles.length === 0) {
          setStatusMessage(`✅ 방치 차량이 발견되지 않았습니다${modeMsg}`);
        } else {
          setStatusMessage(`🔵 ${abandonedVehicles.length}대의 방치 차량 발견${modeMsg}`);
        }
      } else {
        setStatusMessage(response.data.status_message || '분석 실패');
      }
    } catch (error: any) {
      console.error('Analysis error:', error);
      setStatusMessage(`분석 실패: ${error.message}`);
    } finally {
      setAnalyzing(false);
    }
  };

  // 차량 클릭 시 위성사진 팝업
  const handleVehicleClick = (vehicle: AbandonedVehicle) => {
    setSelectedVehicle(vehicle);
    setShowSatellitePopup(true);
  };

  // 지도 이동 시 현재 위치 주소 가져오기 (역지오코딩)
  const handleMapMove = async (center: [number, number], zoom: number) => {
    setMapCenter(center);
    setMapZoom(zoom);

    // 줌 레벨이 충분히 크면 주소 표시 (14 이상)
    if (zoom >= 14) {
      setAddressLoading(true);
      try {
        // Nominatim reverse geocoding (무료)
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
        console.error('Reverse geocoding error:', error);
        setCurrentAddress(`위도: ${center[0].toFixed(6)}, 경도: ${center[1].toFixed(6)}`);
      } finally {
        setAddressLoading(false);
      }
    } else {
      setCurrentAddress('');
    }
  };

  return (
    <Container>
      {/* 중앙 상단 검색 바 */}
      <SearchBar>
        <Logo>장기 방치 차량 탐지 시스템</Logo>

        <SearchControls>
          <Select value={sido} onChange={(e) => setSido(e.target.value)} disabled={loading || analyzing}>
            <option value="">시/도 선택</option>
            {sidoList.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </Select>

          <Select value={sigungu} onChange={(e) => setSigungu(e.target.value)} disabled={!sido || loading || analyzing}>
            <option value="">시/군/구 선택</option>
            {sigunguList.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </Select>

          <Input
            type="text"
            placeholder="동/읍/면 (선택)"
            value={dong}
            onChange={(e) => setDong(e.target.value)}
            disabled={loading || analyzing}
          />

          <Input
            type="text"
            placeholder="지번 (선택)"
            value={jibun}
            onChange={(e) => setJibun(e.target.value)}
            disabled={loading || analyzing}
          />

          <SearchButton onClick={handleSearch} disabled={!sido || loading || analyzing}>
            {loading ? <Loader size={20} className="spin" /> : <Search size={20} />}
            위치 검색
          </SearchButton>

          {!analyzed ? (
            <AnalyzeButton onClick={handleAnalyze} disabled={!mapCenter[0] || analyzing || loading}>
              {analyzing ? <Loader size={20} className="spin" /> : <Search size={20} />}
              {analyzing ? '분석 중...' : '방치 차량 분석'}
            </AnalyzeButton>
          ) : (
            <UpdateButton onClick={handleAnalyze} disabled={analyzing}>
              {analyzing ? <Loader size={20} className="spin" /> : <RefreshCw size={20} />}
              {analyzing ? '분석 중...' : '업데이트'}
            </UpdateButton>
          )}
        </SearchControls>

        {statusMessage && (
          <StatusMessage>{statusMessage}</StatusMessage>
        )}
      </SearchBar>

      {/* 지도 영역 */}
      <MapArea>
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          style={{ width: '100%', height: '100%' }}
        >
          <MapEventHandler onMapMove={handleMapMove} />
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* 검색 위치 표시 (작은 원) */}
          {mapCenter[0] !== 37.5665 && (
            <Circle
              center={mapCenter}
              radius={50}
              pathOptions={{ color: '#666', fillColor: '#999', fillOpacity: 0.3 }}
            />
          )}

          {/* 방치 차량 마커 (파란색) */}
          {vehicles.map((vehicle, index) => (
            <Marker
              key={index}
              position={[vehicle.latitude, vehicle.longitude]}
              icon={blueIcon}
              eventHandlers={{
                click: () => handleVehicleClick(vehicle)
              }}
            >
              <Popup>
                <PopupContent>
                  <PopupTitle>방치 차량 #{index + 1}</PopupTitle>
                  <PopupInfo>유사도: {vehicle.similarity_percentage}%</PopupInfo>
                  <PopupInfo>위험도: {vehicle.risk_level}</PopupInfo>
                  <PopupInfo>경과: {vehicle.years_difference}년</PopupInfo>
                  <PopupButton onClick={() => handleVehicleClick(vehicle)}>
                    상세보기
                  </PopupButton>
                </PopupContent>
              </Popup>
            </Marker>
          ))}
        </MapContainer>

        {/* 통계 표시 */}
        {analyzed && (
          <StatsOverlay>
            <StatItem>
              <StatLabel>분석 완료</StatLabel>
              <StatValue isClean={vehicles.length === 0}>
                {vehicles.length === 0 ? '정상' : `${vehicles.length}대`}
              </StatValue>
            </StatItem>
          </StatsOverlay>
        )}

        {/* 실시간 주소 표시 (좌측 하단) */}
        {currentAddress && (
          <AddressOverlay>
            <MapPin size={16} />
            <AddressText>
              {addressLoading ? '주소 확인 중...' : currentAddress}
            </AddressText>
          </AddressOverlay>
        )}
      </MapArea>

      {/* 차량 상세 팝업 (위성사진) */}
      {showSatellitePopup && selectedVehicle && (
        <SatellitePopup>
          <PopupOverlay onClick={() => setShowSatellitePopup(false)} />
          <PopupWindow>
            <PopupHeader>
              <PopupWindowTitle>방치 차량 상세 정보</PopupWindowTitle>
              <CloseButton onClick={() => setShowSatellitePopup(false)}>×</CloseButton>
            </PopupHeader>

            <PopupBody>
              <VehicleInfo>
                <InfoRow>
                  <InfoLabel>유사도:</InfoLabel>
                  <InfoValue>{selectedVehicle.similarity_percentage}%</InfoValue>
                </InfoRow>
                <InfoRow>
                  <InfoLabel>위험도:</InfoLabel>
                  <RiskBadge level={selectedVehicle.risk_level}>
                    {selectedVehicle.risk_level}
                  </RiskBadge>
                </InfoRow>
                <InfoRow>
                  <InfoLabel>경과 시간:</InfoLabel>
                  <InfoValue>{selectedVehicle.years_difference}년</InfoValue>
                </InfoRow>
              </VehicleInfo>

              <SatelliteImageContainer>
                <SatelliteImagePlaceholder>
                  <PlaceholderText>
                    해당 위치의 위성 사진
                    <br />
                    <small>(국토정보플랫폼 API 연동 시 표시)</small>
                  </PlaceholderText>
                </SatelliteImagePlaceholder>
              </SatelliteImageContainer>
            </PopupBody>
          </PopupWindow>
        </SatellitePopup>
      )}
    </Container>
  );
};

// Styled Components (흑백 + 파란색 테마)
const Container = styled.div`
  width: 100vw;
  height: 100vh;
  background: #000;
  position: relative;
  overflow: hidden;
`;

const SearchBar = styled.div`
  position: absolute;
  top: 40px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, rgba(0,0,0,0.95) 0%, rgba(20,20,20,0.95) 100%);
  backdrop-filter: blur(20px);
  padding: 30px 40px;
  z-index: 1000;
  border-radius: 20px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 20px 60px rgba(0,0,0,0.8), 0 0 80px rgba(59, 130, 246, 0.1);
  max-width: 1200px;
  width: 90%;

  @media (max-width: 768px) {
    top: 20px;
    width: 95%;
    padding: 20px;
  }
`;

const Logo = styled.h1`
  color: #fff;
  font-size: 28px;
  font-weight: 700;
  text-align: center;
  margin: 0 0 30px 0;
  letter-spacing: -0.5px;
  background: linear-gradient(90deg, #fff 0%, #3B82F6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;

  @media (max-width: 768px) {
    font-size: 20px;
    margin: 0 0 20px 0;
  }
`;

const SearchControls = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
`;

const Select = styled.select`
  padding: 12px 16px;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  min-width: 150px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover:not(:disabled) {
    border-color: #3B82F6;
  }

  &:focus {
    outline: none;
    border-color: #3B82F6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const Input = styled.input`
  padding: 12px 16px;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  min-width: 120px;
  transition: all 0.2s;

  &::placeholder {
    color: #666;
  }

  &:hover:not(:disabled) {
    border-color: #3B82F6;
  }

  &:focus {
    outline: none;
    border-color: #3B82F6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const SearchButton = styled.button`
  padding: 12px 24px;
  background: #3B82F6;
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;

  &:hover:not(:disabled) {
    background: #2563EB;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;

const AnalyzeButton = styled(SearchButton)`
  background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
`;

const UpdateButton = styled(SearchButton)`
  background: #666;

  &:hover:not(:disabled) {
    background: #888;
  }
`;

const StatusMessage = styled.div`
  text-align: center;
  margin-top: 20px;
  padding: 12px 20px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 10px;
  color: #3B82F6;
  font-size: 14px;
  font-weight: 500;
  backdrop-filter: blur(10px);
`;

const MapArea = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;

  .leaflet-container {
    background: #1a1a1a;
  }
`;

const StatsOverlay = styled.div`
  position: absolute;
  top: 140px;
  right: 20px;
  background: rgba(0,0,0,0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 12px;
  padding: 20px;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.8);

  @media (max-width: 768px) {
    top: auto;
    bottom: 80px;
    right: 10px;
  }
`;

const StatItem = styled.div`
  text-align: center;
`;

const StatLabel = styled.div`
  color: #999;
  font-size: 12px;
  margin-bottom: 4px;
`;

const StatValue = styled.div<{ isClean?: boolean }>`
  color: ${props => props.isClean ? '#10B981' : '#3B82F6'};
  font-size: 24px;
  font-weight: 700;
`;

const PopupContent = styled.div`
  padding: 4px;
`;

const PopupTitle = styled.div`
  font-weight: 700;
  font-size: 14px;
  margin-bottom: 8px;
  color: #000;
`;

const PopupInfo = styled.div`
  font-size: 12px;
  margin-bottom: 4px;
  color: #333;
`;

const PopupButton = styled.button`
  margin-top: 8px;
  padding: 6px 12px;
  background: #3B82F6;
  border: none;
  border-radius: 4px;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
  width: 100%;

  &:hover {
    background: #2563EB;
  }
`;

// 위성사진 팝업
const SatellitePopup = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const PopupOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.8);
`;

const PopupWindow = styled.div`
  position: relative;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 16px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  z-index: 2001;
  box-shadow: 0 20px 60px rgba(0,0,0,0.8);
`;

const PopupHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #333;
`;

const PopupWindowTitle = styled.h2`
  color: #fff;
  font-size: 20px;
  font-weight: 700;
  margin: 0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: #999;
  font-size: 32px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;

  &:hover {
    color: #fff;
  }
`;

const PopupBody = styled.div`
  padding: 24px;
`;

const VehicleInfo = styled.div`
  margin-bottom: 24px;
`;

const InfoRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #333;

  &:last-child {
    border-bottom: none;
  }
`;

const InfoLabel = styled.span`
  color: #999;
  font-size: 14px;
`;

const InfoValue = styled.span`
  color: #fff;
  font-size: 14px;
  font-weight: 600;
`;

const RiskBadge = styled.span<{ level: string }>`
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  background: ${props => {
    switch(props.level) {
      case 'CRITICAL': return '#DC2626';
      case 'HIGH': return '#EA580C';
      case 'MEDIUM': return '#F59E0B';
      default: return '#10B981';
    }
  }};
  color: #fff;
`;

const SatelliteImageContainer = styled.div`
  background: #0a0a0a;
  border: 1px solid #333;
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 16/9;
`;

const SatelliteImagePlaceholder = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
`;

const PlaceholderText = styled.div`
  text-align: center;
  font-size: 16px;

  small {
    font-size: 12px;
    color: #444;
  }
`;

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

  svg {
    color: #3B82F6;
    flex-shrink: 0;
  }

  @media (max-width: 768px) {
    max-width: calc(100% - 40px);
    font-size: 12px;
  }
`;

const AddressText = styled.div`
  color: #fff;
  font-size: 13px;
  line-height: 1.4;
  word-break: keep-all;

  @media (max-width: 768px) {
    font-size: 11px;
  }
`;

export default MainDetectionPage;
