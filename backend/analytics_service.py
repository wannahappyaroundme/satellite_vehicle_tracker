"""
analytics_service.py
방치 차량 데이터 분석 서비스

기능:
- DBSCAN 클러스터링: 방치 차량 밀집 지역 탐지
- 핫스팟 분석: 위험도 기반 가중 클러스터링
- 통계 분석: 지역별, 위험도별, 시간별 분석
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.cluster import DBSCAN
from datetime import datetime, timedelta
import math


class VehicleAnalyticsService:
    """
    방치 차량 데이터 분석 서비스
    """

    def __init__(self):
        """초기화"""
        pass

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        두 좌표 간 거리 계산 (Haversine formula)

        Args:
            lat1, lon1: 첫 번째 좌표
            lat2, lon2: 두 번째 좌표

        Returns:
            거리 (km)
        """
        R = 6371  # 지구 반지름 (km)

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def perform_clustering(
        self,
        vehicles: List[Dict],
        eps_km: float = 0.5,
        min_samples: int = 3
    ) -> Dict:
        """
        DBSCAN 클러스터링 수행

        Args:
            vehicles: 차량 리스트 (latitude, longitude 포함)
            eps_km: 클러스터 반경 (km)
            min_samples: 최소 차량 수

        Returns:
            클러스터링 결과 (클러스터별 차량 목록, 통계)
        """
        if not vehicles:
            return {
                "success": False,
                "error": "차량 데이터가 없습니다",
                "clusters": [],
                "noise": []
            }

        # 좌표 데이터 추출
        coordinates = np.array([[v.get('latitude', 0), v.get('longitude', 0)] for v in vehicles])

        # DBSCAN 클러스터링 (eps는 라디안 단위로 변환)
        # eps_km를 라디안으로 변환: eps_radians = eps_km / 6371
        eps_radians = eps_km / 6371
        db = DBSCAN(eps=eps_radians, min_samples=min_samples, metric='haversine')

        # 라디안으로 변환
        coords_radians = np.radians(coordinates)
        labels = db.fit_predict(coords_radians)

        # 클러스터별로 그룹화
        clusters = {}
        noise = []

        for idx, label in enumerate(labels):
            if label == -1:
                # 노이즈 (클러스터에 속하지 않음)
                noise.append(vehicles[idx])
            else:
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(vehicles[idx])

        # 클러스터 통계 계산
        cluster_stats = []
        for cluster_id, cluster_vehicles in clusters.items():
            # 중심 좌표 계산
            center_lat = np.mean([v.get('latitude', 0) for v in cluster_vehicles])
            center_lon = np.mean([v.get('longitude', 0) for v in cluster_vehicles])

            # 위험도 분포
            risk_counts = {
                'CRITICAL': sum(1 for v in cluster_vehicles if v.get('risk_level') == 'CRITICAL'),
                'HIGH': sum(1 for v in cluster_vehicles if v.get('risk_level') == 'HIGH'),
                'MEDIUM': sum(1 for v in cluster_vehicles if v.get('risk_level') == 'MEDIUM'),
                'LOW': sum(1 for v in cluster_vehicles if v.get('risk_level') == 'LOW')
            }

            # 평균 유사도
            avg_similarity = np.mean([v.get('similarity_percentage', 0) for v in cluster_vehicles])

            # 위험 점수 계산 (CRITICAL=4, HIGH=3, MEDIUM=2, LOW=1)
            risk_score = (
                risk_counts['CRITICAL'] * 4 +
                risk_counts['HIGH'] * 3 +
                risk_counts['MEDIUM'] * 2 +
                risk_counts['LOW'] * 1
            )

            cluster_stats.append({
                'cluster_id': int(cluster_id),
                'vehicle_count': len(cluster_vehicles),
                'center': {
                    'latitude': float(center_lat),
                    'longitude': float(center_lon)
                },
                'risk_distribution': risk_counts,
                'avg_similarity': float(avg_similarity),
                'risk_score': risk_score,
                'vehicles': cluster_vehicles
            })

        # 위험 점수 기준으로 정렬
        cluster_stats.sort(key=lambda x: x['risk_score'], reverse=True)

        return {
            "success": True,
            "total_vehicles": len(vehicles),
            "total_clusters": len(clusters),
            "noise_vehicles": len(noise),
            "clusters": cluster_stats,
            "noise": noise,
            "parameters": {
                "eps_km": eps_km,
                "min_samples": min_samples
            }
        }

    def generate_heatmap_data(
        self,
        vehicles: List[Dict],
        grid_size: float = 0.01  # 약 1km 그리드
    ) -> Dict:
        """
        히트맵 데이터 생성 (위험도 가중 밀도)

        Args:
            vehicles: 차량 리스트
            grid_size: 그리드 크기 (degrees, 약 1km)

        Returns:
            히트맵 데이터 (그리드별 차량 수 및 위험도)
        """
        if not vehicles:
            return {
                "success": False,
                "error": "차량 데이터가 없습니다",
                "heatmap": []
            }

        # 그리드별 집계
        grid_dict = {}

        for vehicle in vehicles:
            lat = vehicle.get('latitude', 0)
            lon = vehicle.get('longitude', 0)
            risk = vehicle.get('risk_level', 'LOW')

            # 그리드 인덱스 계산
            grid_lat = round(lat / grid_size) * grid_size
            grid_lon = round(lon / grid_size) * grid_size
            grid_key = (grid_lat, grid_lon)

            if grid_key not in grid_dict:
                grid_dict[grid_key] = {
                    'latitude': grid_lat,
                    'longitude': grid_lon,
                    'vehicle_count': 0,
                    'risk_score': 0,
                    'risk_counts': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
                }

            # 카운트 증가
            grid_dict[grid_key]['vehicle_count'] += 1
            grid_dict[grid_key]['risk_counts'][risk] += 1

            # 위험 점수 가중치
            risk_weights = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            grid_dict[grid_key]['risk_score'] += risk_weights.get(risk, 1)

        # 리스트로 변환
        heatmap_data = list(grid_dict.values())

        # 위험 점수 기준으로 정렬
        heatmap_data.sort(key=lambda x: x['risk_score'], reverse=True)

        return {
            "success": True,
            "total_grids": len(heatmap_data),
            "heatmap": heatmap_data,
            "parameters": {
                "grid_size": grid_size
            }
        }

    def analyze_by_city(self, vehicles: List[Dict]) -> Dict:
        """
        시/도별 통계 분석

        Args:
            vehicles: 차량 리스트

        Returns:
            시/도별 통계
        """
        city_stats = {}

        for vehicle in vehicles:
            city = vehicle.get('city', '알 수 없음')
            risk = vehicle.get('risk_level', 'LOW')

            if city not in city_stats:
                city_stats[city] = {
                    'city': city,
                    'total_count': 0,
                    'risk_counts': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
                    'avg_similarity': 0,
                    'total_similarity': 0
                }

            city_stats[city]['total_count'] += 1
            city_stats[city]['risk_counts'][risk] += 1
            city_stats[city]['total_similarity'] += vehicle.get('similarity_percentage', 0)

        # 평균 유사도 계산
        for city, stats in city_stats.items():
            if stats['total_count'] > 0:
                stats['avg_similarity'] = stats['total_similarity'] / stats['total_count']
            del stats['total_similarity']  # 임시 필드 제거

        # 리스트로 변환 및 정렬
        city_list = list(city_stats.values())
        city_list.sort(key=lambda x: x['total_count'], reverse=True)

        return {
            "success": True,
            "total_cities": len(city_list),
            "city_statistics": city_list
        }

    def analyze_trends(self, vehicles: List[Dict], days: int = 30) -> Dict:
        """
        시간대별 트렌드 분석 (최근 N일)

        Args:
            vehicles: 차량 리스트
            days: 분석 기간 (일)

        Returns:
            일별 통계
        """
        now = datetime.now()
        cutoff_date = now - timedelta(days=days)

        # 일별 집계
        daily_stats = {}

        for vehicle in vehicles:
            created_at = vehicle.get('created_at')
            if not created_at:
                continue

            # 문자열을 datetime으로 변환
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    continue

            # 날짜만 추출
            date_key = created_at.date().isoformat()

            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    'date': date_key,
                    'vehicle_count': 0,
                    'risk_counts': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
                }

            daily_stats[date_key]['vehicle_count'] += 1
            risk = vehicle.get('risk_level', 'LOW')
            daily_stats[date_key]['risk_counts'][risk] += 1

        # 리스트로 변환 및 정렬
        trend_list = list(daily_stats.values())
        trend_list.sort(key=lambda x: x['date'])

        return {
            "success": True,
            "period_days": days,
            "total_days": len(trend_list),
            "daily_trends": trend_list
        }


# 싱글톤 인스턴스
_analytics_service = None


def get_analytics_service() -> VehicleAnalyticsService:
    """
    Analytics 서비스 싱글톤 인스턴스 반환

    Returns:
        VehicleAnalyticsService 인스턴스
    """
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = VehicleAnalyticsService()
    return _analytics_service
