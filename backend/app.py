from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import cv2
import numpy as np
from PIL import Image
import io
import base64
import os
from datetime import datetime, timedelta
import json
from models import db, Vehicle, VehicleLocation, StorageAnalysis
from vehicle_detector import VehicleDetector
from storage_analyzer import StorageAnalyzer
from long_term_detector import LongTermStoppedVehicleDetector
from vehicle_classifier import AdvancedVehicleClassifier
from south_korea_satellite import SouthKoreaSatelliteService
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize database
db.init_app(app)

# Initialize AI models
vehicle_detector = VehicleDetector()
storage_analyzer = StorageAnalyzer()
long_term_detector = LongTermStoppedVehicleDetector()
vehicle_classifier = AdvancedVehicleClassifier()
satellite_service = SouthKoreaSatelliteService()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """Process uploaded satellite imagery and detect vehicles"""
    try:
        data = request.json
        image_data = data.get('image')  # Base64 encoded image
        coordinates = data.get('coordinates')  # {lat, lng, zoom}
        
        if not image_data or not coordinates:
            return jsonify({"error": "Missing image or coordinates"}), 400
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        image_np = np.array(image)
        
        # Detect vehicles
        detections = vehicle_detector.detect_vehicles(image_np)
        
        # Enhanced classification for each detection
        enhanced_detections = []
        for detection in detections:
            # Get detailed classification
            detailed_classification = vehicle_classifier.classify_vehicle_detailed(image_np, detection)
            
            # Calculate coordinates
            vehicle_lat = coordinates['lat'] + (detection['y'] - image_np.shape[0]/2) * 0.0001
            vehicle_lng = coordinates['lng'] + (detection['x'] - image_np.shape[1]/2) * 0.0001
            
            # Create enhanced detection
            enhanced_detection = {
                **detection,
                'classification': detailed_classification,
                'latitude': vehicle_lat,
                'longitude': vehicle_lng
            }
            enhanced_detections.append(enhanced_detection)
        
        # Save vehicle locations to database
        vehicle_locations = []
        for detection in enhanced_detections:
            location = VehicleLocation(
                latitude=detection['latitude'],
                longitude=detection['longitude'],
                confidence=detection['classification']['overall_confidence'],
                vehicle_type=detection['classification']['vehicle_type'],
                timestamp=datetime.now(),
                image_coords={'x': detection['x'], 'y': detection['y']}
            )
            db.session.add(location)
            vehicle_locations.append(location)
        
        db.session.commit()
        
        return jsonify({
            "detections": len(enhanced_detections),
            "vehicles": [{
                "id": loc.id,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "confidence": loc.confidence,
                "type": loc.vehicle_type,
                "timestamp": loc.timestamp.isoformat(),
                "classification": enhanced_detections[i]['classification'] if i < len(enhanced_detections) else None
            } for i, loc in enumerate(vehicle_locations)]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search-vehicles', methods=['GET'])
def search_vehicles():
    """Search for vehicles in a specific area"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        radius = float(request.args.get('radius', 0.01))  # Default ~1km
        vehicle_type = request.args.get('type')
        time_range = request.args.get('time_range', '24h')  # 24h, 7d, 30d
        
        # Calculate time filter
        if time_range == '24h':
            time_filter = datetime.now() - timedelta(hours=24)
        elif time_range == '7d':
            time_filter = datetime.now() - timedelta(days=7)
        elif time_range == '30d':
            time_filter = datetime.now() - timedelta(days=30)
        else:
            time_filter = datetime.now() - timedelta(hours=24)
        
        # Query vehicles in area
        query = VehicleLocation.query.filter(
            VehicleLocation.timestamp >= time_filter,
            VehicleLocation.latitude.between(lat - radius, lat + radius),
            VehicleLocation.longitude.between(lng - radius, lng + radius)
        )
        
        if vehicle_type:
            query = query.filter(VehicleLocation.vehicle_type == vehicle_type)
        
        vehicles = query.all()
        
        return jsonify({
            "count": len(vehicles),
            "vehicles": [{
                "id": v.id,
                "latitude": v.latitude,
                "longitude": v.longitude,
                "confidence": v.confidence,
                "type": v.vehicle_type,
                "timestamp": v.timestamp.isoformat()
            } for v in vehicles]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/storage-analysis', methods=['GET'])
def storage_analysis():
    """Analyze vehicles that might be seeking long-term storage"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        radius = float(request.args.get('radius', 0.01))
        
        # Get recent vehicles in area
        recent_time = datetime.now() - timedelta(days=7)
        vehicles = VehicleLocation.query.filter(
            VehicleLocation.timestamp >= recent_time,
            VehicleLocation.latitude.between(lat - radius, lat + radius),
            VehicleLocation.longitude.between(lng - radius, lng + radius)
        ).all()
        
        # Analyze for storage patterns
        analysis = storage_analyzer.analyze_storage_potential(vehicles)
        
        return jsonify({
            "total_vehicles": len(vehicles),
            "storage_potential": analysis['storage_potential'],
            "recommended_locations": analysis['recommended_locations'],
            "vehicle_clusters": analysis['vehicle_clusters']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/aircraft-search', methods=['GET'])
def search_aircraft():
    """Search for aircraft in satellite imagery"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        radius = float(request.args.get('radius', 0.01))
        
        # Search for aircraft specifically
        aircraft = VehicleLocation.query.filter(
            VehicleLocation.latitude.between(lat - radius, lat + radius),
            VehicleLocation.longitude.between(lng - radius, lng + radius),
            VehicleLocation.vehicle_type.in_(['aircraft', 'plane', 'helicopter'])
        ).all()
        
        return jsonify({
            "count": len(aircraft),
            "aircraft": [{
                "id": a.id,
                "latitude": a.latitude,
                "longitude": a.longitude,
                "confidence": a.confidence,
                "type": a.vehicle_type,
                "timestamp": a.timestamp.isoformat()
            } for a in aircraft]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/long-term-stopped', methods=['GET'])
def detect_long_term_stopped():
    """Detect long-term stopped vehicles in a specific area"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        radius = float(request.args.get('radius', 0.01))
        days_back = int(request.args.get('days_back', 7))
        
        # Get vehicles in area within time range
        start_time = datetime.now() - timedelta(days=days_back)
        vehicles = VehicleLocation.query.filter(
            VehicleLocation.timestamp >= start_time,
            VehicleLocation.latitude.between(lat - radius, lat + radius),
            VehicleLocation.longitude.between(lng - radius, lng + radius)
        ).all()
        
        # Run long-term detection analysis
        analysis = long_term_detector.detect_long_term_stopped_vehicles(
            vehicles, 
            analysis_start=start_time
        )
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vehicle-history/<int:vehicle_id>', methods=['GET'])
def get_vehicle_history(vehicle_id):
    """Get movement history for a specific vehicle"""
    try:
        vehicle = VehicleLocation.query.get(vehicle_id)
        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404
        
        # Find similar vehicles (same type, nearby location)
        radius = 0.001  # ~100m radius
        similar_vehicles = VehicleLocation.query.filter(
            VehicleLocation.vehicle_type == vehicle.vehicle_type,
            VehicleLocation.latitude.between(vehicle.latitude - radius, vehicle.latitude + radius),
            VehicleLocation.longitude.between(vehicle.longitude - radius, vehicle.longitude + radius)
        ).order_by(VehicleLocation.timestamp).all()
        
        # Analyze movement pattern
        if len(similar_vehicles) > 1:
            pattern = long_term_detector._analyze_movement_pattern(similar_vehicles)
        else:
            pattern = {"total_detections": 1, "movement_score": 0, "stop_periods": []}
        
        return jsonify({
            "vehicle_id": vehicle_id,
            "vehicle_type": vehicle.vehicle_type,
            "total_detections": len(similar_vehicles),
            "movement_pattern": pattern,
            "history": [v.to_dict() for v in similar_vehicles]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/area-summary', methods=['GET'])
def get_area_summary():
    """Get comprehensive summary of vehicle activity in an area"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        radius = float(request.args.get('radius', 0.01))
        days_back = int(request.args.get('days_back', 7))
        
        start_time = datetime.now() - timedelta(days=days_back)
        
        # Get all vehicles in area
        vehicles = VehicleLocation.query.filter(
            VehicleLocation.timestamp >= start_time,
            VehicleLocation.latitude.between(lat - radius, lat + radius),
            VehicleLocation.longitude.between(lng - radius, lng + radius)
        ).all()
        
        if not vehicles:
            return jsonify({
                "area": {"latitude": lat, "longitude": lng, "radius_km": radius * 111},
                "summary": "No vehicle activity detected in this area",
                "total_vehicles": 0,
                "vehicle_types": {},
                "time_range": f"{days_back} days",
                "risk_level": "LOW"
            })
        
        # Analyze vehicle types
        vehicle_types = {}
        for vehicle in vehicles:
            vehicle_types[vehicle.vehicle_type] = vehicle_types.get(vehicle.vehicle_type, 0) + 1
        
        # Run long-term detection
        long_term_analysis = long_term_detector.detect_long_term_stopped_vehicles(vehicles, start_time)
        
        # Run storage analysis
        storage_analysis = storage_analyzer.analyze_storage_potential(vehicles)
        
        return jsonify({
            "area": {
                "latitude": lat,
                "longitude": lng,
                "radius_km": radius * 111
            },
            "summary": {
                "total_vehicles": len(vehicles),
                "vehicle_types": vehicle_types,
                "time_range_days": days_back,
                "analysis_period": f"{start_time.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}"
            },
            "long_term_analysis": long_term_analysis,
            "storage_analysis": storage_analysis,
            "risk_assessment": {
                "long_term_risk": long_term_analysis["risk_assessment"]["level"],
                "storage_potential": storage_analysis["storage_potential"],
                "overall_risk": "HIGH" if (
                    long_term_analysis["risk_assessment"]["level"] == "HIGH" or 
                    storage_analysis["storage_potential"] > 70
                ) else "MEDIUM" if (
                    long_term_analysis["risk_assessment"]["level"] == "MEDIUM" or 
                    storage_analysis["storage_potential"] > 40
                ) else "LOW"
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/south-korea/coverage', methods=['GET'])
def get_south_korea_coverage():
    """Get satellite imagery coverage for South Korea locations"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        radius = float(request.args.get('radius', 1.0))
        
        coverage = satellite_service.get_south_korea_coverage(lat, lng, radius)
        return jsonify(coverage)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/south-korea/imagery', methods=['GET'])
def get_recent_imagery():
    """Get recent satellite imagery for South Korea locations"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        days_back = int(request.args.get('days_back', 30))
        
        imagery = satellite_service.get_recent_imagery(lat, lng, days_back)
        return jsonify({
            "location": {"latitude": lat, "longitude": lng},
            "days_back": days_back,
            "imagery_count": len(imagery),
            "imagery": imagery
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/south-korea/cities', methods=['GET'])
def get_cities_coverage():
    """Get satellite coverage for major South Korean cities"""
    try:
        coverage = satellite_service.get_major_cities_coverage()
        return jsonify(coverage)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/south-korea/download-guide', methods=['GET'])
def get_download_guide():
    """Get instructions for downloading satellite imagery"""
    try:
        guide = satellite_service.get_download_instructions()
        return jsonify(guide)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vehicle/<int:vehicle_id>/details', methods=['GET'])
def get_vehicle_details(vehicle_id):
    """Get detailed vehicle information including classification and parking duration"""
    try:
        vehicle = VehicleLocation.query.get(vehicle_id)
        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404
        
        # Find similar vehicles for parking duration analysis
        radius = 0.001  # ~100m radius
        similar_vehicles = VehicleLocation.query.filter(
            VehicleLocation.vehicle_type == vehicle.vehicle_type,
            VehicleLocation.latitude.between(vehicle.latitude - radius, vehicle.latitude + radius),
            VehicleLocation.longitude.between(vehicle.longitude - radius, vehicle.longitude + radius)
        ).order_by(VehicleLocation.timestamp).all()
        
        # Analyze parking duration
        parking_analysis = vehicle_classifier.get_parking_duration_analysis(
            str(vehicle_id), 
            [v.to_dict() for v in similar_vehicles]
        )
        
        return jsonify({
            "vehicle": vehicle.to_dict(),
            "parking_analysis": parking_analysis,
            "similar_vehicles_count": len(similar_vehicles),
            "analysis_timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

