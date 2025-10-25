import React from 'react';
import styled from 'styled-components';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, AlertTriangle, MapPin, Calendar, Download } from 'lucide-react';

interface VehicleStats {
  total: number;
  byRiskLevel: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
  byVehicleType: {
    car: number;
    truck: number;
    bus: number;
  };
  byRegion: { name: string; count: number }[];
}

interface StatisticsDashboardProps {
  vehicles: Array<{
    id: string;
    risk_level: string;
    vehicle_type?: string;
    latitude: number;
    longitude: number;
  }>;
}

const StatisticsDashboard: React.FC<StatisticsDashboardProps> = ({ vehicles }) => {
  // 통계 계산
  const stats: VehicleStats = {
    total: vehicles.length,
    byRiskLevel: {
      CRITICAL: vehicles.filter(v => v.risk_level === 'CRITICAL').length,
      HIGH: vehicles.filter(v => v.risk_level === 'HIGH').length,
      MEDIUM: vehicles.filter(v => v.risk_level === 'MEDIUM').length,
      LOW: vehicles.filter(v => v.risk_level === 'LOW').length,
    },
    byVehicleType: {
      car: vehicles.filter(v => v.vehicle_type === 'car').length,
      truck: vehicles.filter(v => v.vehicle_type === 'truck').length,
      bus: vehicles.filter(v => v.vehicle_type === 'bus').length,
    },
    byRegion: [], // TODO: 지역별 집계 (현재는 더미 데이터)
  };

  // CSV 내보내기 함수
  const exportToCSV = () => {
    // CSV 헤더
    const headers = ['차량ID', '위도', '경도', '차량타입', '위험도', '유사도(%)', '년수차이'];

    // CSV 데이터 행
    const rows = vehicles.map((v, index) => [
      v.id || `vehicle_${index + 1}`,
      v.latitude.toFixed(6),
      v.longitude.toFixed(6),
      v.vehicle_type || 'unknown',
      v.risk_level,
      ((v as any).similarity_percentage || 0).toFixed(2),
      (v as any).years_difference || 0
    ]);

    // CSV 문자열 생성 (UTF-8 BOM 추가 for Excel 한글 지원)
    const BOM = '\uFEFF';
    const csvContent = BOM + [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    // Blob 생성 및 다운로드
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `abandoned_vehicles_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 위험도별 데이터 (파이 차트용)
  const riskLevelData = [
    { name: 'CRITICAL', value: stats.byRiskLevel.CRITICAL, color: '#DC2626' },
    { name: 'HIGH', value: stats.byRiskLevel.HIGH, color: '#EA580C' },
    { name: 'MEDIUM', value: stats.byRiskLevel.MEDIUM, color: '#F59E0B' },
    { name: 'LOW', value: stats.byRiskLevel.LOW, color: '#10B981' },
  ].filter(item => item.value > 0);

  // 차량 타입별 데이터 (막대 차트용)
  const vehicleTypeData = [
    { name: '승용차', count: stats.byVehicleType.car, color: '#3B82F6' },
    { name: '트럭', count: stats.byVehicleType.truck, color: '#8B5CF6' },
    { name: '버스', count: stats.byVehicleType.bus, color: '#EC4899' },
  ].filter(item => item.count > 0);

  // 데이터가 없으면 빈 상태 표시
  if (vehicles.length === 0) {
    return (
      <Container>
        <Header>
          <Title>
            <TrendingUp size={28} />
            방치 차량 통계 대시보드
          </Title>
        </Header>
        <EmptyState>
          <EmptyIcon>📊</EmptyIcon>
          <EmptyText>아직 분석된 방치 차량이 없습니다.</EmptyText>
          <EmptySubtext>위치를 선택하고 "방치 차량 분석"을 실행하세요.</EmptySubtext>
        </EmptyState>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <HeaderLeft>
          <Title>
            <TrendingUp size={28} />
            방치 차량 통계 대시보드
          </Title>
          <Subtitle>전체 {stats.total}대 발견</Subtitle>
        </HeaderLeft>
        <ExportButton onClick={exportToCSV}>
          <Download size={20} />
          CSV 내보내기
        </ExportButton>
      </Header>

      {/* 요약 카드 */}
      <SummaryCards>
        <SummaryCard color="#DC2626">
          <CardIcon>
            <AlertTriangle size={24} />
          </CardIcon>
          <CardContent>
            <CardLabel>긴급 조치 필요</CardLabel>
            <CardValue>{stats.byRiskLevel.CRITICAL}대</CardValue>
          </CardContent>
        </SummaryCard>

        <SummaryCard color="#EA580C">
          <CardIcon>
            <AlertTriangle size={24} />
          </CardIcon>
          <CardContent>
            <CardLabel>높은 위험도</CardLabel>
            <CardValue>{stats.byRiskLevel.HIGH}대</CardValue>
          </CardContent>
        </SummaryCard>

        <SummaryCard color="#F59E0B">
          <CardIcon>
            <MapPin size={24} />
          </CardIcon>
          <CardContent>
            <CardLabel>중간 위험도</CardLabel>
            <CardValue>{stats.byRiskLevel.MEDIUM}대</CardValue>
          </CardContent>
        </SummaryCard>

        <SummaryCard color="#10B981">
          <CardIcon>
            <Calendar size={24} />
          </CardIcon>
          <CardContent>
            <CardLabel>낮은 위험도</CardLabel>
            <CardValue>{stats.byRiskLevel.LOW}대</CardValue>
          </CardContent>
        </SummaryCard>
      </SummaryCards>

      {/* 차트 그리드 */}
      <ChartsGrid>
        {/* 위험도별 분포 (파이 차트) */}
        <ChartCard>
          <ChartTitle>위험도별 분포</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskLevelData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name} (${entry.value}대)`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {riskLevelData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <ChartLegend>
            {riskLevelData.map((item) => (
              <LegendItem key={item.name}>
                <LegendColor color={item.color} />
                <LegendText>{item.name}: {item.value}대</LegendText>
              </LegendItem>
            ))}
          </ChartLegend>
        </ChartCard>

        {/* 차량 타입별 분포 (막대 차트) */}
        <ChartCard>
          <ChartTitle>차량 타입별 분포</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={vehicleTypeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#999" />
              <YAxis stroke="#999" />
              <Tooltip
                contentStyle={{
                  background: '#1a1a1a',
                  border: '1px solid #333',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
              <Bar dataKey="count" fill="#3B82F6">
                {vehicleTypeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <ChartLegend>
            {vehicleTypeData.map((item) => (
              <LegendItem key={item.name}>
                <LegendColor color={item.color} />
                <LegendText>{item.name}: {item.count}대</LegendText>
              </LegendItem>
            ))}
          </ChartLegend>
        </ChartCard>
      </ChartsGrid>

      {/* 통계 정보 */}
      <StatsInfo>
        <InfoSection>
          <InfoTitle>📊 데이터 요약</InfoTitle>
          <InfoList>
            <InfoItem>
              <InfoLabel>총 방치 차량:</InfoLabel>
              <InfoValue>{stats.total}대</InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>긴급 조치 필요:</InfoLabel>
              <InfoValue style={{ color: '#DC2626' }}>
                {stats.byRiskLevel.CRITICAL}대
              </InfoValue>
            </InfoItem>
            <InfoItem>
              <InfoLabel>승용차 비율:</InfoLabel>
              <InfoValue>
                {stats.total > 0
                  ? ((stats.byVehicleType.car / stats.total) * 100).toFixed(1)
                  : 0}
                %
              </InfoValue>
            </InfoItem>
          </InfoList>
        </InfoSection>

        <InfoSection>
          <InfoTitle>⚠️ 위험도 분포</InfoTitle>
          <ProgressBars>
            <ProgressBar>
              <ProgressLabel>CRITICAL</ProgressLabel>
              <ProgressTrack>
                <ProgressFill
                  width={
                    stats.total > 0
                      ? (stats.byRiskLevel.CRITICAL / stats.total) * 100
                      : 0
                  }
                  color="#DC2626"
                />
              </ProgressTrack>
              <ProgressValue>
                {stats.total > 0
                  ? ((stats.byRiskLevel.CRITICAL / stats.total) * 100).toFixed(0)
                  : 0}
                %
              </ProgressValue>
            </ProgressBar>

            <ProgressBar>
              <ProgressLabel>HIGH</ProgressLabel>
              <ProgressTrack>
                <ProgressFill
                  width={
                    stats.total > 0
                      ? (stats.byRiskLevel.HIGH / stats.total) * 100
                      : 0
                  }
                  color="#EA580C"
                />
              </ProgressTrack>
              <ProgressValue>
                {stats.total > 0
                  ? ((stats.byRiskLevel.HIGH / stats.total) * 100).toFixed(0)
                  : 0}
                %
              </ProgressValue>
            </ProgressBar>

            <ProgressBar>
              <ProgressLabel>MEDIUM</ProgressLabel>
              <ProgressTrack>
                <ProgressFill
                  width={
                    stats.total > 0
                      ? (stats.byRiskLevel.MEDIUM / stats.total) * 100
                      : 0
                  }
                  color="#F59E0B"
                />
              </ProgressTrack>
              <ProgressValue>
                {stats.total > 0
                  ? ((stats.byRiskLevel.MEDIUM / stats.total) * 100).toFixed(0)
                  : 0}
                %
              </ProgressValue>
            </ProgressBar>

            <ProgressBar>
              <ProgressLabel>LOW</ProgressLabel>
              <ProgressTrack>
                <ProgressFill
                  width={
                    stats.total > 0 ? (stats.byRiskLevel.LOW / stats.total) * 100 : 0
                  }
                  color="#10B981"
                />
              </ProgressTrack>
              <ProgressValue>
                {stats.total > 0
                  ? ((stats.byRiskLevel.LOW / stats.total) * 100).toFixed(0)
                  : 0}
                %
              </ProgressValue>
            </ProgressBar>
          </ProgressBars>
        </InfoSection>
      </StatsInfo>
    </Container>
  );
};

// Styled Components
const Container = styled.div`
  width: 100%;
  padding: 30px;
  background: linear-gradient(135deg, #000 0%, #0a0a0a 100%);
  color: #fff;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  gap: 20px;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: stretch;
  }
`;

const HeaderLeft = styled.div`
  flex: 1;
`;

const ExportButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
  }

  &:active {
    transform: translateY(0);
  }

  @media (max-width: 768px) {
    width: 100%;
    justify-content: center;
  }
`;

const Title = styled.h2`
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
`;

const Subtitle = styled.p`
  font-size: 16px;
  color: #999;
  margin-left: 40px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 80px 20px;
`;

const EmptyIcon = styled.div`
  font-size: 64px;
  margin-bottom: 20px;
`;

const EmptyText = styled.p`
  font-size: 20px;
  color: #fff;
  margin-bottom: 8px;
`;

const EmptySubtext = styled.p`
  font-size: 14px;
  color: #666;
`;

const SummaryCards = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
`;

const SummaryCard = styled.div<{ color: string }>`
  background: linear-gradient(135deg, rgba(0,0,0,0.95) 0%, rgba(20,20,20,0.95) 100%);
  border: 1px solid ${props => props.color}33;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;

  &:hover {
    border-color: ${props => props.color};
    box-shadow: 0 8px 24px ${props => props.color}22;
    transform: translateY(-4px);
  }
`;

const CardIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  color: inherit;
`;

const CardContent = styled.div`
  flex: 1;
`;

const CardLabel = styled.div`
  font-size: 14px;
  color: #999;
  margin-bottom: 4px;
`;

const CardValue = styled.div`
  font-size: 28px;
  font-weight: 700;
  color: #fff;
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 40px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled.div`
  background: linear-gradient(135deg, rgba(0,0,0,0.95) 0%, rgba(20,20,20,0.95) 100%);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 16px;
  padding: 24px;
`;

const ChartTitle = styled.h3`
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 20px;
`;

const ChartLegend = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 16px;
  justify-content: center;
`;

const LegendItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const LegendColor = styled.div<{ color: string }>`
  width: 16px;
  height: 16px;
  border-radius: 4px;
  background: ${props => props.color};
`;

const LegendText = styled.span`
  font-size: 14px;
  color: #ccc;
`;

const StatsInfo = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
`;

const InfoSection = styled.div`
  background: linear-gradient(135deg, rgba(0,0,0,0.95) 0%, rgba(20,20,20,0.95) 100%);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 16px;
  padding: 24px;
`;

const InfoTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 16px;
`;

const InfoList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const InfoItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #222;

  &:last-child {
    border-bottom: none;
  }
`;

const InfoLabel = styled.span`
  font-size: 14px;
  color: #999;
`;

const InfoValue = styled.span`
  font-size: 16px;
  font-weight: 600;
  color: #fff;
`;

const ProgressBars = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const ProgressBar = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const ProgressLabel = styled.span`
  font-size: 12px;
  color: #999;
  width: 70px;
  text-align: right;
`;

const ProgressTrack = styled.div`
  flex: 1;
  height: 24px;
  background: #1a1a1a;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #333;
`;

const ProgressFill = styled.div<{ width: number; color: string }>`
  height: 100%;
  width: ${props => props.width}%;
  background: ${props => props.color};
  transition: width 0.5s ease;
  border-radius: 12px;
`;

const ProgressValue = styled.span`
  font-size: 14px;
  color: #fff;
  font-weight: 600;
  width: 50px;
  text-align: left;
`;

export default StatisticsDashboard;
