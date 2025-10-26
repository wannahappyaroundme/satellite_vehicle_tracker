import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Search, Loader, MapPin, BarChart3, Settings, Camera } from 'lucide-react';
import axios from 'axios';
import StatisticsDashboard from './StatisticsDashboard';
import AdminDashboard from './AdminDashboard';

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

interface CCTVLocation {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  distance?: number; // meters
  type?: string;
  is_public: boolean;
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

// 지도 동적 이동 컴포넌트 (FIX: 지역 선택 시 지도 이동)
const MapController: React.FC<{ center: [number, number]; zoom: number }> = ({ center, zoom }) => {
  const map = useMap();

  useEffect(() => {
    map.setView(center, zoom, { animate: true, duration: 1 });
  }, [center, zoom, map]);

  return null;
};

const MainDetectionPage: React.FC = () => {
  const [sido, setSido] = useState('');
  const [sigungu, setSigungu] = useState('');

  const [sidoList] = useState([
    '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시',
    '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원도',
    '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도'
  ]);

  const [sigunguList, setSigunguList] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingVehicles, setLoadingVehicles] = useState(false);
  const [showVehicles, setShowVehicles] = useState(false); // 방치 차량 표시 토글

  const [mapCenter, setMapCenter] = useState<[number, number]>([37.5665, 126.9780]); // 서울 기본
  const [mapZoom, setMapZoom] = useState(13);

  const [vehicles, setVehicles] = useState<AbandonedVehicle[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<AbandonedVehicle | null>(null);
  const [showSatellitePopup, setShowSatellitePopup] = useState(false);
  const [imageScale, setImageScale] = useState(1);
  const [imagePosition, setImagePosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const [showStatsDashboard, setShowStatsDashboard] = useState(false);
  const [showAdminDashboard, setShowAdminDashboard] = useState(false);

  const [statusMessage, setStatusMessage] = useState('');
  const [currentAddress, setCurrentAddress] = useState(''); // 실시간 주소
  const [addressLoading, setAddressLoading] = useState(false);

  // CCTV 검증 관련 상태
  const [nearbyCCTVs, setNearbyCCTVs] = useState<CCTVLocation[]>([]);
  const [showCCTVVerification, setShowCCTVVerification] = useState(false);
  const [loadingCCTV, setLoadingCCTV] = useState(false);

  // 시/군/구 목록 가져오기
  useEffect(() => {
    if (sido) {
      const sigunguMap: { [key: string]: string[] } = {
        '서울특별시': ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'],
        '부산광역시': ['강서구', '금정구', '기장군', '남구', '동구', '동래구', '부산진구', '북구', '사상구', '사하구', '서구', '수영구', '연제구', '영도구', '중구', '해운대구'],
        '대구광역시': ['남구', '달서구', '달성군', '동구', '북구', '서구', '수성구', '중구'],
        '인천광역시': ['강화군', '계양구', '남동구', '동구', '미추홀구', '부평구', '서구', '연수구', '옹진군', '중구'],
        '광주광역시': ['광산구', '남구', '동구', '북구', '서구'],
        '대전광역시': ['대덕구', '동구', '서구', '유성구', '중구'],
        '울산광역시': ['남구', '동구', '북구', '울주군', '중구'],
        '세종특별자치시': ['세종시'],
        '경기도': ['수원시', '성남시', '의정부시', '안양시', '부천시', '광명시', '평택시', '동두천시', '안산시', '고양시', '과천시', '구리시', '남양주시', '오산시', '시흥시', '군포시', '의왕시', '하남시', '용인시', '파주시', '이천시', '안성시', '김포시', '화성시', '광주시', '양주시', '포천시', '여주시', '연천군', '가평군', '양평군'],
        '강원도': ['춘천시', '원주시', '강릉시', '동해시', '태백시', '속초시', '삼척시', '홍천군', '횡성군', '영월군', '평창군', '정선군', '철원군', '화천군', '양구군', '인제군', '고성군', '양양군'],
        '충청북도': ['청주시', '충주시', '제천시', '보은군', '옥천군', '영동군', '증평군', '진천군', '괴산군', '음성군', '단양군'],
        '충청남도': ['천안시', '공주시', '보령시', '아산시', '서산시', '논산시', '계룡시', '당진시', '금산군', '부여군', '서천군', '청양군', '홍성군', '예산군', '태안군'],
        '전라북도': ['전주시', '군산시', '익산시', '정읍시', '남원시', '김제시', '완주군', '진안군', '무주군', '장수군', '임실군', '순창군', '고창군', '부안군'],
        '전라남도': ['목포시', '여수시', '순천시', '나주시', '광양시', '담양군', '곡성군', '구례군', '고흥군', '보성군', '화순군', '장흥군', '강진군', '해남군', '영암군', '무안군', '함평군', '영광군', '장성군', '완도군', '진도군', '신안군'],
        '경상북도': ['포항시', '경주시', '김천시', '안동시', '구미시', '영주시', '영천시', '상주시', '문경시', '경산시', '군위군', '의성군', '청송군', '영양군', '영덕군', '청도군', '고령군', '성주군', '칠곡군', '예천군', '봉화군', '울진군', '울릉군'],
        '경상남도': ['창원시', '진주시', '통영시', '사천시', '김해시', '밀양시', '거제시', '양산시', '의령군', '함안군', '창녕군', '고성군', '남해군', '하동군', '산청군', '함양군', '거창군', '합천군'],
        '제주특별자치도': ['제주시', '서귀포시'],
      };
      setSigunguList(sigunguMap[sido] || []);
      setSigungu('');
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
          sigungu: sigungu || undefined
        }
      });

      if (response.data.success) {
        const { latitude, longitude, address } = response.data;
        const displayAddress = response.data.full_address || address;

        setMapCenter([latitude, longitude]);
        setMapZoom(17);

        const modeMsg = USE_DEMO_MODE ? ' 🎭 (데모 모드)' : '';
        setStatusMessage(`위치 찾음: ${displayAddress}${modeMsg}`);
        // Reset vehicle display when searching new location
        setShowVehicles(false);
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

  // DB에서 방치 차량 로드 (자동 분석 결과)
  // 관리자 대시보드 비밀번호 인증
  const handleAdminClick = () => {
    const password = prompt('관리자 비밀번호를 입력하세요:');
    if (password === 'Matthew0917') {
      setShowAdminDashboard(true);
    } else if (password !== null) {
      alert('❌ 비밀번호가 올바르지 않습니다.');
    }
  };

  const loadVehiclesFromDB = async () => {
    setLoadingVehicles(true);
    setStatusMessage('DB에서 방치 차량 로드 중...');

    try {
      // DB에서 방치 차량 조회 (필터: 현재 선택된 지역)
      const params: any = {
        min_similarity: 0.85,
        limit: 100
      };

      // 시/도 필터
      if (sido) {
        params.city = sido;
      }

      // 시/군/구 필터
      if (sigungu) {
        params.district = sigungu;
      }

      const response = await axios.get(`${API_BASE_URL}/abandoned-vehicles`, { params });

      if (response.data.success) {
        const abandonedVehicles = response.data.abandoned_vehicles || [];
        setVehicles(abandonedVehicles);

        if (abandonedVehicles.length === 0) {
          setStatusMessage(`✅ ${sido || '전국'} ${sigungu || ''} 지역에 방치 차량이 없습니다 (최근 자동 분석 결과)`);
        } else {
          setStatusMessage(`🔵 ${abandonedVehicles.length}대의 방치 차량 발견 (매일 0시, 12시 자동 업데이트)`);
        }
      } else {
        setStatusMessage('방치 차량 데이터를 불러올 수 없습니다');
      }
    } catch (error: any) {
      console.error('Load vehicles error:', error);
      setStatusMessage(`로드 실패: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingVehicles(false);
    }
  };

  // 방치 차량 표시 토글
  const handleToggleVehicles = async () => {
    if (!showVehicles) {
      // 표시 ON: DB에서 로드
      await loadVehiclesFromDB();
      setShowVehicles(true);
    } else {
      // 표시 OFF: 숨기기
      setVehicles([]);
      setShowVehicles(false);
      setStatusMessage('방치 차량 표시가 비활성화되었습니다');
    }
  };

  // 차량 클릭 시 위성사진 팝업
  const handleVehicleClick = (vehicle: AbandonedVehicle) => {
    setSelectedVehicle(vehicle);
    setShowSatellitePopup(true);
    // Reset zoom and pan
    setImageScale(1);
    setImagePosition({ x: 0, y: 0 });
    // 주변 CCTV 검색
    if (vehicle.latitude && vehicle.longitude) {
      fetchNearbyCCTVs(vehicle.latitude, vehicle.longitude);
    }
  };

  // 위성 이미지 줌/팬 핸들러
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    setImageScale(prev => Math.max(0.5, Math.min(5, prev + delta)));
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - imagePosition.x, y: e.clientY - imagePosition.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setImagePosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const resetZoom = () => {
    setImageScale(1);
    setImagePosition({ x: 0, y: 0 });
  };

  // 거리 계산 함수 (Haversine formula)
  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
    const R = 6371; // Earth radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c * 1000; // return in meters
  };

  // 주변 CCTV 검색
  const fetchNearbyCCTVs = async (lat: number, lon: number) => {
    setLoadingCCTV(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/vworld/cctv`, {
        params: { lat, lon, radius: 1000 }
      });

      if (response.data.success && response.data.cctv) {
        // 거리 계산 및 정렬
        const cctvWithDistance = response.data.cctv.map((cctv: CCTVLocation) => ({
          ...cctv,
          distance: calculateDistance(lat, lon, cctv.latitude, cctv.longitude)
        }));

        // 거리순으로 정렬
        cctvWithDistance.sort((a, b) => (a.distance || 0) - (b.distance || 0));

        setNearbyCCTVs(cctvWithDistance);
      } else {
        setNearbyCCTVs([]);
      }
    } catch (error) {
      console.error('CCTV 검색 실패:', error);
      setNearbyCCTVs([]);
    } finally {
      setLoadingCCTV(false);
    }
  };

  // 지도 이동 시 현재 위치 주소 가져오기 (역지오코딩)
  const handleMapMove = async (center: [number, number], zoom: number) => {
    setMapCenter(center);
    setMapZoom(zoom);

    // 줌 레벨이 충분히 크면 주소 표시 (14 이상)
    if (zoom >= 14) {
      setAddressLoading(true);
      try {
        // 백엔드 프록시를 통한 역지오코딩 (CORS 해결)
        const response = await axios.get(`${API_BASE_URL}/reverse-geocode`, {
          params: {
            lat: center[0],
            lon: center[1]
          },
          timeout: 5000  // 5초 타임아웃
        });

        if (response.data && response.data.success && response.data.address) {
          setCurrentAddress(response.data.address);
        } else {
          setCurrentAddress(`위도: ${center[0].toFixed(6)}, 경도: ${center[1].toFixed(6)}`);
        }
      } catch (error) {
        console.error('Reverse geocoding error:', error);
        // 에러 시 좌표만 표시 (network error 방지)
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
          <Select value={sido} onChange={(e) => setSido(e.target.value)} disabled={loading || loadingVehicles}>
            <option value="">시/도 선택</option>
            {sidoList.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </Select>

          <Select value={sigungu} onChange={(e) => setSigungu(e.target.value)} disabled={!sido || loading || loadingVehicles}>
            <option value="">시/군/구 선택</option>
            {sigunguList.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </Select>



          <SearchButton onClick={handleSearch} disabled={!sido || loading || loadingVehicles}>
            {loading ? <Loader size={20} className="spin" /> : <Search size={20} />}
            위치 검색
          </SearchButton>

          <ButtonGroup>
            <ToggleButton onClick={handleToggleVehicles} disabled={loadingVehicles} $active={showVehicles}>
              {loadingVehicles ? <Loader size={20} className="spin" /> : <MapPin size={20} />}
              {loadingVehicles ? '로드 중...' : showVehicles ? '방치 차량 숨기기' : '방치 차량 표시'}
            </ToggleButton>

            {showVehicles && vehicles.length > 0 && (
              <StatsButton onClick={() => setShowStatsDashboard(true)}>
                <BarChart3 size={20} />
                통계 대시보드
              </StatsButton>
            )}

            <AdminButton onClick={handleAdminClick}>
              <Settings size={20} />
              관리자
            </AdminButton>
          </ButtonGroup>
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
          <MapController center={mapCenter} zoom={mapZoom} />
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
        {showVehicles && vehicles.length > 0 && (
          <StatsOverlay>
            <StatItem>
              <StatLabel>방치 차량</StatLabel>
              <StatValue isClean={false}>
                {vehicles.length}대
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
              <div style={{display: 'flex', gap: '10px', alignItems: 'center'}}>
                <button
                  onClick={() => setImageScale(prev => Math.min(5, prev + 0.2))}
                  style={{
                    padding: '5px 10px',
                    background: '#4CAF50',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: 'bold'
                  }}
                >
                  +
                </button>
                <span style={{fontSize: '14px', fontWeight: 'bold', minWidth: '50px', textAlign: 'center'}}>
                  {Math.round(imageScale * 100)}%
                </span>
                <button
                  onClick={() => setImageScale(prev => Math.max(0.5, prev - 0.2))}
                  style={{
                    padding: '5px 10px',
                    background: '#f44336',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: 'bold'
                  }}
                >
                  -
                </button>
                <button
                  onClick={resetZoom}
                  style={{
                    padding: '5px 10px',
                    background: '#2196F3',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '12px'
                  }}
                >
                  Reset
                </button>
              </div>
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
                {selectedVehicle.latitude && selectedVehicle.longitude ? (
                  <SatelliteWrapper>
                    {/* 3x3 Grid of Satellite Tiles for better coverage */}
                    <SatelliteTileGrid
                      onWheel={handleWheel}
                      onMouseDown={handleMouseDown}
                      onMouseMove={handleMouseMove}
                      onMouseUp={handleMouseUp}
                      onMouseLeave={handleMouseUp}
                      style={{
                        transform: `translate(${imagePosition.x}px, ${imagePosition.y}px) scale(${imageScale})`,
                        cursor: isDragging ? 'grabbing' : 'grab',
                        transformOrigin: 'center center',
                        transition: isDragging ? 'none' : 'transform 0.1s ease-out',
                      }}
                    >
                      {(() => {
                        const zoom = 18;
                        const centerX = Math.floor((selectedVehicle.longitude + 180) / 360 * Math.pow(2, zoom));
                        const centerY = Math.floor((1 - Math.log(Math.tan(selectedVehicle.latitude * Math.PI / 180) + 1 / Math.cos(selectedVehicle.latitude * Math.PI / 180)) / Math.PI) / 2 * Math.pow(2, zoom));

                        const tiles = [];
                        for (let dy = -1; dy <= 1; dy++) {
                          for (let dx = -1; dx <= 1; dx++) {
                            const x = centerX + dx;
                            const y = centerY + dy;
                            tiles.push(
                              <SatelliteTile
                                key={`${x}-${y}`}
                                src={`https://mt1.google.com/vt/lyrs=s&x=${x}&y=${y}&z=${zoom}`}
                                alt="위성 항공사진"
                                onError={(e) => {
                                  // Fallback to Esri
                                  const esriUrl = `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${zoom}/${y}/${x}`;
                                  if (e.currentTarget.src.indexOf('google.com') !== -1) {
                                    e.currentTarget.src = esriUrl;
                                  }
                                }}
                              />
                            );
                          }
                        }
                        return tiles;
                      })()}

                      {/* 빨간 네모 박스 오버레이 (방치 차량 표시) - 이제 transform과 함께 움직임 */}
                      {selectedVehicle.bbox && (
                        <BoundingBoxOverlay>
                          <svg width="100%" height="100%" viewBox="0 0 768 768" preserveAspectRatio="none">
                            {/* 빨간 테두리 + 반투명 배경 */}
                            <rect
                              x={selectedVehicle.bbox.x}
                              y={selectedVehicle.bbox.y}
                              width={selectedVehicle.bbox.w}
                              height={selectedVehicle.bbox.h}
                              fill="rgba(255, 0, 0, 0.3)"
                              stroke="red"
                              strokeWidth="3"
                            />
                            {/* "방치 차량" 라벨 */}
                            <text
                              x={selectedVehicle.bbox.x + selectedVehicle.bbox.w / 2}
                              y={selectedVehicle.bbox.y - 10}
                              fill="red"
                              fontSize="20"
                              fontWeight="bold"
                              textAnchor="middle"
                              style={{ textShadow: '0 0 4px black, 0 0 8px black' }}
                            >
                              방치 차량
                            </text>
                          </svg>
                        </BoundingBoxOverlay>
                      )}
                    </SatelliteTileGrid>

                    <SatelliteImagePlaceholder style={{ display: 'none' }}>
                      <PlaceholderText>
                        항공사진 로드 실패
                        <br />
                        <small>좌표: {selectedVehicle.latitude.toFixed(6)}, {selectedVehicle.longitude.toFixed(6)}</small>
                      </PlaceholderText>
                    </SatelliteImagePlaceholder>
                  </SatelliteWrapper>
                ) : (
                  <SatelliteImagePlaceholder>
                    <PlaceholderText>
                      위치 정보 없음
                      <br />
                      <small>(좌표 데이터가 필요합니다)</small>
                    </PlaceholderText>
                  </SatelliteImagePlaceholder>
                )}
              </SatelliteImageContainer>

              {/* CCTV 검증 섹션 */}
              <CCTVVerificationSection>
                <CCTVSectionTitle>
                  <Camera size={20} />
                  CCTV 검증
                  {loadingCCTV && <LoadingDot>검색 중...</LoadingDot>}
                  {!loadingCCTV && nearbyCCTVs.length > 0 && (
                    <CCTVCount>{nearbyCCTVs.length}개 발견</CCTVCount>
                  )}
                </CCTVSectionTitle>

                {!loadingCCTV && nearbyCCTVs.length === 0 && (
                  <NoCCTVMessage>
                    주변에 검증 가능한 CCTV가 없습니다
                  </NoCCTVMessage>
                )}

                {!loadingCCTV && nearbyCCTVs.length > 0 && (
                  <>
                    <CCTVDescription>
                      거리순으로 정렬된 주변 CCTV 목록입니다. 클릭하여 상세 정보를 확인하세요.
                    </CCTVDescription>
                    <CCTVButton onClick={() => setShowCCTVVerification(true)}>
                      <Camera size={18} />
                      CCTV로 검증하기 ({nearbyCCTVs.length}개)
                    </CCTVButton>
                  </>
                )}
              </CCTVVerificationSection>
            </PopupBody>
          </PopupWindow>
        </SatellitePopup>
      )}

      {/* 통계 대시보드 모달 */}
      {showStatsDashboard && (
        <DashboardModal>
          <DashboardOverlay onClick={() => setShowStatsDashboard(false)} />
          <DashboardWindow>
            <DashboardHeader>
              <DashboardTitle>
                <BarChart3 size={28} />
                방치 차량 통계 대시보드
              </DashboardTitle>
              <DashboardCloseButton onClick={() => setShowStatsDashboard(false)}>✕</DashboardCloseButton>
            </DashboardHeader>
            <DashboardContent>
              <StatisticsDashboard vehicles={vehicles} />
            </DashboardContent>
          </DashboardWindow>
        </DashboardModal>
      )}

      {/* 관리자 대시보드 모달 */}
      {showAdminDashboard && (
        <DashboardModal>
          <DashboardOverlay onClick={() => setShowAdminDashboard(false)} />
          <DashboardWindow>
            <DashboardHeader>
              <DashboardTitle>
                <Settings size={28} />
                관리자 대시보드
              </DashboardTitle>
              <DashboardCloseButton onClick={() => setShowAdminDashboard(false)}>✕</DashboardCloseButton>
            </DashboardHeader>
            <DashboardContent>
              <AdminDashboard />
            </DashboardContent>
          </DashboardWindow>
        </DashboardModal>
      )}

      {/* CCTV 검증 팝업 */}
      {showCCTVVerification && selectedVehicle && (
        <SatellitePopup>
          <PopupOverlay onClick={() => setShowCCTVVerification(false)} />
          <PopupWindow style={{maxWidth: '700px'}}>
            <PopupHeader>
              <PopupWindowTitle>
                <Camera size={24} style={{marginRight: '8px'}} />
                CCTV 실시간 검증
              </PopupWindowTitle>
              <CloseButton onClick={() => setShowCCTVVerification(false)}>×</CloseButton>
            </PopupHeader>

            <PopupBody>
              {/* 방치 차량 정보 */}
              <CCTVPopupSection>
                <CCTVPopupSectionTitle>🚗 방치 차량 정보</CCTVPopupSectionTitle>
                <CCTVPopupText>
                  <strong>ID:</strong> {selectedVehicle.id}<br/>
                  <strong>유사도:</strong> {selectedVehicle.similarity_percentage}%<br/>
                  <strong>위험도:</strong> <RiskBadge level={selectedVehicle.risk_level}>
                    {selectedVehicle.risk_level}
                  </RiskBadge><br/>
                  <strong>경과 시간:</strong> {selectedVehicle.years_difference}년<br/>
                  <strong>위치:</strong> {selectedVehicle.latitude.toFixed(6)}, {selectedVehicle.longitude.toFixed(6)}
                </CCTVPopupText>
              </CCTVPopupSection>

              {/* CCTV 목록 */}
              <CCTVPopupSection>
                <CCTVPopupSectionTitle>📹 검증 가능한 CCTV (거리순)</CCTVPopupSectionTitle>
                {nearbyCCTVs.length === 0 ? (
                  <NoCCTVMessage>주변에 CCTV가 없습니다</NoCCTVMessage>
                ) : (
                  <CCTVList>
                    {nearbyCCTVs.slice(0, 5).map((cctv, index) => (
                      <CCTVListItem key={cctv.id}>
                        <CCTVItemNumber>#{index + 1}</CCTVItemNumber>
                        <CCTVItemInfo>
                          <CCTVItemName>{cctv.name}</CCTVItemName>
                          <CCTVItemDetails>
                            거리: {cctv.distance ? `${cctv.distance.toFixed(0)}m` : 'N/A'}
                            {cctv.type && ` • ${cctv.type}`}
                            {cctv.is_public && ' • 공개'}
                          </CCTVItemDetails>
                        </CCTVItemInfo>
                      </CCTVListItem>
                    ))}
                  </CCTVList>
                )}
              </CCTVPopupSection>

              {/* 실시간 영상 placeholder */}
              <CCTVPopupSection>
                <CCTVPopupSectionTitle>📺 실시간 영상</CCTVPopupSectionTitle>
                <CCTVStreamPlaceholder>
                  <Camera size={64} color="#6b7280" />
                  <CCTVPlaceholderText>
                    실제 운영 시 여기에 실시간 CCTV 영상이 표시됩니다
                  </CCTVPlaceholderText>
                  <CCTVPlaceholderSubtext>
                    지자체 CCTV 통합관제 시스템 연동 필요
                  </CCTVPlaceholderSubtext>
                </CCTVStreamPlaceholder>
              </CCTVPopupSection>
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

const ToggleButton = styled(SearchButton)<{ $active: boolean }>`
  background: ${props => props.$active ? 'linear-gradient(135deg, #10B981 0%, #059669 100%)' : 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)'};
  border: ${props => props.$active ? '2px solid #10B981' : 'none'};

  &:hover:not(:disabled) {
    background: ${props => props.$active ? 'linear-gradient(135deg, #059669 0%, #047857 100%)' : '#2563EB'};
    transform: translateY(-2px);
    box-shadow: 0 4px 12px ${props => props.$active ? 'rgba(16, 185, 129, 0.3)' : 'rgba(59, 130, 246, 0.3)'};
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
  position: relative;
`;

const SatelliteWrapper = styled.div`
  position: relative;
  width: 100%;
  height: 100%;
`;

const SatelliteTileGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  width: 100%;
  height: 100%;
  gap: 0;
`;

const SatelliteTile = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
`;

const BoundingBoxOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 10;

  svg {
    width: 100%;
    height: 100%;
  }
`;

const SatelliteImagePlaceholder = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  position: absolute;
  top: 0;
  left: 0;
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

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
`;

const StatsButton = styled(SearchButton)`
  background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%);

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const AdminButton = styled(SearchButton)`
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);

  &:hover {
    background: linear-gradient(135deg, #059669 0%, #047857 100%);
    transform: translateY(-2px);
  }
`;

const DashboardModal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const DashboardOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
`;

const DashboardWindow = styled.div`
  position: relative;
  width: 90vw;
  max-width: 1400px;
  max-height: 90vh;
  background: linear-gradient(135deg, #000 0%, #0a0a0a 100%);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 30px 80px rgba(0,0,0,0.9), 0 0 120px rgba(59, 130, 246, 0.2);
  z-index: 10001;
  display: flex;
  flex-direction: column;

  @media (max-width: 768px) {
    width: 95vw;
    max-height: 95vh;
  }
`;

const DashboardHeader = styled.div`
  padding: 24px 32px;
  background: linear-gradient(135deg, rgba(0,0,0,0.98) 0%, rgba(20,20,20,0.98) 100%);
  border-bottom: 1px solid rgba(59, 130, 246, 0.3);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
`;

const DashboardTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
`;

const DashboardContent = styled.div`
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;

  /* 커스텀 스크롤바 */
  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: #0a0a0a;
  }

  &::-webkit-scrollbar-thumb {
    background: #3B82F6;
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: #60A5FA;
  }
`;

const DashboardCloseButton = styled.button`
  background: none;
  border: none;
  color: #999;
  font-size: 32px;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  border-radius: 8px;

  &:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.1);
  }
`;

// CCTV 검증 관련 Styled Components
const CCTVVerificationSection = styled.div`
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #333;
`;

const CCTVSectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const CCTVCount = styled.span`
  font-size: 14px;
  color: #10b981;
  font-weight: 500;
  background: rgba(16, 185, 129, 0.1);
  padding: 4px 12px;
  border-radius: 12px;
  margin-left: auto;
`;

const LoadingDot = styled.span`
  font-size: 14px;
  color: #6b7280;
  font-weight: 400;
  margin-left: auto;
`;

const NoCCTVMessage = styled.p`
  font-size: 14px;
  color: #9ca3af;
  margin: 12px 0;
`;

const CCTVDescription = styled.p`
  font-size: 14px;
  color: #d1d5db;
  margin: 0 0 16px 0;
  line-height: 1.6;
`;

const CCTVButton = styled.button`
  width: 100%;
  padding: 14px 20px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  }

  &:active {
    transform: translateY(0);
  }
`;

// CCTV 팝업 관련 Styled Components
const CCTVPopupSection = styled.div`
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #333;

  &:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }
`;

const CCTVPopupSectionTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 12px 0;
`;

const CCTVPopupText = styled.p`
  font-size: 14px;
  line-height: 1.8;
  color: #d1d5db;
  margin: 0;

  strong {
    color: #fff;
    font-weight: 600;
  }
`;

const CCTVList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const CCTVListItem = styled.div`
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s ease;

  &:hover {
    border-color: #3b82f6;
    background: #222;
  }
`;

const CCTVItemNumber = styled.div`
  font-size: 14px;
  font-weight: 700;
  color: #3b82f6;
  min-width: 36px;
  text-align: center;
`;

const CCTVItemInfo = styled.div`
  flex: 1;
`;

const CCTVItemName = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
`;

const CCTVItemDetails = styled.div`
  font-size: 13px;
  color: #9ca3af;
`;

const CCTVStreamPlaceholder = styled.div`
  background: #0a0a0a;
  border: 2px dashed #333;
  border-radius: 12px;
  padding: 60px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
`;

const CCTVPlaceholderText = styled.p`
  font-size: 16px;
  color: #9ca3af;
  margin: 16px 0 0 0;
`;

const CCTVPlaceholderSubtext = styled.p`
  font-size: 13px;
  color: #6b7280;
  margin: 8px 0 0 0;
`;

export default MainDetectionPage;
