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
import styles from './AnalyticsDashboard.module.css';
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
    <div className={styles["analytics-dashboard"]}>
      {/* 탭 메뉴 */}
      <div className={styles.tabs}>
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
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>데이터를 분석하는 중...</p>
        </div>
      )}

      {/* 클러스터링 뷰 */}
      {activeTab === 'clustering' && !loading && (
        <div className="clustering-view">
          <h3>🔵 DBSCAN 클러스터링 분석</h3>
          <p className={styles.description}>
            방치 차량이 밀집된 지역을 자동으로 탐지합니다. (반경 500m, 최소 3대)
          </p>

          <div className={styles["clusters-list"]}>
            {clusters.map((cluster, index) => (
              <div key={cluster.cluster_id} className={styles["cluster-card"]}>
                <div className={styles["cluster-header"]}>
                  <span className={styles["cluster-rank"]}>#{index + 1}</span>
                  <span className={styles["cluster-count"]}>{cluster.vehicle_count}대</span>
                  <span className={styles["risk-score"]}>위험도: {cluster.risk_score}</span>
                </div>

                <div className={styles["cluster-location"]}>
                  📍 위치: {cluster.center.latitude.toFixed(4)}, {cluster.center.longitude.toFixed(4)}
                </div>

                <div className={styles["risk-bars"]}>
                  {cluster.risk_distribution.CRITICAL > 0 && (
                    <div className={`${styles["risk-bar"]} ${styles.critical}`}>
                      <span>CRITICAL</span>
                      <span>{cluster.risk_distribution.CRITICAL}대</span>
                    </div>
                  )}
                  {cluster.risk_distribution.HIGH > 0 && (
                    <div className={`${styles["risk-bar"]} ${styles.high}`}>
                      <span>HIGH</span>
                      <span>{cluster.risk_distribution.HIGH}대</span>
                    </div>
                  )}
                  {cluster.risk_distribution.MEDIUM > 0 && (
                    <div className={`${styles["risk-bar"]} ${styles.medium}`}>
                      <span>MEDIUM</span>
                      <span>{cluster.risk_distribution.MEDIUM}대</span>
                    </div>
                  )}
                </div>

                <div className={styles["avg-similarity"]}>
                  평균 유사도: {cluster.avg_similarity.toFixed(1)}%
                </div>
              </div>
            ))}
          </div>

          {clusters.length === 0 && !loading && (
            <div className={styles["no-data"]}>
              클러스터링 데이터가 없습니다.
            </div>
          )}
        </div>
      )}

      {/* 히트맵 뷰 */}
      {activeTab === 'heatmap' && !loading && (
        <div className="heatmap-view">
          <h3>🔥 위험도 가중 히트맵</h3>
          <p className={styles.description}>
            위험도를 고려한 차량 밀집도를 시각화합니다. (1km 그리드)
          </p>

          <div className={styles["heatmap-grid"]}>
            {heatmapData.slice(0, 20).map((grid, index) => {
              const maxScore = heatmapData[0]?.risk_score || 1;
              const color = getRiskColor(grid.risk_score, maxScore);

              return (
                <div key={index} className={styles["heatmap-item"]} style={{ borderLeft: `5px solid ${color}` }}>
                  <div className={styles["heatmap-header"]}>
                    <span className={styles.rank}>#{index + 1}</span>
                    <span className={styles["vehicle-count"]}>{grid.vehicle_count}대</span>
                    <span className={styles["risk-score"]}>점수: {grid.risk_score}</span>
                  </div>

                  <div className={styles.location}>
                    📍 {grid.latitude.toFixed(4)}, {grid.longitude.toFixed(4)}
                  </div>

                  <div className={styles["risk-counts"]}>
                    {grid.risk_counts.CRITICAL > 0 && <span className={`${styles.badge} ${styles.critical}`}>CRITICAL: {grid.risk_counts.CRITICAL}</span>}
                    {grid.risk_counts.HIGH > 0 && <span className={`${styles.badge} ${styles.high}`}>HIGH: {grid.risk_counts.HIGH}</span>}
                    {grid.risk_counts.MEDIUM > 0 && <span className={`${styles.badge} ${styles.medium}`}>MEDIUM: {grid.risk_counts.MEDIUM}</span>}
                  </div>
                </div>
              );
            })}
          </div>

          {heatmapData.length === 0 && !loading && (
            <div className={styles["no-data"]}>
              히트맵 데이터가 없습니다.
            </div>
          )}
        </div>
      )}

      {/* 시/도별 통계 뷰 */}
      {activeTab === 'city' && !loading && (
        <div className="city-stats-view">
          <h3>📊 시/도별 통계</h3>
          <p className={styles.description}>
            각 시/도별 방치 차량 현황을 확인합니다.
          </p>

          <div className={styles["city-stats-list"]}>
            {cityStats.map((city, index) => (
              <div key={index} className={styles["city-stat-card"]}>
                <div className={styles["city-header"]}>
                  <span className={styles["city-rank"]}>#{index + 1}</span>
                  <span className={styles["city-name"]}>{city.city}</span>
                  <span className={styles["city-count"]}>{city.total_count}대</span>
                </div>

                <div className={styles["city-risks"]}>
                  <div className={`${styles["risk-item"]} ${styles.critical}`}>
                    <span>CRITICAL</span>
                    <span>{city.risk_counts.CRITICAL}</span>
                  </div>
                  <div className={`${styles["risk-item"]} ${styles.high}`}>
                    <span>HIGH</span>
                    <span>{city.risk_counts.HIGH}</span>
                  </div>
                  <div className={`${styles["risk-item"]} ${styles.medium}`}>
                    <span>MEDIUM</span>
                    <span>{city.risk_counts.MEDIUM}</span>
                  </div>
                  <div className={`${styles["risk-item"]} ${styles.low}`}>
                    <span>LOW</span>
                    <span>{city.risk_counts.LOW}</span>
                  </div>
                </div>

                <div className={styles["city-avg"]}>
                  평균 유사도: {city.avg_similarity.toFixed(1)}%
                </div>
              </div>
            ))}
          </div>

          {cityStats.length === 0 && !loading && (
            <div className={styles["no-data"]}>
              시/도별 통계 데이터가 없습니다.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;
