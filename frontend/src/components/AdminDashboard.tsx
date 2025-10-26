/**
 * AdminDashboard.tsx
 * 관리자 대시보드 컴포넌트
 *
 * 기능:
 * - 실시간 통계 표시 (총 차량 수, 위험도별 분포, 지역별 분포)
 * - 스케줄러 상태 확인
 * - 최근 분석 이력 조회
 * - 차량 상태 관리 (승인, 거부, 삭제)
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styles from './AdminDashboard.module.css';

const API_URL = process.env.REACT_APP_FASTAPI_URL || 'http://localhost:8000/api';

interface Statistics {
  total_vehicles: number;
  risk_distribution: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
  city_distribution: Array<{
    city: string;
    count: number;
  }>;
  recent_analyses: Array<{
    id: number;
    analysis_type: string;
    status: string;
    started_at: string | null;
    completed_at: string | null;
    regions_analyzed: number | null;
    vehicles_found: number | null;
    vehicles_updated: number | null;
  }>;
}

interface SchedulerStatus {
  is_running: boolean;
  next_run_time: string;
  schedule: string;
}

const AdminDashboard: React.FC = () => {
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [schedulerStatus, setSchedulerStatus] = useState<SchedulerStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 통계 데이터 로드
  const loadStatistics = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/admin/statistics`);
      if (response.data.success) {
        setStatistics(response.data.statistics);
      }
    } catch (err: any) {
      console.error('통계 로드 실패:', err);
      setError(err.message);
    }
  };

  // 스케줄러 상태 로드
  const loadSchedulerStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/admin/scheduler-status`);
      if (response.data.success) {
        setSchedulerStatus(response.data.scheduler);
      }
    } catch (err: any) {
      console.error('스케줄러 상태 로드 실패:', err);
    }
  };

  // 수동 분석 트리거
  const triggerAnalysis = async () => {
    try {
      const response = await axios.post(`${API_URL}/api/admin/trigger-analysis`);
      if (response.data.success) {
        alert(response.data.message);
        // 통계 새로고침
        setTimeout(() => loadStatistics(), 2000);
      }
    } catch (err: any) {
      console.error('분석 트리거 실패:', err);
      alert('분석 시작에 실패했습니다: ' + err.message);
    }
  };

  // 초기 로드
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([loadStatistics(), loadSchedulerStatus()]);
      setLoading(false);
    };

    loadData();

    // 30초마다 자동 새로고침
    const interval = setInterval(() => {
      loadStatistics();
      loadSchedulerStatus();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className={styles.adminDashboard}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>관리자 대시보드를 로드하는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.adminDashboard}>
        <div className={styles.error}>
          <h3>⚠️ 오류 발생</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>새로고침</button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.adminDashboard}>
      <div className={styles.dashboardHeader}>
        <h2>🔧 관리자 대시보드</h2>
        <button className={styles.refreshButton} onClick={() => {
          loadStatistics();
          loadSchedulerStatus();
        }}>
          🔄 새로고침
        </button>
      </div>

      {/* 통계 카드 */}
      <div className={styles.statsGrid}>
        {/* 총 차량 수 */}
        <div className={`${styles.statCard} ${styles.total}`}>
          <div className={styles.statIcon}>🚗</div>
          <div className={styles.statContent}>
            <h3>총 방치 차량</h3>
            <p className={styles.statValue}>{statistics?.total_vehicles || 0}대</p>
          </div>
        </div>

        {/* 위험도별 분포 */}
        <div className={`${styles.statCard} ${styles.critical}`}>
          <div className={styles.statIcon}>🔴</div>
          <div className={styles.statContent}>
            <h3>CRITICAL</h3>
            <p className={styles.statValue}>{statistics?.risk_distribution.CRITICAL || 0}대</p>
          </div>
        </div>

        <div className={`${styles.statCard} ${styles.high}`}>
          <div className={styles.statIcon}>🟠</div>
          <div className={styles.statContent}>
            <h3>HIGH</h3>
            <p className={styles.statValue}>{statistics?.risk_distribution.HIGH || 0}대</p>
          </div>
        </div>

        <div className={`${styles.statCard} ${styles.medium}`}>
          <div className={styles.statIcon}>🟡</div>
          <div className={styles.statContent}>
            <h3>MEDIUM</h3>
            <p className={styles.statValue}>{statistics?.risk_distribution.MEDIUM || 0}대</p>
          </div>
        </div>
      </div>

      {/* 스케줄러 상태 */}
      <div className={styles.schedulerStatus}>
        <h3>⏰ 자동 스케줄러 상태</h3>
        <div className={styles.schedulerInfo}>
          <div className={styles.statusRow}>
            <span className="label">상태:</span>
            <span className={`status ${schedulerStatus?.is_running ? 'running' : 'stopped'}`}>
              {schedulerStatus?.is_running ? '✅ 실행 중' : '⏸️ 중지됨'}
            </span>
          </div>
          <div className={styles.statusRow}>
            <span className="label">실행 주기:</span>
            <span className="value">{schedulerStatus?.next_run_time || '정보 없음'}</span>
          </div>
          <div className={styles.statusRow}>
            <span className="label">Cron 표현식:</span>
            <span className="value">{schedulerStatus?.schedule || '정보 없음'}</span>
          </div>
        </div>
        <button className={styles.triggerButton} onClick={triggerAnalysis}>
          ▶️ 수동 분석 시작
        </button>
      </div>

      {/* 지역별 분포 */}
      <div className={styles.cityDistribution}>
        <h3>📍 지역별 분포 (상위 10개)</h3>
        <div className={styles.cityList}>
          {statistics?.city_distribution.map((item, index) => (
            <div key={index} className={styles.cityItem}>
              <span className="rank">#{index + 1}</span>
              <span className="cityName">{item.city}</span>
              <span className="cityCount">{item.count}대</span>
              <div
                className={styles.cityBar}
                style={{
                  width: `${(item.count / (statistics.city_distribution[0]?.count || 1)) * 100}%`
                }}
              ></div>
            </div>
          ))}
        </div>
      </div>

      {/* 최근 분석 이력 */}
      <div className={styles.recentAnalyses}>
        <h3>📊 최근 분석 이력</h3>
        <div className={styles.analysisTable}>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>분석 타입</th>
                <th>상태</th>
                <th>시작 시간</th>
                <th>완료 시간</th>
                <th>분석 지역</th>
                <th>발견 차량</th>
                <th>업데이트</th>
              </tr>
            </thead>
            <tbody>
              {statistics?.recent_analyses.map((log) => (
                <tr key={log.id}>
                  <td>{log.id}</td>
                  <td>{log.analysis_type}</td>
                  <td>
                    <span className={`${styles.statusBadge} ${styles[log.status]}`}>
                      {log.status}
                    </span>
                  </td>
                  <td>{log.started_at ? new Date(log.started_at).toLocaleString('ko-KR') : '-'}</td>
                  <td>{log.completed_at ? new Date(log.completed_at).toLocaleString('ko-KR') : '-'}</td>
                  <td>{log.regions_analyzed || 0}</td>
                  <td>{log.vehicles_found || 0}</td>
                  <td>{log.vehicles_updated || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
