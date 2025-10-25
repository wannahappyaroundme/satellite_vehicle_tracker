import React, { useState } from 'react';
import styled from 'styled-components';
import { AlertTriangle, MapPin, Target, TrendingUp, Eye, AlertCircle } from 'lucide-react';
import { detectLongTermStopped, getAreaSummary } from '../services/api';

const PanelContainer = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
`;

const Section = styled.div`
  margin-bottom: 25px;
`;

const SectionTitle = styled.h3`
  margin: 0 0 15px 0;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const InputGroup = styled.div`
  margin-bottom: 15px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  font-weight: 500;
`;

const Input = styled.input`
  width: 100%;
  padding: 10px;
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 6px;
  background: rgba(255,255,255,0.1);
  color: white;
  font-size: 14px;

  &::placeholder {
    color: rgba(255,255,255,0.6);
  }

  &:focus {
    outline: none;
    border-color: rgba(255,255,255,0.5);
    background: rgba(255,255,255,0.15);
  }
`;

const Button = styled.button`
  width: 100%;
  padding: 12px;
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 6px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255,255,255,0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ResultsContainer = styled.div`
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 15px;
  margin-top: 15px;
`;

const RiskCard = styled.div<{ level: 'HIGH' | 'MEDIUM' | 'LOW' }>`
  background: ${props => 
    props.level === 'HIGH' ? 'rgba(231, 76, 60, 0.2)' :
    props.level === 'MEDIUM' ? 'rgba(243, 156, 18, 0.2)' :
    'rgba(39, 174, 96, 0.2)'
  };
  border: 1px solid ${props => 
    props.level === 'HIGH' ? 'rgba(231, 76, 60, 0.3)' :
    props.level === 'MEDIUM' ? 'rgba(243, 156, 18, 0.3)' :
    'rgba(39, 174, 96, 0.3)'
  };
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
`;

const RiskTitle = styled.div<{ level: 'HIGH' | 'MEDIUM' | 'LOW' }>`
  font-size: 16px;
  font-weight: 600;
  color: ${props => 
    props.level === 'HIGH' ? '#e74c3c' :
    props.level === 'MEDIUM' ? '#f39c12' :
    '#27ae60'
  };
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
`;

const StatGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 15px;
`;

const StatItem = styled.div`
  background: rgba(255,255,255,0.1);
  border-radius: 6px;
  padding: 10px;
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
`;

const StatLabel = styled.div`
  font-size: 12px;
  opacity: 0.8;
`;

const AlertList = styled.div`
  margin-top: 15px;
`;

const AlertItem = styled.div<{ severity: 'HIGH' | 'MEDIUM' | 'LOW' }>`
  background: ${props => 
    props.severity === 'HIGH' ? 'rgba(231, 76, 60, 0.1)' :
    props.severity === 'MEDIUM' ? 'rgba(243, 156, 18, 0.1)' :
    'rgba(52, 152, 219, 0.1)'
  };
  border-left: 3px solid ${props => 
    props.severity === 'HIGH' ? '#e74c3c' :
    props.severity === 'MEDIUM' ? '#f39c12' :
    '#3498db'
  };
  padding: 10px;
  margin-bottom: 8px;
  border-radius: 4px;
`;

const VehicleCard = styled.div`
  background: rgba(255,255,255,0.1);
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 8px;
  border: 1px solid rgba(255,255,255,0.2);
`;

const Coordinates = styled.div`
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  opacity: 0.7;
  margin-top: 5px;
`;

interface LongTermDetectorProps {
  onLocationSelect: (lat: number, lng: number) => void;
  onLoadingChange: (loading: boolean) => void;
}

const LongTermDetector: React.FC<LongTermDetectorProps> = ({
  onLocationSelect,
  onLoadingChange
}) => {
  const [coordinates, setCoordinates] = useState({
    lat: 40.7128,
    lng: -74.0060
  });
  const [radius, setRadius] = useState(0.01);
  const [daysBack, setDaysBack] = useState(7);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleLongTermDetection = async () => {
    setLoading(true);
    onLoadingChange(true);
    
    try {
      const analysis = await detectLongTermStopped({
        lat: coordinates.lat,
        lng: coordinates.lng,
        radius: radius,
        days_back: daysBack
      });
      
      setResults({ type: 'long_term', data: analysis });
    } catch (error) {
      console.error('Long-term detection error:', error);
      setResults({ type: 'error', message: 'Detection failed' });
    } finally {
      setLoading(false);
      onLoadingChange(false);
    }
  };

  const handleAreaSummary = async () => {
    setLoading(true);
    onLoadingChange(true);
    
    try {
      const summary = await getAreaSummary({
        lat: coordinates.lat,
        lng: coordinates.lng,
        radius: radius,
        days_back: daysBack
      });
      
      setResults({ type: 'summary', data: summary });
    } catch (error) {
      console.error('Area summary error:', error);
      setResults({ type: 'error', message: 'Summary failed' });
    } finally {
      setLoading(false);
      onLoadingChange(false);
    }
  };

  const renderResults = () => {
    if (!results) return null;

    if (results.type === 'error') {
      return (
        <ResultsContainer>
          <div style={{ color: '#e74c3c', fontSize: '14px' }}>
            <AlertCircle size={16} style={{ marginRight: '8px' }} />
            {results.message}
          </div>
        </ResultsContainer>
      );
    }

    if (results.type === 'long_term') {
      const data = results.data;
      return (
        <ResultsContainer>
          <SectionTitle>
            <AlertTriangle size={16} />
            Long-Term Stopped Vehicles
          </SectionTitle>

          <RiskCard level={data.risk_assessment.level}>
            <RiskTitle level={data.risk_assessment.level}>
              <AlertTriangle size={16} />
              {data.risk_assessment.level} RISK
            </RiskTitle>
            <div style={{ fontSize: '14px', marginBottom: '10px' }}>
              {data.risk_assessment.description}
            </div>
            
            <StatGrid>
              <StatItem>
                <StatValue>{data.total_vehicles_analyzed}</StatValue>
                <StatLabel>Total Vehicles</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{data.stopped_vehicles_found}</StatValue>
                <StatLabel>Stopped Vehicles</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{data.stop_clusters}</StatValue>
                <StatLabel>Stop Clusters</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{data.analysis_period_hours.toFixed(0)}h</StatValue>
                <StatLabel>Analysis Period</StatLabel>
              </StatItem>
            </StatGrid>

            {data.alerts.length > 0 && (
              <div>
                <h4 style={{ fontSize: '14px', marginBottom: '10px' }}>Alerts:</h4>
                <AlertList>
                  {data.alerts.map((alert: any, index: number) => (
                    <AlertItem key={index} severity={alert.severity}>
                      <strong>{alert.type}</strong>: {alert.message}
                      <br />
                      <small>{new Date(alert.timestamp).toLocaleString()}</small>
                    </AlertItem>
                  ))}
                </AlertList>
              </div>
            )}

            {data.risk_assessment.recommendations && (
              <div>
                <h4 style={{ fontSize: '14px', marginBottom: '10px' }}>Recommendations:</h4>
                <ul style={{ fontSize: '12px', paddingLeft: '20px' }}>
                  {data.risk_assessment.recommendations.map((rec: string, index: number) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </RiskCard>

          {data.stopped_vehicles.length > 0 && (
            <div>
              <h4 style={{ fontSize: '14px', marginBottom: '10px' }}>Stopped Vehicles:</h4>
              {data.stopped_vehicles.slice(0, 5).map((vehicle: any) => (
                <VehicleCard key={vehicle.vehicle_id}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <strong>{vehicle.vehicle_type}</strong>
                      <div style={{ fontSize: '12px', opacity: 0.8 }}>
                        Stopped for {vehicle.stop_duration_hours.toFixed(1)} hours
                      </div>
                    </div>
                    <div style={{ fontSize: '12px' }}>
                      {(vehicle.confidence * 100).toFixed(0)}% confidence
                    </div>
                  </div>
                  <Coordinates>
                    {vehicle.location.latitude.toFixed(6)}, {vehicle.location.longitude.toFixed(6)}
                  </Coordinates>
                  <Button 
                    style={{ marginTop: '8px', padding: '6px', fontSize: '12px' }}
                    onClick={() => onLocationSelect(vehicle.location.latitude, vehicle.location.longitude)}
                  >
                    <Eye size={12} />
                    View Location
                  </Button>
                </VehicleCard>
              ))}
            </div>
          )}
        </ResultsContainer>
      );
    }

    if (results.type === 'summary') {
      const data = results.data;
      return (
        <ResultsContainer>
          <SectionTitle>
            <TrendingUp size={16} />
            Area Summary
          </SectionTitle>

          <RiskCard level={data.risk_assessment.overall_risk}>
            <RiskTitle level={data.risk_assessment.overall_risk}>
              <Target size={16} />
              {data.risk_assessment.overall_risk} OVERALL RISK
            </RiskTitle>
            
            <StatGrid>
              <StatItem>
                <StatValue>{data.summary.total_vehicles}</StatValue>
                <StatLabel>Total Vehicles</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{data.summary.time_range_days}</StatValue>
                <StatLabel>Days Analyzed</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{data.long_term_analysis.stopped_vehicles_found}</StatValue>
                <StatLabel>Stopped Vehicles</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{data.storage_analysis.storage_potential.toFixed(0)}%</StatValue>
                <StatLabel>Storage Potential</StatLabel>
              </StatItem>
            </StatGrid>

            <div style={{ fontSize: '14px', marginBottom: '10px' }}>
              <strong>Vehicle Types:</strong> {Object.entries(data.summary.vehicle_types)
                .map(([type, count]) => `${type}: ${count}`)
                .join(', ')}
            </div>

            <div style={{ fontSize: '14px' }}>
              <strong>Analysis Period:</strong> {data.summary.analysis_period}
            </div>
          </RiskCard>
        </ResultsContainer>
      );
    }

    return null;
  };

  return (
    <PanelContainer>
      <Section>
        <SectionTitle>
          <MapPin size={16} />
          Analysis Location
        </SectionTitle>
        
        <InputGroup>
          <Label>Latitude</Label>
          <Input
            type="number"
            step="any"
            value={coordinates.lat}
            onChange={(e) => setCoordinates(prev => ({ ...prev, lat: parseFloat(e.target.value) }))}
            placeholder="40.7128"
          />
        </InputGroup>

        <InputGroup>
          <Label>Longitude</Label>
          <Input
            type="number"
            step="any"
            value={coordinates.lng}
            onChange={(e) => setCoordinates(prev => ({ ...prev, lng: parseFloat(e.target.value) }))}
            placeholder="-74.0060"
          />
        </InputGroup>

        <InputGroup>
          <Label>Search Radius (km)</Label>
          <Input
            type="number"
            step="0.001"
            value={radius}
            onChange={(e) => setRadius(parseFloat(e.target.value))}
            placeholder="0.01"
          />
        </InputGroup>

        <InputGroup>
          <Label>Days Back</Label>
          <Input
            type="number"
            min="1"
            max="30"
            value={daysBack}
            onChange={(e) => setDaysBack(parseInt(e.target.value))}
            placeholder="7"
          />
        </InputGroup>
      </Section>

      <Section>
        <Button onClick={handleLongTermDetection} disabled={loading}>
          <AlertTriangle size={16} />
          {loading ? 'Detecting...' : 'Detect Long-Term Stopped'}
        </Button>

        <Button 
          onClick={handleAreaSummary} 
          disabled={loading}
          style={{ marginTop: '10px', background: 'rgba(255,255,255,0.1)' }}
        >
          <TrendingUp size={16} />
          {loading ? 'Analyzing...' : 'Get Area Summary'}
        </Button>
      </Section>

      {renderResults()}
    </PanelContainer>
  );
};

export default LongTermDetector;
