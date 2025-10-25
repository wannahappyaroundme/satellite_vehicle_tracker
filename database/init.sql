-- Initialize database for Satellite Vehicle Tracker

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_vehicle_locations_coordinates 
ON vehicle_locations USING GIST (ST_Point(longitude, latitude));

CREATE INDEX IF NOT EXISTS idx_vehicle_locations_timestamp 
ON vehicle_locations (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_vehicle_locations_type 
ON vehicle_locations (vehicle_type);

CREATE INDEX IF NOT EXISTS idx_vehicle_locations_confidence 
ON vehicle_locations (confidence DESC);

-- Create spatial index for storage analyses
CREATE INDEX IF NOT EXISTS idx_storage_analyses_coordinates 
ON storage_analyses USING GIST (ST_Point(longitude, latitude));

-- Create function for distance calculation
CREATE OR REPLACE FUNCTION calculate_distance(lat1 float, lon1 float, lat2 float, lon2 float)
RETURNS float AS $$
BEGIN
    RETURN ST_Distance(
        ST_Point(lon1, lat1)::geography,
        ST_Point(lon2, lat2)::geography
    );
END;
$$ LANGUAGE plpgsql;

-- Create function for finding nearby vehicles
CREATE OR REPLACE FUNCTION find_nearby_vehicles(
    center_lat float,
    center_lon float,
    radius_meters float,
    vehicle_type_filter text DEFAULT NULL
)
RETURNS TABLE (
    id integer,
    latitude float,
    longitude float,
    confidence float,
    vehicle_type text,
    timestamp timestamp,
    distance_meters float
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vl.id,
        vl.latitude,
        vl.longitude,
        vl.confidence,
        vl.vehicle_type,
        vl.timestamp,
        calculate_distance(center_lat, center_lon, vl.latitude, vl.longitude) as distance_meters
    FROM vehicle_locations vl
    WHERE 
        calculate_distance(center_lat, center_lon, vl.latitude, vl.longitude) <= radius_meters
        AND (vehicle_type_filter IS NULL OR vl.vehicle_type = vehicle_type_filter)
    ORDER BY distance_meters;
END;
$$ LANGUAGE plpgsql;

-- Create view for recent vehicle activity
CREATE OR REPLACE VIEW recent_vehicle_activity AS
SELECT 
    vehicle_type,
    COUNT(*) as vehicle_count,
    AVG(confidence) as avg_confidence,
    MAX(timestamp) as last_seen,
    MIN(timestamp) as first_seen
FROM vehicle_locations
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY vehicle_type
ORDER BY vehicle_count DESC;

-- Create view for long-term stopped vehicles
CREATE OR REPLACE VIEW long_term_stopped_vehicles AS
SELECT 
    vl1.id,
    vl1.latitude,
    vl1.longitude,
    vl1.vehicle_type,
    vl1.confidence,
    vl1.timestamp,
    COUNT(vl2.id) as detection_count,
    MAX(vl2.timestamp) - MIN(vl2.timestamp) as time_span,
    AVG(calculate_distance(vl1.latitude, vl1.longitude, vl2.latitude, vl2.longitude)) as avg_movement
FROM vehicle_locations vl1
JOIN vehicle_locations vl2 ON 
    vl1.vehicle_type = vl2.vehicle_type
    AND calculate_distance(vl1.latitude, vl1.longitude, vl2.latitude, vl2.longitude) < 50
    AND ABS(EXTRACT(EPOCH FROM (vl1.timestamp - vl2.timestamp))) < 86400
WHERE vl1.timestamp >= NOW() - INTERVAL '7 days'
GROUP BY vl1.id, vl1.latitude, vl1.longitude, vl1.vehicle_type, vl1.confidence, vl1.timestamp
HAVING COUNT(vl2.id) >= 3 AND MAX(vl2.timestamp) - MIN(vl2.timestamp) > INTERVAL '24 hours'
ORDER BY detection_count DESC;
