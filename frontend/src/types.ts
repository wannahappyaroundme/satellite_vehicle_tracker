export interface VehicleData {
  id: number;
  latitude: number;
  longitude: number;
  confidence: number;
  type: string;
  timestamp: string;
  image_coords?: {
    x: number;
    y: number;
  };
  altitude?: number;
  heading?: number;
  speed?: number;
}

export interface StorageAnalysisData {
  storage_potential: number;
  recommended_locations: RecommendedLocation[];
  vehicle_clusters: VehicleCluster[];
  analysis_summary: string;
  total_vehicles: number;
}

export interface RecommendedLocation {
  location: {
    latitude: number;
    longitude: number;
  };
  potential_score: number;
  reasoning: string;
  vehicle_count: number;
  primary_vehicle_types: string[];
}

export interface VehicleCluster {
  cluster_id: number;
  center: {
    latitude: number;
    longitude: number;
  };
  vehicle_count: number;
  vehicle_types: Record<string, number>;
  metrics: {
    time_span_hours: number;
    spatial_spread_deg: number;
    average_confidence: number;
    vehicle_type_diversity: number;
    density: number;
  };
  vehicles: VehicleData[];
}

export interface SearchFilters {
  vehicle_type?: string;
  time_range: '24h' | '7d' | '30d';
  radius: number;
  min_confidence: number;
}

export interface UploadImageData {
  image: string; // Base64 encoded
  coordinates: {
    lat: number;
    lng: number;
    zoom: number;
  };
}

