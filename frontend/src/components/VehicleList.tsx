import React from 'react';
import styled from 'styled-components';
import { Car, Clock, MapPin, Eye, Filter } from 'lucide-react';
import { VehicleData } from '../types';

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

const VehicleCard = styled.div`
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 12px;
  border: 1px solid rgba(255,255,255,0.2);
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255,255,255,0.15);
    border-color: rgba(255,255,255,0.3);
  }
`;

const VehicleHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: between;
  margin-bottom: 10px;
`;

const VehicleType = styled.div<{ type: string }>`
  background: ${props => 
    props.type === 'aircraft' ? '#e74c3c' :
    props.type === 'truck' ? '#f39c12' :
    props.type === 'bus' ? '#9b59b6' :
    props.type === 'motorcycle' ? '#e67e22' :
    '#3498db'
  };
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  text-transform: capitalize;
`;

const ConfidenceBadge = styled.div<{ confidence: number }>`
  background: ${props => 
    props.confidence > 0.8 ? '#27ae60' :
    props.confidence > 0.6 ? '#f39c12' : '#e74c3c'
  };
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
  margin-left: auto;
`;

const VehicleInfo = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  font-size: 13px;
`;

const InfoItem = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  opacity: 0.8;
`;

const Coordinates = styled.div`
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  opacity: 0.7;
  margin-top: 8px;
`;

const ActionButton = styled.button`
  width: 100%;
  padding: 8px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 4px;
  color: white;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s ease;
  margin-top: 10px;

  &:hover {
    background: rgba(255,255,255,0.2);
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  opacity: 0.6;
`;

const EmptyIcon = styled.div`
  font-size: 48px;
  margin-bottom: 15px;
  opacity: 0.5;
`;

const FilterContainer = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
`;

const FilterButton = styled.button<{ active: boolean }>`
  padding: 6px 12px;
  background: ${props => props.active ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.1)'};
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 16px;
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255,255,255,0.2);
  }
`;

interface VehicleListProps {
  vehicles: VehicleData[];
  onVehicleSelect: (vehicle: VehicleData) => void;
}

const VehicleList: React.FC<VehicleListProps> = ({ vehicles, onVehicleSelect }) => {
  const [filter, setFilter] = React.useState<string>('all');
  const [sortBy, setSortBy] = React.useState<'timestamp' | 'confidence' | 'type'>('timestamp');

  const filteredVehicles = React.useMemo(() => {
    let filtered = vehicles;

    if (filter !== 'all') {
      filtered = filtered.filter(v => v.type === filter);
    }

    return filtered.sort((a, b) => {
      switch (sortBy) {
        case 'timestamp':
          return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
        case 'confidence':
          return b.confidence - a.confidence;
        case 'type':
          return a.type.localeCompare(b.type);
        default:
          return 0;
      }
    });
  }, [vehicles, filter, sortBy]);

  const vehicleTypes = React.useMemo(() => {
    const types = new Set(vehicles.map(v => v.type));
    return Array.from(types);
  }, [vehicles]);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  if (vehicles.length === 0) {
    return (
      <PanelContainer>
        <EmptyState>
          <EmptyIcon>
            <Car size={48} />
          </EmptyIcon>
          <div>No vehicles detected</div>
          <div style={{ fontSize: '14px', marginTop: '8px' }}>
            Upload an image or search for vehicles to get started
          </div>
        </EmptyState>
      </PanelContainer>
    );
  }

  return (
    <PanelContainer>
      <Section>
        <SectionTitle>
          <Car size={16} />
          Detected Vehicles ({vehicles.length})
        </SectionTitle>

        <FilterContainer>
          <FilterButton 
            active={filter === 'all'} 
            onClick={() => setFilter('all')}
          >
            All
          </FilterButton>
          {vehicleTypes.map(type => (
            <FilterButton 
              key={type}
              active={filter === type} 
              onClick={() => setFilter(type)}
            >
              {type}
            </FilterButton>
          ))}
        </FilterContainer>

        <FilterContainer>
          <FilterButton 
            active={sortBy === 'timestamp'} 
            onClick={() => setSortBy('timestamp')}
          >
            <Clock size={12} />
            Time
          </FilterButton>
          <FilterButton 
            active={sortBy === 'confidence'} 
            onClick={() => setSortBy('confidence')}
          >
            <Filter size={12} />
            Confidence
          </FilterButton>
          <FilterButton 
            active={sortBy === 'type'} 
            onClick={() => setSortBy('type')}
          >
            Type
          </FilterButton>
        </FilterContainer>
      </Section>

      {filteredVehicles.map((vehicle) => (
        <VehicleCard key={vehicle.id}>
          <VehicleHeader>
            <VehicleType type={vehicle.type}>
              {vehicle.type}
            </VehicleType>
            <ConfidenceBadge confidence={vehicle.confidence}>
              {(vehicle.confidence * 100).toFixed(0)}%
            </ConfidenceBadge>
          </VehicleHeader>

          <VehicleInfo>
            <InfoItem>
              <Clock size={12} />
              {formatTimestamp(vehicle.timestamp)}
            </InfoItem>
            <InfoItem>
              <MapPin size={12} />
              ID: {vehicle.id}
            </InfoItem>
          </VehicleInfo>

          <Coordinates>
            {vehicle.latitude.toFixed(6)}, {vehicle.longitude.toFixed(6)}
          </Coordinates>

          <ActionButton onClick={() => onVehicleSelect(vehicle)}>
            <Eye size={12} />
            View on Map
          </ActionButton>
        </VehicleCard>
      ))}

      {filteredVehicles.length === 0 && filter !== 'all' && (
        <EmptyState>
          <div>No {filter} vehicles found</div>
        </EmptyState>
      )}
    </PanelContainer>
  );
};

export default VehicleList;

