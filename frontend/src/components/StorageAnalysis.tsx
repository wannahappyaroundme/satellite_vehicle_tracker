import React from 'react';
import styled from 'styled-components';
import { Database, MapPin, TrendingUp, Target, Info, Car } from 'lucide-react';
import { StorageAnalysisData } from '../types';

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

const ScoreCard = styled.div`
  background: rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  border: 1px solid rgba(255,255,255,0.2);
`;

const ScoreValue = styled.div<{ score: number }>`
  font-size: 36px;
  font-weight: 700;
  color: ${props => 
    props.score > 70 ? '#27ae60' :
    props.score > 40 ? '#f39c12' : '#e74c3c'
  };
  margin-bottom: 8px;
`;

const ScoreLabel = styled.div`
  font-size: 14px;
  opacity: 0.8;
  margin-bottom: 15px;
`;

const ScoreBar = styled.div`
  background: rgba(255,255,255,0.2);
  height: 6px;
  border-radius: 3px;
  overflow: hidden;
`;

const ScoreBarFill = styled.div<{ score: number }>`
  height: 100%;
  background: ${props => 
    props.score > 70 ? '#27ae60' :
    props.score > 40 ? '#f39c12' : '#e74c3c'
  };
  width: ${props => props.score}%;
  transition: width 0.3s ease;
`;

const LocationCard = styled.div<{ score: number }>`
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 12px;
  border: 1px solid ${props => 
    props.score > 70 ? 'rgba(39, 174, 96, 0.3)' :
    props.score > 40 ? 'rgba(243, 156, 18, 0.3)' : 'rgba(231, 76, 60, 0.3)'
  };
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255,255,255,0.15);
  }
`;

const LocationHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
`;

const LocationScore = styled.div<{ score: number }>`
  background: ${props => 
    props.score > 70 ? '#27ae60' :
    props.score > 40 ? '#f39c12' : '#e74c3c'
  };
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
`;

const LocationInfo = styled.div`
  font-size: 13px;
  margin-bottom: 8px;
`;

const VehicleTypes = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
`;

const VehicleTypeTag = styled.div`
  background: rgba(255,255,255,0.2);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  text-transform: capitalize;
`;

const Reasoning = styled.div`
  font-size: 12px;
  opacity: 0.8;
  font-style: italic;
  margin-bottom: 10px;
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

  &:hover {
    background: rgba(255,255,255,0.2);
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
`;

const StatCard = styled.div`
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  border: 1px solid rgba(255,255,255,0.2);
`;

const StatValue = styled.div`
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 5px;
`;

const StatLabel = styled.div`
  font-size: 12px;
  opacity: 0.8;
`;

const SummaryCard = styled.div`
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 15px;
  border: 1px solid rgba(255,255,255,0.2);
  margin-bottom: 20px;
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

interface StorageAnalysisProps {
  analysis: StorageAnalysisData | null;
  onLocationSelect: (lat: number, lng: number) => void;
}

const StorageAnalysis: React.FC<StorageAnalysisProps> = ({ analysis, onLocationSelect }) => {
  const getScoreLabel = (score: number) => {
    if (score > 70) return 'High Potential';
    if (score > 40) return 'Moderate Potential';
    return 'Low Potential';
  };

  if (!analysis) {
    return (
      <PanelContainer>
        <EmptyState>
          <EmptyIcon>
            <Database size={48} />
          </EmptyIcon>
          <div>No storage analysis available</div>
          <div style={{ fontSize: '14px', marginTop: '8px' }}>
            Run a storage analysis from the search panel
          </div>
        </EmptyState>
      </PanelContainer>
    );
  }

  return (
    <PanelContainer>
      <Section>
        <SectionTitle>
          <TrendingUp size={16} />
          Storage Potential
        </SectionTitle>
        
        <ScoreCard>
          <ScoreValue score={analysis.storage_potential}>
            {analysis.storage_potential.toFixed(1)}%
          </ScoreValue>
          <ScoreLabel>
            {getScoreLabel(analysis.storage_potential)}
          </ScoreLabel>
          <ScoreBar>
            <ScoreBarFill score={analysis.storage_potential} />
          </ScoreBar>
        </ScoreCard>
      </Section>

      <Section>
        <StatsGrid>
          <StatCard>
            <StatValue>{analysis.total_vehicles}</StatValue>
            <StatLabel>Total Vehicles</StatLabel>
          </StatCard>
          <StatCard>
            <StatValue>{analysis.vehicle_clusters.length}</StatValue>
            <StatLabel>Clusters Found</StatLabel>
          </StatCard>
          <StatCard>
            <StatValue>{analysis.recommended_locations.length}</StatValue>
            <StatLabel>Recommendations</StatLabel>
          </StatCard>
          <StatCard>
            <StatValue>
              {Math.round(analysis.vehicle_clusters.reduce((sum, cluster) => 
                sum + cluster.vehicle_count, 0) / Math.max(analysis.vehicle_clusters.length, 1))}
            </StatValue>
            <StatLabel>Avg per Cluster</StatLabel>
          </StatCard>
        </StatsGrid>
      </Section>

      <Section>
        <SummaryCard>
          <SectionTitle>
            <Info size={16} />
            Analysis Summary
          </SectionTitle>
          <div style={{ fontSize: '14px', lineHeight: '1.5' }}>
            {analysis.analysis_summary}
          </div>
        </SummaryCard>
      </Section>

      {analysis.recommended_locations.length > 0 && (
        <Section>
          <SectionTitle>
            <Target size={16} />
            Recommended Locations
          </SectionTitle>
          
          {analysis.recommended_locations.map((location, index) => (
            <LocationCard key={index} score={location.potential_score}>
              <LocationHeader>
                <div style={{ fontSize: '14px', fontWeight: '500' }}>
                  Location #{index + 1}
                </div>
                <LocationScore score={location.potential_score}>
                  {location.potential_score.toFixed(1)}%
                </LocationScore>
              </LocationHeader>

              <LocationInfo>
                <div>Vehicles: {location.vehicle_count}</div>
                <div style={{ fontFamily: 'Monaco, Menlo, monospace', fontSize: '12px', opacity: 0.7 }}>
                  {location.location.latitude.toFixed(6)}, {location.location.longitude.toFixed(6)}
                </div>
              </LocationInfo>

              <VehicleTypes>
                {location.primary_vehicle_types.map((type, i) => (
                  <VehicleTypeTag key={i}>
                    <Car size={10} style={{ marginRight: '4px' }} />
                    {type}
                  </VehicleTypeTag>
                ))}
              </VehicleTypes>

              <Reasoning>
                {location.reasoning}
              </Reasoning>

              <ActionButton onClick={() => onLocationSelect(location.location.latitude, location.location.longitude)}>
                <MapPin size={12} />
                View on Map
              </ActionButton>
            </LocationCard>
          ))}
        </Section>
      )}

      {analysis.vehicle_clusters.length > 0 && (
        <Section>
          <SectionTitle>
            <Database size={16} />
            Vehicle Clusters
          </SectionTitle>
          
          {analysis.vehicle_clusters.slice(0, 3).map((cluster) => (
            <LocationCard key={cluster.cluster_id} score={60}>
              <LocationHeader>
                <div style={{ fontSize: '14px', fontWeight: '500' }}>
                  Cluster #{cluster.cluster_id}
                </div>
                <LocationScore score={60}>
                  {cluster.vehicle_count} vehicles
                </LocationScore>
              </LocationHeader>

              <LocationInfo>
                <div>Time Span: {cluster.metrics.time_span_hours.toFixed(1)}h</div>
                <div>Confidence: {(cluster.metrics.average_confidence * 100).toFixed(1)}%</div>
                <div style={{ fontFamily: 'Monaco, Menlo, monospace', fontSize: '12px', opacity: 0.7 }}>
                  {cluster.center.latitude.toFixed(6)}, {cluster.center.longitude.toFixed(6)}
                </div>
              </LocationInfo>

              <VehicleTypes>
                {Object.entries(cluster.vehicle_types).map(([type, count]) => (
                  <VehicleTypeTag key={type}>
                    {type}: {count}
                  </VehicleTypeTag>
                ))}
              </VehicleTypes>

              <ActionButton onClick={() => onLocationSelect(cluster.center.latitude, cluster.center.longitude)}>
                <MapPin size={12} />
                View Cluster
              </ActionButton>
            </LocationCard>
          ))}
        </Section>
      )}
    </PanelContainer>
  );
};

export default StorageAnalysis;

