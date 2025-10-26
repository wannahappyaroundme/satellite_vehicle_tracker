/**
 * AnalyticsDashboard.tsx
 * 데이터 분석 대시보드
 *
 * 기능:
 * - DBSCAN 클러스터링: 차량 밀집 지역 분석
 * - 히트맵: 위험도 가중 밀도 시각화
 * - 시/도별 통계
 * - 시간대별 트렌드
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Circle, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface ClusterData {
  cluster_id: number;
  vehicle_count: number;
  center: {
    latitude: number;
    longitude: number;
  };
  risk_distribution: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
  avg_similarity: number;
  risk_score: number;
}

interface HeatmapGrid {
  latitude: number;
  longitude: number;
  vehicle_count: number;
  risk_score: number;
  risk_counts: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
}

interface CityStats {
  city: string;
  total_count: number;
  risk_counts: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
  avg_similarity: number;
}

const AnalyticsDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'clustering' | 'heatmap' | 'city' | 'trends'>('clustering');
  const [clusters, setClusters] = useState<ClusterData[]>([]);
  const [heatmapData, setHeatmapData] = useState<HeatmapGrid[]>([]);
  const [cityStats, setCityStats] = useState<CityStats[]>([]);
  const [loading, setLoading] = useState(false);

  // 클러스터링 데이터 로드
  const loadClustering = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/analytics/clustering?eps_km=0.5&min_samples=3`);
      if (response.data.success) {
        setClusters(response.data.clusters);
      }
    } catch (error) {
      console.error('클러스터링 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  // 히트맵 데이터 로드
  const loadHeatmap = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/analytics/heatmap?grid_size=0.01`);
      if (response.data.success) {
        setHeatmapData(response.data.heatmap);
      }
    } catch (error) {
      console.error('히트맵 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  // 시/도별 통계 로드
  const loadCityStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/analytics/by-city`);
      if (response.data.success) {
        setCityStats(response.data.city_statistics);
      }
    } catch (error) {
      console.error('시/도별 통계 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  // 탭 변경 시 데이터 로드
  useEffect(() => {
    if (activeTab === 'clustering') {
      loadClustering();
    } else if (activeTab === 'heatmap') {
      loadHeatmap();
    } else if (activeTab === 'city') {
      loadCityStats();
    }
  }, [activeTab]);

  // 위험도에 따른 색상
  const getRiskColor = (riskScore: number, maxScore: number): string => {
    const intensity = Math.min(1, riskScore / maxScore);
    if (intensity > 0.75) return '#DC2626';  // Red
    if (intensity > 0.5) return '#F59E0B';   // Orange
    if (intensity > 0.25) return '#FCD34D';  // Yellow
    return '#60A5FA';  // Blue
  };

  return (
    <div className="analytics-dashboard">
      {/* 탭 메뉴 */}
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'clustering' ? 'active' : ''}`}
          onClick={() => setActiveTab('clustering')}
        >
          🔵 클러스터링
        </button>
        <button
          className={`tab ${activeTab === 'heatmap' ? 'active' : ''}`}
          onClick={() => setActiveTab('heatmap')}
        >
          🔥 히트맵
        </button>
        <button
          className={`tab ${activeTab === 'city' ? 'active' : ''}`}
          onClick={() => setActiveTab('city')}
        >
          📊 시/도별 통계
        </button>
      </div>

      {/* 로딩 */}
      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>데이터를 분석하는 중...</p>
        </div>
      )}

      {/* 클러스터링 뷰 */}
      {activeTab === 'clustering' && !loading && (
        <div className="clustering-view">
          <h3>🔵 DBSCAN 클러스터링 분석</h3>
          <p className="description">
            방치 차량이 밀집된 지역을 자동으로 탐지합니다. (반경 500m, 최소 3대)
          </p>

          <div className="clusters-list">
            {clusters.map((cluster, index) => (
              <div key={cluster.cluster_id} className="cluster-card">
                <div className="cluster-header">
                  <span className="cluster-rank">#{index + 1}</span>
                  <span className="cluster-count">{cluster.vehicle_count}대</span>
                  <span className="risk-score">위험도: {cluster.risk_score}</span>
                </div>

                <div className="cluster-location">
                  📍 위치: {cluster.center.latitude.toFixed(4)}, {cluster.center.longitude.toFixed(4)}
                </div>

                <div className="risk-bars">
                  {cluster.risk_distribution.CRITICAL > 0 && (
                    <div className="risk-bar critical">
                      <span>CRITICAL</span>
                      <span>{cluster.risk_distribution.CRITICAL}대</span>
                    </div>
                  )}
                  {cluster.risk_distribution.HIGH > 0 && (
                    <div className="risk-bar high">
                      <span>HIGH</span>
                      <span>{cluster.risk_distribution.HIGH}대</span>
                    </div>
                  )}
                  {cluster.risk_distribution.MEDIUM > 0 && (
                    <div className="risk-bar medium">
                      <span>MEDIUM</span>
                      <span>{cluster.risk_distribution.MEDIUM}대</span>
                    </div>
                  )}
                </div>

                <div className="avg-similarity">
                  평균 유사도: {cluster.avg_similarity.toFixed(1)}%
                </div>
              </div>
            ))}
          </div>

          {clusters.length === 0 && !loading && (
            <div className="no-data">
              클러스터링 데이터가 없습니다.
            </div>
          )}
        </div>
      )}

      {/* 히트맵 뷰 */}
      {activeTab === 'heatmap' && !loading && (
        <div className="heatmap-view">
          <h3>🔥 위험도 가중 히트맵</h3>
          <p className="description">
            위험도를 고려한 차량 밀집도를 시각화합니다. (1km 그리드)
          </p>

          <div className="heatmap-grid">
            {heatmapData.slice(0, 20).map((grid, index) => {
              const maxScore = heatmapData[0]?.risk_score || 1;
              const color = getRiskColor(grid.risk_score, maxScore);

              return (
                <div key={index} className="heatmap-item" style={{ borderLeft: `5px solid ${color}` }}>
                  <div className="heatmap-header">
                    <span className="rank">#{index + 1}</span>
                    <span className="vehicle-count">{grid.vehicle_count}대</span>
                    <span className="risk-score">점수: {grid.risk_score}</span>
                  </div>

                  <div className="location">
                    📍 {grid.latitude.toFixed(4)}, {grid.longitude.toFixed(4)}
                  </div>

                  <div className="risk-counts">
                    {grid.risk_counts.CRITICAL > 0 && <span className="badge critical">CRITICAL: {grid.risk_counts.CRITICAL}</span>}
                    {grid.risk_counts.HIGH > 0 && <span className="badge high">HIGH: {grid.risk_counts.HIGH}</span>}
                    {grid.risk_counts.MEDIUM > 0 && <span className="badge medium">MEDIUM: {grid.risk_counts.MEDIUM}</span>}
                  </div>
                </div>
              );
            })}
          </div>

          {heatmapData.length === 0 && !loading && (
            <div className="no-data">
              히트맵 데이터가 없습니다.
            </div>
          )}
        </div>
      )}

      {/* 시/도별 통계 뷰 */}
      {activeTab === 'city' && !loading && (
        <div className="city-stats-view">
          <h3>📊 시/도별 통계</h3>
          <p className="description">
            각 시/도별 방치 차량 현황을 확인합니다.
          </p>

          <div className="city-stats-list">
            {cityStats.map((city, index) => (
              <div key={index} className="city-stat-card">
                <div className="city-header">
                  <span className="city-rank">#{index + 1}</span>
                  <span className="city-name">{city.city}</span>
                  <span className="city-count">{city.total_count}대</span>
                </div>

                <div className="city-risks">
                  <div className="risk-item critical">
                    <span>CRITICAL</span>
                    <span>{city.risk_counts.CRITICAL}</span>
                  </div>
                  <div className="risk-item high">
                    <span>HIGH</span>
                    <span>{city.risk_counts.HIGH}</span>
                  </div>
                  <div className="risk-item medium">
                    <span>MEDIUM</span>
                    <span>{city.risk_counts.MEDIUM}</span>
                  </div>
                  <div className="risk-item low">
                    <span>LOW</span>
                    <span>{city.risk_counts.LOW}</span>
                  </div>
                </div>

                <div className="city-avg">
                  평균 유사도: {city.avg_similarity.toFixed(1)}%
                </div>
              </div>
            ))}
          </div>

          {cityStats.length === 0 && !loading && (
            <div className="no-data">
              시/도별 통계 데이터가 없습니다.
            </div>
          )}
        </div>
      )}

      <style jsx>{`
        .analytics-dashboard {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .tabs {
          display: flex;
          gap: 10px;
          margin-bottom: 30px;
          border-bottom: 2px solid #e5e7eb;
        }

        .tab {
          padding: 12px 24px;
          background: none;
          border: none;
          border-bottom: 3px solid transparent;
          cursor: pointer;
          font-size: 16px;
          font-weight: 500;
          color: #6b7280;
          transition: all 0.3s;
        }

        .tab:hover {
          color: #2563EB;
        }

        .tab.active {
          color: #2563EB;
          border-bottom-color: #2563EB;
        }

        .loading {
          text-align: center;
          padding: 60px 20px;
        }

        .spinner {
          border: 4px solid #f3f3f3;
          border-top: 4px solid #2563EB;
          border-radius: 50%;
          width: 50px;
          height: 50px;
          animation: spin 1s linear infinite;
          margin: 0 auto 20px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        h3 {
          font-size: 24px;
          margin-bottom: 10px;
        }

        .description {
          color: #6b7280;
          margin-bottom: 30px;
        }

        /* 클러스터링 스타일 */
        .clusters-list {
          display: grid;
          gap: 20px;
        }

        .cluster-card {
          background: white;
          padding: 20px;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .cluster-header {
          display: flex;
          gap: 15px;
          align-items: center;
          margin-bottom: 15px;
        }

        .cluster-rank {
          font-size: 24px;
          font-weight: bold;
          color: #6b7280;
        }

        .cluster-count {
          font-size: 20px;
          font-weight: bold;
          color: #2563EB;
        }

        .risk-score {
          margin-left: auto;
          padding: 6px 12px;
          background: #FEF3C7;
          color: #92400E;
          border-radius: 6px;
          font-weight: 600;
        }

        .cluster-location {
          margin-bottom: 15px;
          color: #4b5563;
        }

        .risk-bars {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 15px;
        }

        .risk-bar {
          display: flex;
          justify-content: space-between;
          padding: 8px 12px;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 600;
        }

        .risk-bar.critical {
          background: #FEE2E2;
          color: #991B1B;
        }

        .risk-bar.high {
          background: #FED7AA;
          color: #9A3412;
        }

        .risk-bar.medium {
          background: #FEF3C7;
          color: #92400E;
        }

        .avg-similarity {
          font-size: 14px;
          color: #6b7280;
        }

        /* 히트맵 스타일 */
        .heatmap-grid {
          display: grid;
          gap: 15px;
        }

        .heatmap-item {
          background: white;
          padding: 15px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .heatmap-header {
          display: flex;
          gap: 15px;
          align-items: center;
          margin-bottom: 10px;
        }

        .rank {
          font-weight: bold;
          color: #6b7280;
        }

        .vehicle-count {
          font-weight: bold;
          color: #2563EB;
        }

        .location {
          margin-bottom: 10px;
          color: #4b5563;
          font-size: 14px;
        }

        .risk-counts {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .badge {
          padding: 4px 10px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
        }

        .badge.critical {
          background: #FEE2E2;
          color: #991B1B;
        }

        .badge.high {
          background: #FED7AA;
          color: #9A3412;
        }

        .badge.medium {
          background: #FEF3C7;
          color: #92400E;
        }

        /* 시/도별 통계 스타일 */
        .city-stats-list {
          display: grid;
          gap: 15px;
        }

        .city-stat-card {
          background: white;
          padding: 20px;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .city-header {
          display: flex;
          gap: 15px;
          align-items: center;
          margin-bottom: 15px;
        }

        .city-rank {
          font-weight: bold;
          color: #6b7280;
        }

        .city-name {
          font-size: 18px;
          font-weight: bold;
        }

        .city-count {
          margin-left: auto;
          font-size: 20px;
          font-weight: bold;
          color: #2563EB;
        }

        .city-risks {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 10px;
          margin-bottom: 15px;
        }

        .risk-item {
          text-align: center;
          padding: 10px;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 600;
        }

        .risk-item.critical {
          background: #FEE2E2;
          color: #991B1B;
        }

        .risk-item.high {
          background: #FED7AA;
          color: #9A3412;
        }

        .risk-item.medium {
          background: #FEF3C7;
          color: #92400E;
        }

        .risk-item.low {
          background: #E0E7FF;
          color: #3730A3;
        }

        .risk-item span:first-child {
          display: block;
          font-size: 11px;
          margin-bottom: 4px;
        }

        .city-avg {
          font-size: 14px;
          color: #6b7280;
        }

        .no-data {
          text-align: center;
          padding: 60px 20px;
          color: #9ca3af;
          font-size: 18px;
        }
      `}</style>
    </div>
  );
};

export default AnalyticsDashboard;
