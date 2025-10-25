import React from 'react';
import styled from 'styled-components';
import { Clock, Car, MapPin, AlertTriangle } from 'lucide-react';
import { VehicleData } from '../types';

const HoverCard = styled.div<{ visible: boolean; x: number; y: number }>`
  position: fixed;
  top: ${props => props.y}px;
  left: ${props => props.x}px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  padding: 20px;
  width: 320px;
  z-index: 1000;
  opacity: ${props => props.visible ? 1 : 0};
  visibility: ${props => props.visible ? 'visible' : 'hidden'};
  transition: all 0.2s ease;
  transform: ${props => props.visible ? 'translateY(0)' : 'translateY(-10px)'};
  pointer-events: none;
  
  &::before {
    content: '';
    position: absolute;
    top: -8px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-bottom: 8px solid white;
  }
`;

const VehicleImage = styled.div`
  width: 100%;
  height: 120px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 48px;
  margin-bottom: 15px;
  position: relative;
  overflow: hidden;
`;

const VehicleType = styled.div<{ type: string }>`
  position: absolute;
  top: 10px;
  right: 10px;
  background: ${props => 
    props.type === 'suv' ? '#e74c3c' :
    props.type === 'sports' ? '#f39c12' :
    props.type === 'truck' ? '#9b59b6' :
    props.type === 'sedan' ? '#3498db' :
    props.type === 'van' ? '#e67e22' :
    '#95a5a6'
  };
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
`;

const VehicleTitle = styled.h3`
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
`;

const VehicleSubtitle = styled.div`
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 15px;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 15px;
`;

const InfoItem = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #34495e;
`;

const InfoIcon = styled.div`
  color: #3498db;
  display: flex;
  align-items: center;
`;

const ConfidenceBar = styled.div`
  margin-bottom: 15px;
`;

const ConfidenceLabel = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
  font-size: 13px;
  color: #34495e;
`;

const ConfidenceFill = styled.div<{ confidence: number }>`
  height: 6px;
  background: ${props => 
    props.confidence > 0.8 ? '#27ae60' :
    props.confidence > 0.6 ? '#f39c12' : '#e74c3c'
  };
  border-radius: 3px;
  width: ${props => props.confidence * 100}%;
  transition: width 0.3s ease;
`;

const DurationInfo = styled.div<{ duration: number }>`
  background: ${props => 
    props.duration > 24 ? 'rgba(231, 76, 60, 0.1)' :
    props.duration > 12 ? 'rgba(243, 156, 18, 0.1)' :
    'rgba(52, 152, 219, 0.1)'
  };
  border: 1px solid ${props => 
    props.duration > 24 ? 'rgba(231, 76, 60, 0.3)' :
    props.duration > 12 ? 'rgba(243, 156, 18, 0.3)' :
    'rgba(52, 152, 219, 0.3)'
  };
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 15px;
`;

const DurationTitle = styled.div<{ duration: number }>`
  font-size: 14px;
  font-weight: 600;
  color: ${props => 
    props.duration > 24 ? '#e74c3c' :
    props.duration > 12 ? '#f39c12' :
    '#3498db'
  };
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 5px;
`;

const DurationText = styled.div`
  font-size: 13px;
  color: #34495e;
`;

const RiskIndicator = styled.div<{ risk: 'HIGH' | 'MEDIUM' | 'LOW' }>`
  background: ${props => 
    props.risk === 'HIGH' ? 'rgba(231, 76, 60, 0.1)' :
    props.risk === 'MEDIUM' ? 'rgba(243, 156, 18, 0.1)' :
    'rgba(39, 174, 96, 0.1)'
  };
  border: 1px solid ${props => 
    props.risk === 'HIGH' ? 'rgba(231, 76, 60, 0.3)' :
    props.risk === 'MEDIUM' ? 'rgba(243, 156, 18, 0.3)' :
    'rgba(39, 174, 96, 0.3)'
  };
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 500;
  color: ${props => 
    props.risk === 'HIGH' ? '#e74c3c' :
    props.risk === 'MEDIUM' ? '#f39c12' :
    '#27ae60'
  };
  display: flex;
  align-items: center;
  gap: 6px;
`;

const Coordinates = styled.div`
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 11px;
  color: #95a5a6;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #ecf0f1;
`;

interface VehicleHoverCardProps {
  vehicle: VehicleData | null;
  visible: boolean;
  position: { x: number; y: number };
}

const VehicleHoverCard: React.FC<VehicleHoverCardProps> = ({ vehicle, visible, position }) => {
  // Return null early if vehicle is not provided
  if (!vehicle) {
    return null;
  }
  
  // Calculate parking duration (mock data for now)
  const parkingDuration = 18.5; // hours
  const riskLevel = parkingDuration > 24 ? 'HIGH' : parkingDuration > 12 ? 'MEDIUM' : 'LOW';
  
  // Get vehicle type icon
  const getVehicleIcon = (type: string) => {
    switch (type) {
      case 'suv': return '🚗';
      case 'sports': return '🏎️';
      case 'truck': return '🚛';
      case 'sedan': return '🚙';
      case 'van': return '🚐';
      case 'bus': return '🚌';
      case 'motorcycle': return '🏍️';
      default: return '🚗';
    }
  };

  // Format duration
  const formatDuration = (hours: number) => {
    if (hours >= 24) {
      const days = Math.floor(hours / 24);
      const remainingHours = Math.floor(hours % 24);
      return `${days}d ${remainingHours}h`;
    }
    return `${Math.floor(hours)}h ${Math.floor((hours % 1) * 60)}m`;
  };

  // Get confidence color
  const getConfidenceColor = (confidence: number) => {
    if (confidence > 0.8) return '#27ae60';
    if (confidence > 0.6) return '#f39c12';
    return '#e74c3c';
  };

  return (
    <HoverCard visible={visible} x={position.x} y={position.y}>
      <VehicleImage>
        <VehicleType type={vehicle.type}>
          {vehicle.type}
        </VehicleType>
        {getVehicleIcon(vehicle.type)}
      </VehicleImage>

      <VehicleTitle>
        {vehicle.type.charAt(0).toUpperCase() + vehicle.type.slice(1)} Vehicle
      </VehicleTitle>

      <VehicleSubtitle>
        Detected at {new Date(vehicle.timestamp).toLocaleString()}
      </VehicleSubtitle>

      <InfoGrid>
        <InfoItem>
          <InfoIcon>
            <Car size={14} />
          </InfoIcon>
          {vehicle.type}
        </InfoItem>
        <InfoItem>
          <InfoIcon>
            <MapPin size={14} />
          </InfoIcon>
          ID: {vehicle.id}
        </InfoItem>
      </InfoGrid>

      <ConfidenceBar>
        <ConfidenceLabel>
          <span>Detection Confidence</span>
          <span style={{ color: getConfidenceColor(vehicle.confidence) }}>
            {(vehicle.confidence * 100).toFixed(1)}%
          </span>
        </ConfidenceLabel>
        <div style={{ 
          height: '6px', 
          background: '#ecf0f1', 
          borderRadius: '3px', 
          overflow: 'hidden' 
        }}>
          <ConfidenceFill confidence={vehicle.confidence} />
        </div>
      </ConfidenceBar>

      <DurationInfo duration={parkingDuration}>
        <DurationTitle duration={parkingDuration}>
          <Clock size={14} />
          Parking Duration
        </DurationTitle>
        <DurationText>
          {formatDuration(parkingDuration)} parked
          {parkingDuration > 24 && ' (Long-term)'}
        </DurationText>
      </DurationInfo>

      <RiskIndicator risk={riskLevel}>
        <AlertTriangle size={12} />
        {riskLevel} RISK
        {riskLevel === 'HIGH' && ' - Investigation Recommended'}
      </RiskIndicator>

      <Coordinates>
        {vehicle.latitude.toFixed(6)}, {vehicle.longitude.toFixed(6)}
      </Coordinates>
    </HoverCard>
  );
};

export default VehicleHoverCard;
