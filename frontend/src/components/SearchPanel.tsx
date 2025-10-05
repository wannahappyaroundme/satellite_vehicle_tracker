import React, { useState } from 'react';
import styled from 'styled-components';
import { Search, MapPin, Clock, Car, Filter, Zap } from 'lucide-react';
import { VehicleData, StorageAnalysisData, SearchFilters } from '../types';
import { searchVehicles, getStorageAnalysis } from '../services/api';

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

const Select = styled.select`
  width: 100%;
  padding: 10px;
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 6px;
  background: rgba(255,255,255,0.1);
  color: white;
  font-size: 14px;

  option {
    background: #333;
    color: white;
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

const ButtonSecondary = styled(Button)`
  background: rgba(255,255,255,0.1);
  margin-top: 10px;

  &:hover {
    background: rgba(255,255,255,0.2);
  }
`;

const ResultsContainer = styled.div`
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 15px;
  margin-top: 15px;
`;

const ResultItem = styled.div`
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  font-size: 14px;

  &:last-child {
    border-bottom: none;
  }
`;

const StatusIndicator = styled.div<{ status: 'success' | 'warning' | 'error' }>`
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
  background: ${props => 
    props.status === 'success' ? '#27ae60' :
    props.status === 'warning' ? '#f39c12' : '#e74c3c'
  };
`;

interface SearchPanelProps {
  onVehicleSearch: (vehicles: VehicleData[]) => void;
  onStorageAnalysis: (analysis: StorageAnalysisData) => void;
  onLoadingChange: (loading: boolean) => void;
}

const SearchPanel: React.FC<SearchPanelProps> = ({
  onVehicleSearch,
  onStorageAnalysis,
  onLoadingChange
}) => {
  const [filters, setFilters] = useState<SearchFilters>({
    time_range: '24h',
    radius: 0.01,
    min_confidence: 0.5
  });
  const [coordinates, setCoordinates] = useState({
    lat: 40.7128,
    lng: -74.0060
  });
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    onLoadingChange(true);
    
    try {
      const vehicles = await searchVehicles({
        lat: coordinates.lat,
        lng: coordinates.lng,
        radius: filters.radius,
        type: filters.vehicle_type,
        time_range: filters.time_range
      });
      
      onVehicleSearch(vehicles);
      setResults({ type: 'vehicles', data: vehicles });
    } catch (error) {
      console.error('Search error:', error);
      setResults({ type: 'error', message: 'Search failed' });
    } finally {
      setLoading(false);
      onLoadingChange(false);
    }
  };

  const handleStorageAnalysis = async () => {
    setLoading(true);
    onLoadingChange(true);
    
    try {
      const analysis = await getStorageAnalysis({
        lat: coordinates.lat,
        lng: coordinates.lng,
        radius: filters.radius
      });
      
      onStorageAnalysis(analysis);
      setResults({ type: 'storage', data: analysis });
    } catch (error) {
      console.error('Storage analysis error:', error);
      setResults({ type: 'error', message: 'Analysis failed' });
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
            <StatusIndicator status="error" />
            {results.message}
          </div>
        </ResultsContainer>
      );
    }

    if (results.type === 'vehicles') {
      return (
        <ResultsContainer>
          <SectionTitle>
            <Car size={16} />
            Found {results.data.length} vehicles
          </SectionTitle>
          {results.data.slice(0, 5).map((vehicle: VehicleData) => (
            <ResultItem key={vehicle.id}>
              <strong>{vehicle.type}</strong> - {(vehicle.confidence * 100).toFixed(1)}% confidence
              <br />
              <small>
                {new Date(vehicle.timestamp).toLocaleString()}
              </small>
            </ResultItem>
          ))}
          {results.data.length > 5 && (
            <div style={{ fontSize: '12px', opacity: 0.8, marginTop: '10px' }}>
              +{results.data.length - 5} more vehicles
            </div>
          )}
        </ResultsContainer>
      );
    }

    if (results.type === 'storage') {
      return (
        <ResultsContainer>
          <SectionTitle>
            <Zap size={16} />
            Storage Analysis
          </SectionTitle>
          <ResultItem>
            <strong>Potential Score:</strong> {results.data.storage_potential.toFixed(1)}%
          </ResultItem>
          <ResultItem>
            <strong>Total Vehicles:</strong> {results.data.total_vehicles}
          </ResultItem>
          <ResultItem>
            <strong>Clusters Found:</strong> {results.data.vehicle_clusters.length}
          </ResultItem>
          <ResultItem>
            <strong>Summary:</strong> {results.data.analysis_summary}
          </ResultItem>
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
          Location
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
      </Section>

      <Section>
        <SectionTitle>
          <Filter size={16} />
          Filters
        </SectionTitle>
        
        <InputGroup>
          <Label>Vehicle Type</Label>
          <Select
            value={filters.vehicle_type || ''}
            onChange={(e) => setFilters(prev => ({ ...prev, vehicle_type: e.target.value || undefined }))}
          >
            <option value="">All Types</option>
            <option value="car">Car</option>
            <option value="truck">Truck</option>
            <option value="bus">Bus</option>
            <option value="motorcycle">Motorcycle</option>
            <option value="aircraft">Aircraft</option>
          </Select>
        </InputGroup>

        <InputGroup>
          <Label>Time Range</Label>
          <Select
            value={filters.time_range}
            onChange={(e) => setFilters(prev => ({ ...prev, time_range: e.target.value as any }))}
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </Select>
        </InputGroup>

        <InputGroup>
          <Label>Search Radius (km)</Label>
          <Input
            type="number"
            step="0.001"
            value={filters.radius}
            onChange={(e) => setFilters(prev => ({ ...prev, radius: parseFloat(e.target.value) }))}
            placeholder="0.01"
          />
        </InputGroup>

        <InputGroup>
          <Label>Min Confidence</Label>
          <Input
            type="number"
            step="0.1"
            min="0"
            max="1"
            value={filters.min_confidence}
            onChange={(e) => setFilters(prev => ({ ...prev, min_confidence: parseFloat(e.target.value) }))}
            placeholder="0.5"
          />
        </InputGroup>
      </Section>

      <Section>
        <Button onClick={handleSearch} disabled={loading}>
          <Search size={16} />
          {loading ? 'Searching...' : 'Search Vehicles'}
        </Button>

        <ButtonSecondary onClick={handleStorageAnalysis} disabled={loading}>
          <Zap size={16} />
          {loading ? 'Analyzing...' : 'Storage Analysis'}
        </ButtonSecondary>
      </Section>

      {renderResults()}
    </PanelContainer>
  );
};

export default SearchPanel;

