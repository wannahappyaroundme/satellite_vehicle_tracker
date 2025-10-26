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

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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
      <div className="admin-dashboard">
        <div className="loading">
          <div className="spinner"></div>
          <p>관리자 대시보드를 로드하는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-dashboard">
        <div className="error">
          <h3>⚠️ 오류 발생</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>새로고침</button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <h2>🔧 관리자 대시보드</h2>
        <button className="refresh-button" onClick={() => {
          loadStatistics();
          loadSchedulerStatus();
        }}>
          🔄 새로고침
        </button>
      </div>

      {/* 통계 카드 */}
      <div className="stats-grid">
        {/* 총 차량 수 */}
        <div className="stat-card total">
          <div className="stat-icon">🚗</div>
          <div className="stat-content">
            <h3>총 방치 차량</h3>
            <p className="stat-value">{statistics?.total_vehicles || 0}대</p>
          </div>
        </div>

        {/* 위험도별 분포 */}
        <div className="stat-card critical">
          <div className="stat-icon">🔴</div>
          <div className="stat-content">
            <h3>CRITICAL</h3>
            <p className="stat-value">{statistics?.risk_distribution.CRITICAL || 0}대</p>
          </div>
        </div>

        <div className="stat-card high">
          <div className="stat-icon">🟠</div>
          <div className="stat-content">
            <h3>HIGH</h3>
            <p className="stat-value">{statistics?.risk_distribution.HIGH || 0}대</p>
          </div>
        </div>

        <div className="stat-card medium">
          <div className="stat-icon">🟡</div>
          <div className="stat-content">
            <h3>MEDIUM</h3>
            <p className="stat-value">{statistics?.risk_distribution.MEDIUM || 0}대</p>
          </div>
        </div>
      </div>

      {/* 스케줄러 상태 */}
      <div className="scheduler-status">
        <h3>⏰ 자동 스케줄러 상태</h3>
        <div className="scheduler-info">
          <div className="status-row">
            <span className="label">상태:</span>
            <span className={`status ${schedulerStatus?.is_running ? 'running' : 'stopped'}`}>
              {schedulerStatus?.is_running ? '✅ 실행 중' : '⏸️ 중지됨'}
            </span>
          </div>
          <div className="status-row">
            <span className="label">실행 주기:</span>
            <span className="value">{schedulerStatus?.next_run_time || '정보 없음'}</span>
          </div>
          <div className="status-row">
            <span className="label">Cron 표현식:</span>
            <span className="value">{schedulerStatus?.schedule || '정보 없음'}</span>
          </div>
        </div>
        <button className="trigger-button" onClick={triggerAnalysis}>
          ▶️ 수동 분석 시작
        </button>
      </div>

      {/* 지역별 분포 */}
      <div className="city-distribution">
        <h3>📍 지역별 분포 (상위 10개)</h3>
        <div className="city-list">
          {statistics?.city_distribution.map((item, index) => (
            <div key={index} className="city-item">
              <span className="rank">#{index + 1}</span>
              <span className="city-name">{item.city}</span>
              <span className="city-count">{item.count}대</span>
              <div
                className="city-bar"
                style={{
                  width: `${(item.count / (statistics.city_distribution[0]?.count || 1)) * 100}%`
                }}
              ></div>
            </div>
          ))}
        </div>
      </div>

      {/* 최근 분석 이력 */}
      <div className="recent-analyses">
        <h3>📊 최근 분석 이력</h3>
        <div className="analysis-table">
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
                    <span className={`status-badge ${log.status}`}>
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

      <style jsx>{`
        .admin-dashboard {
          padding: 20px;
          max-width: 1400px;
          margin: 0 auto;
        }

        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
        }

        .dashboard-header h2 {
          font-size: 28px;
          color: #333;
          margin: 0;
        }

        .refresh-button {
          padding: 10px 20px;
          background: #4CAF50;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          transition: background 0.3s;
        }

        .refresh-button:hover {
          background: #45a049;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }

        .stat-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          display: flex;
          align-items: center;
          gap: 15px;
        }

        .stat-card.total {
          border-left: 4px solid #2196F3;
        }

        .stat-card.critical {
          border-left: 4px solid #f44336;
        }

        .stat-card.high {
          border-left: 4px solid #ff9800;
        }

        .stat-card.medium {
          border-left: 4px solid #ffc107;
        }

        .stat-icon {
          font-size: 48px;
        }

        .stat-content h3 {
          margin: 0 0 8px 0;
          font-size: 14px;
          color: #666;
        }

        .stat-value {
          margin: 0;
          font-size: 32px;
          font-weight: bold;
          color: #333;
        }

        .scheduler-status {
          background: white;
          border-radius: 12px;
          padding: 25px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          margin-bottom: 30px;
        }

        .scheduler-status h3 {
          margin: 0 0 20px 0;
          font-size: 20px;
          color: #333;
        }

        .scheduler-info {
          margin-bottom: 20px;
        }

        .status-row {
          display: flex;
          padding: 10px 0;
          border-bottom: 1px solid #eee;
        }

        .status-row:last-child {
          border-bottom: none;
        }

        .status-row .label {
          width: 150px;
          font-weight: 600;
          color: #666;
        }

        .status-row .value {
          flex: 1;
          color: #333;
        }

        .status.running {
          color: #4CAF50;
          font-weight: bold;
        }

        .status.stopped {
          color: #f44336;
          font-weight: bold;
        }

        .trigger-button {
          padding: 12px 24px;
          background: #2196F3;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 16px;
          font-weight: bold;
          transition: background 0.3s;
        }

        .trigger-button:hover {
          background: #1976D2;
        }

        .city-distribution {
          background: white;
          border-radius: 12px;
          padding: 25px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          margin-bottom: 30px;
        }

        .city-distribution h3 {
          margin: 0 0 20px 0;
          font-size: 20px;
          color: #333;
        }

        .city-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .city-item {
          display: flex;
          align-items: center;
          gap: 15px;
          position: relative;
          padding: 10px;
          border-radius: 6px;
          background: #f5f5f5;
        }

        .city-item .rank {
          font-weight: bold;
          color: #666;
          width: 40px;
        }

        .city-item .city-name {
          flex: 1;
          font-weight: 500;
        }

        .city-item .city-count {
          font-weight: bold;
          color: #2196F3;
          width: 60px;
          text-align: right;
        }

        .city-bar {
          position: absolute;
          left: 0;
          top: 0;
          height: 100%;
          background: linear-gradient(90deg, #2196F3 0%, #64B5F6 100%);
          opacity: 0.2;
          border-radius: 6px;
          z-index: 0;
        }

        .recent-analyses {
          background: white;
          border-radius: 12px;
          padding: 25px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .recent-analyses h3 {
          margin: 0 0 20px 0;
          font-size: 20px;
          color: #333;
        }

        .analysis-table {
          overflow-x: auto;
        }

        table {
          width: 100%;
          border-collapse: collapse;
        }

        thead {
          background: #f5f5f5;
        }

        th {
          padding: 12px;
          text-align: left;
          font-weight: 600;
          color: #666;
          border-bottom: 2px solid #ddd;
        }

        td {
          padding: 12px;
          border-bottom: 1px solid #eee;
        }

        .status-badge {
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: bold;
        }

        .status-badge.completed {
          background: #C8E6C9;
          color: #2E7D32;
        }

        .status-badge.running {
          background: #BBDEFB;
          color: #1565C0;
        }

        .status-badge.failed {
          background: #FFCDD2;
          color: #C62828;
        }

        .loading, .error {
          text-align: center;
          padding: 60px 20px;
        }

        .spinner {
          border: 4px solid #f3f3f3;
          border-top: 4px solid #2196F3;
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

        .error {
          color: #f44336;
        }

        .error button {
          margin-top: 20px;
          padding: 10px 20px;
          background: #2196F3;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
        }
      `}</style>
    </div>
  );
};

export default AdminDashboard;
