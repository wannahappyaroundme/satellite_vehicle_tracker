import React, { useState } from 'react';
import styled from 'styled-components';
import { AlertTriangle, Camera, MapPin, Calendar, TrendingUp, Search } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface AbandonedVehicle {
  parking_space_id: string;
  year1: number;
  year2: number;
  years_difference: number;
  similarity_score: number;
  similarity_percentage: number;
  threshold: number;
  is_abandoned: boolean;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: string;
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
  stream_url: string;
  is_public: boolean;
}

interface AnalysisResult {
  success: boolean;
  status_message?: string;
  status_message_en?: string;
  metadata: {
    image1: any;
    image2: any;
    years_difference: number;
  };
  analysis: {
    total_parking_spaces_detected: number;
    spaces_analyzed: number;
    abandoned_vehicles_found: number;
    detection_threshold: number;
    is_clean?: boolean;
  };
  results: AbandonedVehicle[];
  abandoned_vehicles: AbandonedVehicle[];
  visualization_path?: string;
  cctv_locations: CCTVLocation[];
}

const AbandonedVehiclePanel: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [selectedVehicle, setSelectedVehicle] = useState<AbandonedVehicle | null>(null);
  const [selectedCCTV, setSelectedCCTV] = useState<CCTVLocation | null>(null);
  const [showCCTVPopup, setShowCCTVPopup] = useState(false);
  const [searchAddress, setSearchAddress] = useState('');
  const [showLocationSearch, setShowLocationSearch] = useState(false);

  const runAnalysis = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/compare-samples`);
      setResults(response.data);
    } catch (error: any) {
      console.error('Analysis failed:', error);
      alert(`분석 실패: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const analyzeRealLocation = async () => {
    if (!searchAddress.trim()) {
      alert('주소를 입력하세요');
      return;
    }

    setLoading(true);
    try {
      // 1. 주소 → 좌표 변환
      const addressResponse = await axios.get(`${API_BASE_URL}/api/search-address`, {
        params: { query: searchAddress }
      });

      if (!addressResponse.data.latitude || !addressResponse.data.longitude) {
        alert('주소를 찾을 수 없습니다');
        return;
      }

      const { latitude, longitude, address: fullAddress } = addressResponse.data;

      // 2. 해당 위치 방치차량 분석 (데모 모드)
      const analysisResponse = await axios.post(`${API_BASE_URL}/api/analyze-location`, null, {
        params: {
          latitude,
          longitude,
          address: fullAddress || searchAddress,
          use_real_api: false  // API 키가 유효하면 true로 변경
        }
      });

      setResults(analysisResponse.data);
      setShowLocationSearch(false);
    } catch (error: any) {
      console.error('Location analysis failed:', error);
      alert(`위치 분석 실패: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const openCCTVVerification = (vehicle: AbandonedVehicle) => {
    setSelectedVehicle(vehicle);
    // Find nearest CCTV
    if (results?.cctv_locations && results.cctv_locations.length > 0) {
      setSelectedCCTV(results.cctv_locations[0]); // For demo, use first CCTV
      setShowCCTVPopup(true);
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'CRITICAL':
        return '#dc2626';
      case 'HIGH':
        return '#ea580c';
      case 'MEDIUM':
        return '#f59e0b';
      case 'LOW':
        return '#10b981';
      default:
        return '#6b7280';
    }
  };

  return (
    <Container>
      <Header>
        <Title>
          <AlertTriangle size={28} color="#ef4444" />
          장기 방치 차량 탐지
        </Title>
        <Subtitle>국토정보플랫폼 항공사진 기반 연도별 비교 분석</Subtitle>
      </Header>

      <ActionSection>
        <InfoBox>
          <InfoTitle>📊 분석 방법</InfoTitle>
          <InfoText>
            • <strong>데이터 출처:</strong> 국토지리정보원 항공사진<br />
            • <strong>비교 연도:</strong> 2015년 vs 2020년 (5년 차이)<br />
            • <strong>탐지 기술:</strong> ResNet 특징 추출 + 코사인 유사도<br />
            • <strong>판정 기준:</strong> 유사도 90% 이상 = 방치 의심
          </InfoText>
        </InfoBox>

        <AnalyzeButton onClick={runAnalysis} disabled={loading}>
          {loading ? '분석 중...' : '샘플 이미지 분석 시작'}
        </AnalyzeButton>

        <LocationSearchSection>
          <LocationSearchButton onClick={() => setShowLocationSearch(!showLocationSearch)}>
            <MapPin size={16} />
            {showLocationSearch ? '위치 검색 닫기' : '실제 위치 분석하기'}
          </LocationSearchButton>

          {showLocationSearch && (
            <LocationSearchBox>
              <LocationInput
                type="text"
                value={searchAddress}
                onChange={(e) => setSearchAddress(e.target.value)}
                placeholder="주소 입력 (예: 서울특별시 강남구)"
                onKeyPress={(e) => e.key === 'Enter' && analyzeRealLocation()}
              />
              <LocationAnalyzeButton onClick={analyzeRealLocation} disabled={loading}>
                <Search size={16} />
                분석 시작
              </LocationAnalyzeButton>
            </LocationSearchBox>
          )}
        </LocationSearchSection>
      </ActionSection>

      {results && (
        <>
          {results.status_message && (
            <StatusMessage isClean={results.analysis.is_clean}>
              {results.status_message}
            </StatusMessage>
          )}

          <ResultsSection>
            <SectionTitle>📈 분석 결과</SectionTitle>

            <StatsGrid>
              <StatCard>
                <StatLabel>탐지된 주차 공간</StatLabel>
                <StatValue>{results.analysis.total_parking_spaces_detected}</StatValue>
              </StatCard>
              <StatCard>
                <StatLabel>분석된 공간</StatLabel>
                <StatValue>{results.analysis.spaces_analyzed}</StatValue>
              </StatCard>
              <StatCard highlight>
                <StatLabel>방치 차량 발견</StatLabel>
                <StatValue>{results.analysis.abandoned_vehicles_found}</StatValue>
              </StatCard>
              <StatCard>
                <StatLabel>탐지 임계값</StatLabel>
                <StatValue>{(results.analysis.detection_threshold * 100).toFixed(0)}%</StatValue>
              </StatCard>
            </StatsGrid>

            <MetadataSection>
              <MetadataCard>
                <MetadataTitle>📅 2015년 항공사진</MetadataTitle>
                <MetadataText>
                  촬영일: {results.metadata.image1.date}<br />
                  위치: {results.metadata.image1.location}
                </MetadataText>
              </MetadataCard>
              <MetadataCard>
                <MetadataTitle>📅 2020년 항공사진</MetadataTitle>
                <MetadataText>
                  촬영일: {results.metadata.image2.date}<br />
                  위치: {results.metadata.image2.location}
                </MetadataText>
              </MetadataCard>
            </MetadataSection>
          </ResultsSection>

          {results.abandoned_vehicles.length > 0 ? (
            <AbandonedVehiclesSection>
              <SectionTitle>
                🚨 방치 의심 차량 목록
                <Badge>{results.abandoned_vehicles.length}건</Badge>
              </SectionTitle>

              <VehicleList>
                {results.abandoned_vehicles.map((vehicle, index) => (
                  <VehicleCard
                    key={index}
                    riskColor={getRiskColor(vehicle.risk_level)}
                    onClick={() => openCCTVVerification(vehicle)}
                  >
                    <VehicleHeader>
                      <VehicleId>{vehicle.parking_space_id}</VehicleId>
                      <RiskBadge riskLevel={vehicle.risk_level}>
                        {vehicle.risk_level}
                      </RiskBadge>
                    </VehicleHeader>

                    <VehicleDetails>
                      <DetailRow>
                        <TrendingUp size={16} />
                        <DetailText>
                          유사도: <strong>{vehicle.similarity_percentage}%</strong>
                        </DetailText>
                      </DetailRow>
                      <DetailRow>
                        <Calendar size={16} />
                        <DetailText>
                          {vehicle.year1}년 → {vehicle.year2}년 ({vehicle.years_difference}년 경과)
                        </DetailText>
                      </DetailRow>
                      {vehicle.bbox && (
                        <DetailRow>
                          <MapPin size={16} />
                          <DetailText>
                            위치: x={vehicle.bbox.x}, y={vehicle.bbox.y}
                          </DetailText>
                        </DetailRow>
                      )}
                    </VehicleDetails>

                    <VerifyButton>
                      <Camera size={16} />
                      CCTV로 검증하기
                    </VerifyButton>
                  </VehicleCard>
                ))}
              </VehicleList>
            </AbandonedVehiclesSection>
          ) : (
            <NoAbandonedVehiclesSection>
              <NoVehiclesIcon>✅</NoVehiclesIcon>
              <NoVehiclesTitle>방치 차량이 발견되지 않았습니다</NoVehiclesTitle>
              <NoVehiclesText>
                분석 결과, 유사도 {(results.analysis.detection_threshold * 100).toFixed(0)}% 이상인 방치 의심 차량이 없습니다.
                <br />
                해당 지역은 정상적으로 관리되고 있는 것으로 보입니다.
              </NoVehiclesText>
              <NoVehiclesStats>
                <StatItem>
                  <StatItemLabel>분석된 주차 공간</StatItemLabel>
                  <StatItemValue>{results.analysis.spaces_analyzed}개</StatItemValue>
                </StatItem>
                <StatItem>
                  <StatItemLabel>탐지 임계값</StatItemLabel>
                  <StatItemValue>{(results.analysis.detection_threshold * 100).toFixed(0)}%</StatItemValue>
                </StatItem>
              </NoVehiclesStats>
            </NoAbandonedVehiclesSection>
          )}

          {results.cctv_locations && results.cctv_locations.length > 0 && (
            <CCTVSection>
              <SectionTitle>📹 검증 가능한 CCTV</SectionTitle>
              <CCTVGrid>
                {results.cctv_locations.map((cctv) => (
                  <CCTVCard key={cctv.id}>
                    <CCTVName>{cctv.name}</CCTVName>
                    <CCTVInfo>
                      위치: {cctv.latitude.toFixed(4)}, {cctv.longitude.toFixed(4)}
                    </CCTVInfo>
                    <CCTVStatus>
                      {cctv.is_public ? '🟢 공개' : '🔒 비공개'}
                    </CCTVStatus>
                  </CCTVCard>
                ))}
              </CCTVGrid>
            </CCTVSection>
          )}
        </>
      )}

      {/* CCTV Verification Popup */}
      {showCCTVPopup && selectedCCTV && selectedVehicle && (
        <Popup>
          <PopupOverlay onClick={() => setShowCCTVPopup(false)} />
          <PopupContent>
            <PopupHeader>
              <Camera size={24} />
              <PopupTitle>CCTV 실시간 검증</PopupTitle>
              <CloseButton onClick={() => setShowCCTVPopup(false)}>✕</CloseButton>
            </PopupHeader>

            <PopupBody>
              <PopupSection>
                <PopupSectionTitle>🚗 방치 차량 정보</PopupSectionTitle>
                <PopupText>
                  ID: {selectedVehicle.parking_space_id}<br />
                  유사도: {selectedVehicle.similarity_percentage}%<br />
                  위험도: <RiskBadge riskLevel={selectedVehicle.risk_level}>
                    {selectedVehicle.risk_level}
                  </RiskBadge>
                </PopupText>
              </PopupSection>

              <PopupSection>
                <PopupSectionTitle>📹 CCTV 정보</PopupSectionTitle>
                <PopupText>
                  {selectedCCTV.name}<br />
                  위치: {selectedCCTV.latitude}, {selectedCCTV.longitude}
                </PopupText>
              </PopupSection>

              <CCTVStreamPlaceholder>
                <Camera size={64} color="#9ca3af" />
                <PlaceholderText>
                  실제 운영 시 여기에 실시간 CCTV 영상이 표시됩니다
                </PlaceholderText>
                <PlaceholderSubtext>
                  Stream URL: {selectedCCTV.stream_url}
                </PlaceholderSubtext>
              </CCTVStreamPlaceholder>
            </PopupBody>
          </PopupContent>
        </Popup>
      )}
    </Container>
  );
};

// Styled Components
const Container = styled.div`
  padding: 20px;
  background: #0a0a0a;
  color: #fff;
  min-height: 100vh;
`;

const Header = styled.div`
  margin-bottom: 30px;
`;

const Title = styled.h1`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
`;

const Subtitle = styled.p`
  font-size: 16px;
  color: #9ca3af;
  margin: 0;
`;

const ActionSection = styled.div`
  margin-bottom: 30px;
`;

const StatusMessage = styled.div<{ isClean?: boolean }>`
  background: ${props => props.isClean
    ? 'linear-gradient(135deg, #064e3b 0%, #065f46 100%)'
    : 'linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%)'
  };
  border: 2px solid ${props => props.isClean ? '#10b981' : '#ef4444'};
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  text-align: center;
  box-shadow: 0 4px 12px ${props => props.isClean ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'};
`;

const InfoBox = styled.div`
  background: #1f1f1f;
  border: 1px solid #ff6b35;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
`;

const InfoTitle = styled.h3`
  font-size: 18px;
  margin: 0 0 12px 0;
  color: #ff6b35;
`;

const InfoText = styled.p`
  font-size: 14px;
  line-height: 1.8;
  margin: 0;
  color: #d1d5db;
`;

const AnalyzeButton = styled.button`
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(255, 107, 53, 0.4);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const LocationSearchSection = styled.div`
  margin-top: 20px;
`;

const LocationSearchButton = styled.button`
  width: 100%;
  padding: 14px;
  background: #1f1f1f;
  color: #fff;
  border: 2px solid #ff6b35;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;

  &:hover {
    background: #ff6b35;
    transform: translateY(-2px);
  }
`;

const LocationSearchBox = styled.div`
  margin-top: 16px;
  display: flex;
  gap: 12px;
`;

const LocationInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  background: #1f1f1f;
  border: 1px solid #333;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;

  &::placeholder {
    color: #666;
  }

  &:focus {
    outline: none;
    border-color: #ff6b35;
  }
`;

const LocationAnalyzeButton = styled.button`
  padding: 12px 24px;
  background: #ff6b35;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;

  &:hover:not(:disabled) {
    background: #f7931e;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ResultsSection = styled.div`
  margin-bottom: 30px;
`;

const SectionTitle = styled.h2`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  margin: 0 0 20px 0;
  color: #fff;
`;

const Badge = styled.span`
  background: #ff6b35;
  color: #fff;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  margin-left: 8px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
`;

const StatCard = styled.div<{ highlight?: boolean }>`
  background: ${props => props.highlight ? 'linear-gradient(135deg, #ff6b35 0%, #f7931e 100%)' : '#1f1f1f'};
  border: 1px solid ${props => props.highlight ? '#ff6b35' : '#333'};
  border-radius: 12px;
  padding: 20px;
  text-align: center;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: #9ca3af;
  margin-bottom: 8px;
`;

const StatValue = styled.div`
  font-size: 32px;
  font-weight: 700;
  color: #fff;
`;

const MetadataSection = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
`;

const MetadataCard = styled.div`
  background: #1f1f1f;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 20px;
`;

const MetadataTitle = styled.h4`
  font-size: 16px;
  color: #ff6b35;
  margin: 0 0 12px 0;
`;

const MetadataText = styled.p`
  font-size: 14px;
  line-height: 1.8;
  color: #d1d5db;
  margin: 0;
`;

const AbandonedVehiclesSection = styled.div`
  margin-bottom: 30px;
`;

const NoAbandonedVehiclesSection = styled.div`
  margin-bottom: 30px;
  background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
  border: 2px solid #10b981;
  border-radius: 16px;
  padding: 48px 32px;
  text-align: center;
`;

const NoVehiclesIcon = styled.div`
  font-size: 64px;
  margin-bottom: 20px;
`;

const NoVehiclesTitle = styled.h2`
  font-size: 28px;
  color: #fff;
  margin: 0 0 16px 0;
  font-weight: 700;
`;

const NoVehiclesText = styled.p`
  font-size: 16px;
  line-height: 1.8;
  color: #d1fae5;
  margin: 0 0 32px 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
`;

const NoVehiclesStats = styled.div`
  display: flex;
  justify-content: center;
  gap: 48px;
  flex-wrap: wrap;
`;

const StatItem = styled.div`
  text-align: center;
`;

const StatItemLabel = styled.div`
  font-size: 14px;
  color: #a7f3d0;
  margin-bottom: 8px;
`;

const StatItemValue = styled.div`
  font-size: 32px;
  font-weight: 700;
  color: #fff;
`;

const VehicleList = styled.div`
  display: grid;
  gap: 16px;
`;

const VehicleCard = styled.div<{ riskColor: string }>`
  background: #1f1f1f;
  border: 2px solid ${props => props.riskColor};
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px ${props => props.riskColor}40;
  }
`;

const VehicleHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
`;

const VehicleId = styled.h3`
  font-size: 18px;
  color: #fff;
  margin: 0;
`;

const RiskBadge = styled.span<{ riskLevel: string }>`
  background: ${props => getRiskColor(props.riskLevel)};
  color: #fff;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
`;

const VehicleDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
`;

const DetailRow = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: #9ca3af;
  font-size: 14px;
`;

const DetailText = styled.span`
  color: #d1d5db;
`;

const VerifyButton = styled.button`
  width: 100%;
  padding: 12px;
  background: #374151;
  color: #fff;
  border: 1px solid #4b5563;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: #4b5563;
    border-color: #6b7280;
  }
`;

const CCTVSection = styled.div`
  margin-bottom: 30px;
`;

const CCTVGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
`;

const CCTVCard = styled.div`
  background: #1f1f1f;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 20px;
`;

const CCTVName = styled.h4`
  font-size: 16px;
  color: #fff;
  margin: 0 0 8px 0;
`;

const CCTVInfo = styled.p`
  font-size: 13px;
  color: #9ca3af;
  margin: 0 0 8px 0;
`;

const CCTVStatus = styled.div`
  font-size: 14px;
  color: #10b981;
  font-weight: 600;
`;

// Popup styles
const Popup = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
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
  background: rgba(0, 0, 0, 0.8);
`;

const PopupContent = styled.div`
  position: relative;
  background: #1f1f1f;
  border: 1px solid #ff6b35;
  border-radius: 16px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  z-index: 1001;
`;

const PopupHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px;
  border-bottom: 1px solid #333;
`;

const PopupTitle = styled.h2`
  flex: 1;
  font-size: 24px;
  color: #fff;
  margin: 0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 28px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    color: #fff;
  }
`;

const PopupBody = styled.div`
  padding: 24px;
`;

const PopupSection = styled.div`
  margin-bottom: 24px;
`;

const PopupSectionTitle = styled.h3`
  font-size: 16px;
  color: #ff6b35;
  margin: 0 0 12px 0;
`;

const PopupText = styled.p`
  font-size: 14px;
  line-height: 1.8;
  color: #d1d5db;
  margin: 0;
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

const PlaceholderText = styled.div`
  color: #9ca3af;
  font-size: 16px;
  margin: 16px 0 8px 0;
`;

const PlaceholderSubtext = styled.div`
  color: #6b7280;
  font-size: 12px;
  font-family: monospace;
`;

// Helper function
function getRiskColor(riskLevel: string): string {
  switch (riskLevel) {
    case 'CRITICAL':
      return '#dc2626';
    case 'HIGH':
      return '#ea580c';
    case 'MEDIUM':
      return '#f59e0b';
    case 'LOW':
      return '#10b981';
    default:
      return '#6b7280';
  }
}

export default AbandonedVehiclePanel;
