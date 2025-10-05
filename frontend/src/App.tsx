import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Search, Upload, MapPin, Car, Plane, Database, Settings, AlertTriangle } from 'lucide-react';
import SearchPanel from './components/SearchPanel';
import UploadPanel from './components/UploadPanel';
import VehicleList from './components/VehicleList';
import StorageAnalysis from './components/StorageAnalysis';
import LongTermDetector from './components/LongTermDetector';
import { VehicleData, StorageAnalysisData } from './types';

// Fix for default markers in react-leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const AppContainer = styled.div`
  display: flex;
  height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
`;

const Sidebar = styled.div`
  width: 400px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 10px rgba(0,0,0,0.1);
  z-index: 1000;
`;

const Header = styled.div`
  padding: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.2);
`;

const Title = styled.h1`
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const Subtitle = styled.p`
  margin: 5px 0 0 0;
  font-size: 14px;
  opacity: 0.8;
`;

const TabContainer = styled.div`
  display: flex;
  background: rgba(255,255,255,0.1);
  margin: 20px;
  border-radius: 10px;
  overflow: hidden;
`;

const Tab = styled.button<{ active: boolean }>`
  flex: 1;
  padding: 12px;
  background: ${props => props.active ? 'rgba(255,255,255,0.2)' : 'transparent'};
  border: none;
  color: white;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255,255,255,0.15);
  }
`;

const ContentArea = styled.div`
  flex: 1;
  position: relative;
`;

const MapWrapper = styled.div`
  width: 100%;
  height: 100%;
`;

const StatusBar = styled.div`
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(0,0,0,0.8);
  color: white;
  padding: 10px 15px;
  border-radius: 8px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 1000;
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255,255,255,0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  font-size: 18px;
  color: #333;
`;

type TabType = 'search' | 'upload' | 'vehicles' | 'storage' | 'longterm';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('search');
  const [vehicles, setVehicles] = useState<VehicleData[]>([]);
  const [storageAnalysis, setStorageAnalysis] = useState<StorageAnalysisData | null>(null);
  const [loading, setLoading] = useState(false);
  const [mapCenter, setMapCenter] = useState<[number, number]>([40.7128, -74.0060]); // NYC default
  const [mapZoom, setMapZoom] = useState(13);

  const handleVehicleSearch = (searchResults: VehicleData[]) => {
    setVehicles(searchResults);
  };

  const handleStorageAnalysis = (analysis: StorageAnalysisData) => {
    setStorageAnalysis(analysis);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'search':
        return (
          <SearchPanel 
            onVehicleSearch={handleVehicleSearch}
            onStorageAnalysis={handleStorageAnalysis}
            onLoadingChange={setLoading}
          />
        );
      case 'upload':
        return (
          <UploadPanel 
            onVehicleDetected={handleVehicleSearch}
            onLoadingChange={setLoading}
          />
        );
      case 'vehicles':
        return (
          <VehicleList 
            vehicles={vehicles}
            onVehicleSelect={(vehicle) => {
              setMapCenter([vehicle.latitude, vehicle.longitude]);
              setMapZoom(16);
            }}
          />
        );
      case 'storage':
        return (
          <StorageAnalysis 
            analysis={storageAnalysis}
            onLocationSelect={(lat, lng) => {
              setMapCenter([lat, lng]);
              setMapZoom(15);
            }}
          />
        );
      case 'longterm':
        return (
          <LongTermDetector
            onLocationSelect={(lat, lng) => {
              setMapCenter([lat, lng]);
              setMapZoom(15);
            }}
            onLoadingChange={setLoading}
          />
        );
      default:
        return null;
    }
  };

  return (
    <AppContainer>
      <Sidebar>
        <Header>
          <Title>
            <MapPin size={28} />
            Satellite Tracker
          </Title>
          <Subtitle>
            Vehicle Detection & Storage Analysis
          </Subtitle>
        </Header>

        <TabContainer>
          <Tab 
            active={activeTab === 'search'} 
            onClick={() => setActiveTab('search')}
          >
            <Search size={16} />
            Search
          </Tab>
          <Tab 
            active={activeTab === 'upload'} 
            onClick={() => setActiveTab('upload')}
          >
            <Upload size={16} />
            Upload
          </Tab>
          <Tab 
            active={activeTab === 'vehicles'} 
            onClick={() => setActiveTab('vehicles')}
          >
            <Car size={16} />
            Vehicles
          </Tab>
          <Tab 
            active={activeTab === 'storage'} 
            onClick={() => setActiveTab('storage')}
          >
            <Database size={16} />
            Storage
          </Tab>
          <Tab 
            active={activeTab === 'longterm'} 
            onClick={() => setActiveTab('longterm')}
          >
            <AlertTriangle size={16} />
            Long-Term
          </Tab>
        </TabContainer>

        {renderTabContent()}
      </Sidebar>

      <ContentArea>
        <MapWrapper>
          <MapContainer
            center={mapCenter}
            zoom={mapZoom}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            
            {/* Vehicle markers */}
            {vehicles.map((vehicle) => (
              <Marker
                key={vehicle.id}
                position={[vehicle.latitude, vehicle.longitude]}
                icon={L.divIcon({
                  className: 'vehicle-marker',
                  html: `<div style="
                    background: ${vehicle.type === 'aircraft' ? '#e74c3c' : '#3498db'};
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    border: 2px solid white;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                  "></div>`,
                  iconSize: [16, 16],
                  iconAnchor: [8, 8]
                })}
              >
                <Popup>
                  <div>
                    <strong>{vehicle.type}</strong><br />
                    Confidence: {(vehicle.confidence * 100).toFixed(1)}%<br />
                    {new Date(vehicle.timestamp).toLocaleString()}
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Storage analysis circles */}
            {storageAnalysis?.recommended_locations.map((location, index) => (
              <Circle
                key={index}
                center={[location.location.latitude, location.location.longitude]}
                radius={500}
                pathOptions={{
                  color: location.potential_score > 70 ? '#27ae60' : 
                         location.potential_score > 40 ? '#f39c12' : '#e74c3c',
                  fillColor: location.potential_score > 70 ? '#27ae60' : 
                            location.potential_score > 40 ? '#f39c12' : '#e74c3c',
                  fillOpacity: 0.2
                }}
              >
                <Popup>
                  <div>
                    <strong>Storage Potential: {location.potential_score.toFixed(1)}%</strong><br />
                    Vehicles: {location.vehicle_count}<br />
                    {location.reasoning}
                  </div>
                </Popup>
              </Circle>
            ))}
          </MapContainer>
        </MapWrapper>

        <StatusBar>
          <Car size={16} />
          {vehicles.length} vehicles detected
          {storageAnalysis && (
            <>
              <span>•</span>
              <Database size={16} />
              Storage potential: {storageAnalysis.storage_potential.toFixed(1)}%
            </>
          )}
        </StatusBar>

        {loading && (
          <LoadingOverlay>
            Processing satellite imagery...
          </LoadingOverlay>
        )}
      </ContentArea>
    </AppContainer>
  );
};

export default App;

