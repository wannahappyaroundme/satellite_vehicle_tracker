from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(100), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    locations = db.relationship('VehicleLocation', backref='vehicle', lazy=True)

class VehicleLocation(db.Model):
    __tablename__ = 'vehicle_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_coords = db.Column(db.JSON)  # Store x,y coordinates in original image
    
    # Additional metadata
    altitude = db.Column(db.Float)
    heading = db.Column(db.Float)
    speed = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'confidence': self.confidence,
            'vehicle_type': self.vehicle_type,
            'timestamp': self.timestamp.isoformat(),
            'image_coords': self.image_coords,
            'altitude': self.altitude,
            'heading': self.heading,
            'speed': self.speed
        }

class StorageAnalysis(db.Model):
    __tablename__ = 'storage_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    storage_potential_score = db.Column(db.Float, nullable=False)
    vehicle_count = db.Column(db.Integer, nullable=False)
    vehicle_types = db.Column(db.JSON)  # Store types and counts
    recommendations = db.Column(db.JSON)  # Store recommendations
    
    def to_dict(self):
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'analysis_date': self.analysis_date.isoformat(),
            'storage_potential_score': self.storage_potential_score,
            'vehicle_count': self.vehicle_count,
            'vehicle_types': self.vehicle_types,
            'recommendations': self.recommendations
        }

