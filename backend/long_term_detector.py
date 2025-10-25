import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster
from models import VehicleLocation
import math

class LongTermStoppedVehicleDetector:
    def __init__(self, 
                 stop_threshold_hours: float = 24.0,
                 movement_threshold_meters: float = 50.0,
                 cluster_radius_meters: float = 100.0,
                 min_stop_duration_hours: float = 6.0):
        """
        Advanced detector for long-term stopped vehicles
        
        Args:
            stop_threshold_hours: Hours after which a vehicle is considered "long-term stopped"
            movement_threshold_meters: Maximum movement in meters to consider vehicle "stopped"
            cluster_radius_meters: Radius for clustering nearby stopped vehicles
            min_stop_duration_hours: Minimum duration to be considered a significant stop
        """
        self.stop_threshold_hours = stop_threshold_hours
        self.movement_threshold_meters = movement_threshold_meters
        self.cluster_radius_meters = cluster_radius_meters
        self.min_stop_duration_hours = min_stop_duration_hours

    def detect_long_term_stopped_vehicles(self, 
                                        vehicles: List[VehicleLocation],
                                        analysis_start: datetime = None) -> Dict[str, Any]:
        """
        Detect vehicles that have been stopped for extended periods
        
        Args:
            vehicles: List of vehicle locations
            analysis_start: Start time for analysis (defaults to 7 days ago)
            
        Returns:
            Dictionary with detection results and analysis
        """
        if not vehicles:
            return self._empty_result()
        
        if analysis_start is None:
            analysis_start = datetime.now() - timedelta(days=7)
        
        # Filter vehicles within analysis period
        recent_vehicles = [v for v in vehicles if v.timestamp >= analysis_start]
        
        if len(recent_vehicles) < 2:
            return self._empty_result()
        
        # Group vehicles by potential vehicle ID (based on location and type)
        vehicle_groups = self._group_vehicles_by_location(recent_vehicles)
        
        # Analyze each group for stop patterns
        stopped_vehicles = []
        movement_patterns = []
        
        for group_id, group_vehicles in vehicle_groups.items():
            if len(group_vehicles) < 2:
                continue
                
            # Sort by timestamp
            group_vehicles.sort(key=lambda x: x.timestamp)
            
            # Analyze movement patterns
            pattern = self._analyze_movement_pattern(group_vehicles)
            movement_patterns.append(pattern)
            
            # Check if vehicle shows long-term stopping behavior
            if self._is_long_term_stopped(pattern):
                stopped_vehicles.append({
                    'vehicle_id': group_id,
                    'vehicles': group_vehicles,
                    'pattern': pattern,
                    'stop_duration_hours': pattern['total_stop_time_hours'],
                    'last_seen': group_vehicles[-1].timestamp,
                    'location': self._calculate_center_location(group_vehicles),
                    'confidence': pattern['stop_confidence']
                })
        
        # Cluster stopped vehicles by location
        stopped_clusters = self._cluster_stopped_vehicles(stopped_vehicles)
        
        # Calculate risk scores and generate alerts
        alerts = self._generate_stop_alerts(stopped_vehicles, stopped_clusters)
        
        return {
            'total_vehicles_analyzed': len(recent_vehicles),
            'stopped_vehicles_found': len(stopped_vehicles),
            'stop_clusters': len(stopped_clusters),
            'stopped_vehicles': stopped_vehicles,
            'clusters': stopped_clusters,
            'alerts': alerts,
            'analysis_period_hours': (datetime.now() - analysis_start).total_seconds() / 3600,
            'risk_assessment': self._assess_risk_level(stopped_vehicles, stopped_clusters)
        }

    def _group_vehicles_by_location(self, vehicles: List[VehicleLocation]) -> Dict[str, List[VehicleLocation]]:
        """Group vehicles that are likely the same vehicle based on location proximity"""
        groups = {}
        used_vehicles = set()
        
        for i, vehicle in enumerate(vehicles):
            if i in used_vehicles:
                continue
                
            # Create a new group for this vehicle
            group_id = f"vehicle_{len(groups)}"
            groups[group_id] = [vehicle]
            used_vehicles.add(i)
            
            # Find nearby vehicles that might be the same vehicle
            for j, other_vehicle in enumerate(vehicles):
                if j in used_vehicles or i == j:
                    continue
                    
                distance = self._calculate_distance(vehicle, other_vehicle)
                time_diff = abs((vehicle.timestamp - other_vehicle.timestamp).total_seconds() / 3600)
                
                # Same vehicle if close in location and time, and same type
                if (distance < self.movement_threshold_meters and 
                    time_diff < 24 and 
                    vehicle.vehicle_type == other_vehicle.vehicle_type):
                    groups[group_id].append(other_vehicle)
                    used_vehicles.add(j)
        
        return groups

    def _analyze_movement_pattern(self, vehicles: List[VehicleLocation]) -> Dict[str, Any]:
        """Analyze the movement pattern of a vehicle group"""
        if len(vehicles) < 2:
            return self._empty_pattern()
        
        # Calculate movement metrics
        total_distance = 0
        total_time = 0
        stop_periods = []
        current_stop_start = None
        current_stop_location = None
        
        for i in range(1, len(vehicles)):
            prev_vehicle = vehicles[i-1]
            curr_vehicle = vehicles[i]
            
            distance = self._calculate_distance(prev_vehicle, curr_vehicle)
            time_diff = (curr_vehicle.timestamp - prev_vehicle.timestamp).total_seconds() / 3600
            
            total_distance += distance
            total_time += time_diff
            
            # Detect stops (no significant movement)
            if distance < self.movement_threshold_meters:
                if current_stop_start is None:
                    current_stop_start = prev_vehicle.timestamp
                    current_stop_location = prev_vehicle
            else:
                if current_stop_start is not None:
                    stop_duration = (curr_vehicle.timestamp - current_stop_start).total_seconds() / 3600
                    if stop_duration >= self.min_stop_duration_hours:
                        stop_periods.append({
                            'start_time': current_stop_start,
                            'end_time': curr_vehicle.timestamp,
                            'duration_hours': stop_duration,
                            'location': current_stop_location,
                            'confidence': min(stop_duration / self.stop_threshold_hours, 1.0)
                        })
                    current_stop_start = None
                    current_stop_location = None
        
        # Handle case where vehicle is still stopped
        if current_stop_start is not None:
            stop_duration = (vehicles[-1].timestamp - current_stop_start).total_seconds() / 3600
            if stop_duration >= self.min_stop_duration_hours:
                stop_periods.append({
                    'start_time': current_stop_start,
                    'end_time': vehicles[-1].timestamp,
                    'duration_hours': stop_duration,
                    'location': current_stop_location,
                    'confidence': min(stop_duration / self.stop_threshold_hours, 1.0)
                })
        
        # Calculate pattern metrics
        total_stop_time = sum(sp['duration_hours'] for sp in stop_periods)
        avg_speed = total_distance / max(total_time, 0.1)  # km/h
        
        # Calculate stop confidence based on multiple factors
        stop_confidence = self._calculate_stop_confidence(
            stop_periods, total_stop_time, total_time, avg_speed
        )
        
        return {
            'total_detections': len(vehicles),
            'total_distance_km': total_distance / 1000,
            'total_time_hours': total_time,
            'avg_speed_kmh': avg_speed,
            'stop_periods': stop_periods,
            'total_stop_time_hours': total_stop_time,
            'stop_confidence': stop_confidence,
            'movement_score': self._calculate_movement_score(avg_speed, total_distance, total_time),
            'first_seen': vehicles[0].timestamp,
            'last_seen': vehicles[-1].timestamp
        }

    def _is_long_term_stopped(self, pattern: Dict[str, Any]) -> bool:
        """Determine if a vehicle pattern indicates long-term stopping"""
        if pattern['total_stop_time_hours'] < self.min_stop_duration_hours:
            return False
        
        # Check if vehicle has been stopped for significant time
        if pattern['total_stop_time_hours'] >= self.stop_threshold_hours:
            return True
        
        # Check if stop confidence is high
        if pattern['stop_confidence'] > 0.7:
            return True
        
        # Check if there's a recent long stop period
        recent_stops = [
            sp for sp in pattern['stop_periods'] 
            if (datetime.now() - sp['end_time']).total_seconds() < 24 * 3600
        ]
        
        if recent_stops and max(sp['duration_hours'] for sp in recent_stops) > 12:
            return True
        
        return False

    def _calculate_stop_confidence(self, 
                                 stop_periods: List[Dict], 
                                 total_stop_time: float, 
                                 total_time: float,
                                 avg_speed: float) -> float:
        """Calculate confidence that vehicle is actually stopped long-term"""
        if total_time == 0:
            return 0.0
        
        # Base confidence from stop time ratio
        stop_ratio = total_stop_time / total_time
        
        # Adjust for speed (lower speed = higher confidence)
        speed_factor = max(0, 1 - (avg_speed / 50))  # Assume 50 km/h is normal movement
        
        # Adjust for number of stop periods (more stops = lower confidence)
        stop_count_factor = 1.0 / (1.0 + len(stop_periods) * 0.1)
        
        # Adjust for longest single stop
        longest_stop = max([sp['duration_hours'] for sp in stop_periods], default=0)
        longest_stop_factor = min(longest_stop / self.stop_threshold_hours, 1.0)
        
        confidence = (stop_ratio * 0.4 + 
                     speed_factor * 0.3 + 
                     stop_count_factor * 0.2 + 
                     longest_stop_factor * 0.1)
        
        return min(confidence, 1.0)

    def _calculate_movement_score(self, avg_speed: float, total_distance: float, total_time: float) -> float:
        """Calculate a score indicating how much the vehicle moved"""
        if total_time == 0:
            return 0.0
        
        # Normalize speed and distance
        speed_score = min(avg_speed / 50, 1.0)  # 50 km/h as max normal speed
        distance_score = min(total_distance / 10000, 1.0)  # 10km as significant distance
        
        return (speed_score + distance_score) / 2

    def _cluster_stopped_vehicles(self, stopped_vehicles: List[Dict]) -> List[Dict]:
        """Cluster stopped vehicles by location"""
        if len(stopped_vehicles) < 2:
            return []
        
        # Extract coordinates for clustering
        coordinates = np.array([[v['location']['latitude'], v['location']['longitude']] 
                               for v in stopped_vehicles])
        
        # Convert cluster radius from meters to approximate degrees
        cluster_radius_deg = self.cluster_radius_meters / 111000  # Rough conversion
        
        # Use DBSCAN for clustering
        clustering = DBSCAN(eps=cluster_radius_deg, min_samples=2)
        cluster_labels = clustering.fit_predict(coordinates)
        
        # Group vehicles by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label == -1:  # Noise points
                continue
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(stopped_vehicles[i])
        
        # Convert to list format with metadata
        cluster_list = []
        for cluster_id, cluster_vehicles in clusters.items():
            center_lat = np.mean([v['location']['latitude'] for v in cluster_vehicles])
            center_lng = np.mean([v['location']['longitude'] for v in cluster_vehicles])
            
            cluster_list.append({
                'cluster_id': cluster_id,
                'center': {'latitude': center_lat, 'longitude': center_lng},
                'vehicle_count': len(cluster_vehicles),
                'vehicles': cluster_vehicles,
                'total_stop_time': sum(v['stop_duration_hours'] for v in cluster_vehicles),
                'avg_confidence': np.mean([v['confidence'] for v in cluster_vehicles]),
                'risk_level': self._calculate_cluster_risk(cluster_vehicles)
            })
        
        return cluster_list

    def _calculate_cluster_risk(self, cluster_vehicles: List[Dict]) -> str:
        """Calculate risk level for a cluster of stopped vehicles"""
        avg_confidence = np.mean([v['confidence'] for v in cluster_vehicles])
        vehicle_count = len(cluster_vehicles)
        total_stop_time = sum(v['stop_duration_hours'] for v in cluster_vehicles)
        
        if avg_confidence > 0.8 and vehicle_count >= 3:
            return 'HIGH'
        elif avg_confidence > 0.6 and vehicle_count >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _generate_stop_alerts(self, 
                            stopped_vehicles: List[Dict], 
                            clusters: List[Dict]) -> List[Dict]:
        """Generate alerts for concerning stop patterns"""
        alerts = []
        
        # Individual vehicle alerts
        for vehicle in stopped_vehicles:
            if vehicle['stop_duration_hours'] > self.stop_threshold_hours * 2:
                alerts.append({
                    'type': 'LONG_TERM_STOP',
                    'severity': 'HIGH',
                    'vehicle_id': vehicle['vehicle_id'],
                    'location': vehicle['location'],
                    'duration_hours': vehicle['stop_duration_hours'],
                    'message': f"Vehicle stopped for {vehicle['stop_duration_hours']:.1f} hours",
                    'timestamp': vehicle['last_seen']
                })
        
        # Cluster alerts
        for cluster in clusters:
            if cluster['risk_level'] == 'HIGH':
                alerts.append({
                    'type': 'STOP_CLUSTER',
                    'severity': 'HIGH',
                    'location': cluster['center'],
                    'vehicle_count': cluster['vehicle_count'],
                    'total_stop_time': cluster['total_stop_time'],
                    'message': f"{cluster['vehicle_count']} vehicles stopped in same area",
                    'timestamp': datetime.now()
                })
        
        return alerts

    def _assess_risk_level(self, 
                         stopped_vehicles: List[Dict], 
                         clusters: List[Dict]) -> Dict[str, Any]:
        """Assess overall risk level of the area"""
        if not stopped_vehicles:
            return {'level': 'LOW', 'score': 0, 'description': 'No stopped vehicles detected'}
        
        high_risk_vehicles = [v for v in stopped_vehicles if v['confidence'] > 0.8]
        high_risk_clusters = [c for c in clusters if c['risk_level'] == 'HIGH']
        
        risk_score = 0
        risk_score += len(stopped_vehicles) * 10
        risk_score += len(high_risk_vehicles) * 20
        risk_score += len(high_risk_clusters) * 30
        
        if risk_score >= 100:
            level = 'HIGH'
        elif risk_score >= 50:
            level = 'MEDIUM'
        else:
            level = 'LOW'
        
        return {
            'level': level,
            'score': risk_score,
            'description': f'{len(stopped_vehicles)} stopped vehicles, {len(high_risk_clusters)} high-risk clusters',
            'recommendations': self._generate_recommendations(level, stopped_vehicles, clusters)
        }

    def _generate_recommendations(self, 
                                risk_level: str, 
                                stopped_vehicles: List[Dict], 
                                clusters: List[Dict]) -> List[str]:
        """Generate recommendations based on risk assessment"""
        recommendations = []
        
        if risk_level == 'HIGH':
            recommendations.extend([
                'Immediate investigation recommended',
                'Consider deploying surveillance',
                'Check for abandoned vehicles',
                'Monitor for illegal parking'
            ])
        elif risk_level == 'MEDIUM':
            recommendations.extend([
                'Periodic monitoring recommended',
                'Check for parking violations',
                'Verify vehicle ownership'
            ])
        else:
            recommendations.extend([
                'Routine monitoring sufficient',
                'Standard parking enforcement'
            ])
        
        return recommendations

    def _calculate_distance(self, vehicle1: VehicleLocation, vehicle2: VehicleLocation) -> float:
        """Calculate distance between two vehicles in meters"""
        lat1, lng1 = vehicle1.latitude, vehicle1.longitude
        lat2, lng2 = vehicle2.latitude, vehicle2.longitude
        
        # Haversine formula for accurate distance calculation
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng/2) * math.sin(delta_lng/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance

    def _calculate_center_location(self, vehicles: List[VehicleLocation]) -> Dict[str, float]:
        """Calculate center location of a group of vehicles"""
        if not vehicles:
            return {'latitude': 0, 'longitude': 0}
        
        lat = np.mean([v.latitude for v in vehicles])
        lng = np.mean([v.longitude for v in vehicles])
        
        return {'latitude': lat, 'longitude': lng}

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            'total_vehicles_analyzed': 0,
            'stopped_vehicles_found': 0,
            'stop_clusters': 0,
            'stopped_vehicles': [],
            'clusters': [],
            'alerts': [],
            'analysis_period_hours': 0,
            'risk_assessment': {'level': 'LOW', 'score': 0, 'description': 'No data available'}
        }

    def _empty_pattern(self) -> Dict[str, Any]:
        """Return empty pattern structure"""
        return {
            'total_detections': 0,
            'total_distance_km': 0,
            'total_time_hours': 0,
            'avg_speed_kmh': 0,
            'stop_periods': [],
            'total_stop_time_hours': 0,
            'stop_confidence': 0,
            'movement_score': 0,
            'first_seen': None,
            'last_seen': None
        }
