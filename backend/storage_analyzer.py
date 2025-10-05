import numpy as np
from sklearn.cluster import DBSCAN
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models import VehicleLocation
import math

class StorageAnalyzer:
    def __init__(self, cluster_radius_km: float = 0.5):
        """
        Initialize the storage analyzer
        
        Args:
            cluster_radius_km: Radius in kilometers for clustering vehicles
        """
        self.cluster_radius_km = cluster_radius_km
        self.cluster_radius_deg = cluster_radius_km / 111.0  # Rough conversion to degrees

    def analyze_storage_potential(self, vehicles: List[VehicleLocation]) -> Dict[str, Any]:
        """
        Analyze vehicles to identify potential long-term storage opportunities
        
        Args:
            vehicles: List of VehicleLocation objects
            
        Returns:
            Dictionary with storage analysis results
        """
        if not vehicles:
            return {
                'storage_potential': 0,
                'recommended_locations': [],
                'vehicle_clusters': [],
                'analysis_summary': 'No vehicles found in area'
            }
        
        # Convert to coordinates for clustering
        coordinates = np.array([[v.latitude, v.longitude] for v in vehicles])
        
        # Perform DBSCAN clustering
        clustering = DBSCAN(eps=self.cluster_radius_deg, min_samples=3)
        cluster_labels = clustering.fit_predict(coordinates)
        
        # Analyze clusters
        clusters = self._analyze_clusters(vehicles, cluster_labels)
        
        # Calculate storage potential score
        storage_potential = self._calculate_storage_potential(clusters, vehicles)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(clusters, vehicles)
        
        return {
            'storage_potential': storage_potential,
            'recommended_locations': recommendations,
            'vehicle_clusters': clusters,
            'analysis_summary': self._generate_analysis_summary(clusters, storage_potential),
            'total_vehicles': len(vehicles)
        }

    def _analyze_clusters(self, vehicles: List[VehicleLocation], cluster_labels: np.ndarray) -> List[Dict[str, Any]]:
        """Analyze vehicle clusters for storage potential"""
        clusters = []
        unique_labels = set(cluster_labels)
        
        for label in unique_labels:
            if label == -1:  # Noise points (not in any cluster)
                continue
                
            cluster_vehicles = [vehicles[i] for i in range(len(vehicles)) if cluster_labels[i] == label]
            
            if len(cluster_vehicles) < 3:  # Skip small clusters
                continue
            
            # Calculate cluster center
            center_lat = np.mean([v.latitude for v in cluster_vehicles])
            center_lng = np.mean([v.longitude for v in cluster_vehicles])
            
            # Analyze vehicle types in cluster
            vehicle_types = {}
            for vehicle in cluster_vehicles:
                vehicle_types[vehicle.vehicle_type] = vehicle_types.get(vehicle.vehicle_type, 0) + 1
            
            # Calculate cluster metrics
            cluster_metrics = self._calculate_cluster_metrics(cluster_vehicles)
            
            cluster_data = {
                'cluster_id': int(label),
                'center': {'latitude': center_lat, 'longitude': center_lng},
                'vehicle_count': len(cluster_vehicles),
                'vehicle_types': vehicle_types,
                'metrics': cluster_metrics,
                'vehicles': [v.to_dict() for v in cluster_vehicles]
            }
            
            clusters.append(cluster_data)
        
        return clusters

    def _calculate_cluster_metrics(self, vehicles: List[VehicleLocation]) -> Dict[str, Any]:
        """Calculate metrics for a vehicle cluster"""
        if not vehicles:
            return {}
        
        # Time analysis
        timestamps = [v.timestamp for v in vehicles]
        time_span = max(timestamps) - min(timestamps)
        
        # Spatial spread
        lats = [v.latitude for v in vehicles]
        lngs = [v.longitude for v in vehicles]
        spatial_spread = max(lats) - min(lats) + max(lngs) - min(lngs)
        
        # Average confidence
        avg_confidence = np.mean([v.confidence for v in vehicles])
        
        # Vehicle type diversity
        unique_types = len(set(v.vehicle_type for v in vehicles))
        
        return {
            'time_span_hours': time_span.total_seconds() / 3600,
            'spatial_spread_deg': spatial_spread,
            'average_confidence': avg_confidence,
            'vehicle_type_diversity': unique_types,
            'density': len(vehicles) / max(spatial_spread, 0.001)  # vehicles per degree
        }

    def _calculate_storage_potential(self, clusters: List[Dict], vehicles: List[VehicleLocation]) -> float:
        """Calculate overall storage potential score (0-100)"""
        if not clusters:
            return 0.0
        
        # Factors that indicate storage potential
        scores = []
        
        for cluster in clusters:
            score = 0
            
            # Vehicle count factor (more vehicles = higher potential)
            vehicle_count_score = min(cluster['vehicle_count'] * 5, 30)
            score += vehicle_count_score
            
            # Time span factor (longer presence = higher potential)
            time_score = min(cluster['metrics']['time_span_hours'] / 24 * 10, 20)
            score += time_score
            
            # Vehicle type factor (diverse types = higher potential)
            type_score = min(cluster['metrics']['vehicle_type_diversity'] * 5, 15)
            score += type_score
            
            # Spatial concentration factor (more concentrated = higher potential)
            concentration_score = min(cluster['metrics']['density'] * 10, 15)
            score += concentration_score
            
            # Confidence factor (higher confidence detections = higher potential)
            confidence_score = cluster['metrics']['average_confidence'] * 20
            score += confidence_score
            
            scores.append(score)
        
        # Return average score across all clusters
        return min(np.mean(scores), 100.0) if scores else 0.0

    def _generate_recommendations(self, clusters: List[Dict], vehicles: List[VehicleLocation]) -> List[Dict[str, Any]]:
        """Generate storage location recommendations"""
        recommendations = []
        
        for cluster in clusters:
            if cluster['vehicle_count'] >= 5:  # Only recommend for significant clusters
                recommendation = {
                    'location': cluster['center'],
                    'potential_score': self._calculate_cluster_storage_score(cluster),
                    'reasoning': self._generate_recommendation_reasoning(cluster),
                    'vehicle_count': cluster['vehicle_count'],
                    'primary_vehicle_types': self._get_primary_vehicle_types(cluster['vehicle_types'])
                }
                recommendations.append(recommendation)
        
        # Sort by potential score
        recommendations.sort(key=lambda x: x['potential_score'], reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations

    def _calculate_cluster_storage_score(self, cluster: Dict) -> float:
        """Calculate storage score for a specific cluster"""
        score = 0
        
        # Base score from vehicle count
        score += min(cluster['vehicle_count'] * 10, 50)
        
        # Bonus for time span
        if cluster['metrics']['time_span_hours'] > 48:
            score += 20
        elif cluster['metrics']['time_span_hours'] > 24:
            score += 10
        
        # Bonus for vehicle type diversity
        score += min(cluster['metrics']['vehicle_type_diversity'] * 5, 15)
        
        # Bonus for high confidence
        score += cluster['metrics']['average_confidence'] * 15
        
        return min(score, 100.0)

    def _generate_recommendation_reasoning(self, cluster: Dict) -> str:
        """Generate human-readable reasoning for recommendation"""
        reasons = []
        
        if cluster['vehicle_count'] >= 10:
            reasons.append(f"High vehicle concentration ({cluster['vehicle_count']} vehicles)")
        elif cluster['vehicle_count'] >= 5:
            reasons.append(f"Moderate vehicle concentration ({cluster['vehicle_count']} vehicles)")
        
        if cluster['metrics']['time_span_hours'] > 48:
            reasons.append("Vehicles present for extended periods (>48h)")
        elif cluster['metrics']['time_span_hours'] > 24:
            reasons.append("Vehicles present for significant time (>24h)")
        
        if cluster['metrics']['vehicle_type_diversity'] >= 3:
            reasons.append("Diverse vehicle types indicate mixed storage needs")
        
        if cluster['metrics']['average_confidence'] > 0.8:
            reasons.append("High confidence detections")
        
        return "; ".join(reasons) if reasons else "Potential storage area identified"

    def _get_primary_vehicle_types(self, vehicle_types: Dict[str, int]) -> List[str]:
        """Get the most common vehicle types in a cluster"""
        sorted_types = sorted(vehicle_types.items(), key=lambda x: x[1], reverse=True)
        return [vehicle_type for vehicle_type, count in sorted_types[:3]]

    def _generate_analysis_summary(self, clusters: List[Dict], storage_potential: float) -> str:
        """Generate a summary of the storage analysis"""
        if storage_potential > 70:
            return f"High storage potential identified with {len(clusters)} vehicle clusters"
        elif storage_potential > 40:
            return f"Moderate storage potential with {len(clusters)} vehicle clusters"
        elif storage_potential > 20:
            return f"Low storage potential with {len(clusters)} vehicle clusters"
        else:
            return "Minimal storage potential identified in this area"

    def find_long_term_vehicles(self, vehicles: List[VehicleLocation], days_threshold: int = 7) -> List[VehicleLocation]:
        """Find vehicles that have been in the same area for extended periods"""
        if not vehicles:
            return []
        
        # Group vehicles by location (within small radius)
        location_groups = {}
        
        for vehicle in vehicles:
            # Find existing group or create new one
            found_group = None
            for group_id, group_vehicles in location_groups.items():
                if self._is_near_location(vehicle, group_vehicles[0]):
                    found_group = group_id
                    break
            
            if found_group is None:
                found_group = len(location_groups)
                location_groups[found_group] = []
            
            location_groups[found_group].append(vehicle)
        
        # Filter groups that have vehicles present for extended periods
        long_term_vehicles = []
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        for group_vehicles in location_groups.values():
            if len(group_vehicles) >= 2:  # At least 2 detections
                # Check if vehicles were present for extended period
                timestamps = [v.timestamp for v in group_vehicles]
                if min(timestamps) < cutoff_date:
                    long_term_vehicles.extend(group_vehicles)
        
        return long_term_vehicles

    def _is_near_location(self, vehicle1: VehicleLocation, vehicle2: VehicleLocation, threshold_km: float = 0.1) -> bool:
        """Check if two vehicles are near each other"""
        lat_diff = abs(vehicle1.latitude - vehicle2.latitude)
        lng_diff = abs(vehicle1.longitude - vehicle2.longitude)
        
        # Rough distance calculation (not precise but fast)
        distance_km = math.sqrt(lat_diff**2 + lng_diff**2) * 111.0
        
        return distance_km < threshold_km

