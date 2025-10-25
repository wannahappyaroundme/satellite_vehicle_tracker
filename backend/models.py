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


class AbandonedVehicleHistory(db.Model):
    """
    방치 차량 이력 추적 모델
    같은 차량이 반복 감지될 때 이력을 누적
    """
    __tablename__ = 'abandoned_vehicle_history'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(100), unique=True, nullable=False, index=True)

    # 위치 정보
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200))

    # 차량 정보
    vehicle_type = db.Column(db.String(50))  # car, truck, bus
    risk_level = db.Column(db.String(20))    # CRITICAL, HIGH, MEDIUM, LOW

    # 이력 정보
    first_detected = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_checked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    detection_count = db.Column(db.Integer, default=1)  # 감지 횟수

    # 유사도 정보
    avg_similarity = db.Column(db.Float)     # 평균 유사도
    max_similarity = db.Column(db.Float)     # 최고 유사도
    years_difference = db.Column(db.Integer) # 경과 년수

    # 처리 상태
    status = db.Column(db.String(20), default='DETECTED')  # DETECTED, INVESTIGATING, RESOLVED
    notes = db.Column(db.Text)  # 관리자 메모

    # 메타데이터
    bbox_data = db.Column(db.JSON)  # Bounding box 정보
    metadata = db.Column(db.JSON)   # 추가 메타데이터

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """JSON 직렬화"""
        # 방치 기간 계산
        if self.first_detected:
            days_abandoned = (datetime.utcnow() - self.first_detected).days
        else:
            days_abandoned = 0

        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'vehicle_type': self.vehicle_type,
            'risk_level': self.risk_level,
            'first_detected': self.first_detected.isoformat() if self.first_detected else None,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'detection_count': self.detection_count,
            'days_abandoned': days_abandoned,
            'avg_similarity': self.avg_similarity,
            'max_similarity': self.max_similarity,
            'years_difference': self.years_difference,
            'status': self.status,
            'notes': self.notes,
            'bbox_data': self.bbox_data,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_detection(self, similarity_score: float, risk_level: str):
        """
        새로운 감지 시 이력 업데이트
        """
        self.last_checked = datetime.utcnow()
        self.detection_count += 1
        self.risk_level = risk_level

        # 평균 유사도 업데이트
        if self.avg_similarity:
            self.avg_similarity = (self.avg_similarity * (self.detection_count - 1) + similarity_score) / self.detection_count
        else:
            self.avg_similarity = similarity_score

        # 최고 유사도 업데이트
        if not self.max_similarity or similarity_score > self.max_similarity:
            self.max_similarity = similarity_score

