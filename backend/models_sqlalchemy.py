"""
SQLAlchemy Models for Abandoned Vehicle Detection System
파일 기반 SQLite 데이터베이스 모델
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Index, Text
from sqlalchemy.sql import func
from database import Base
from datetime import datetime
from typing import Dict, Optional


class AbandonedVehicle(Base):
    """
    방치 차량 이력 추적 모델 (SQLAlchemy ORM)
    SQLite 파일 기반 영구 저장소
    """
    __tablename__ = 'abandoned_vehicles'

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Unique Vehicle ID
    vehicle_id = Column(String(100), unique=True, nullable=False, index=True)

    # 위치 정보 (Location)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    city = Column(String(50), index=True)  # 시/도 (e.g., "서울특별시")
    district = Column(String(50), index=True)  # 구/군 (e.g., "강남구")
    address = Column(String(200))  # 전체 주소

    # 차량 정보 (Vehicle Info)
    vehicle_type = Column(String(50))  # car, truck, bus

    # 탐지 정보 (Detection Info)
    similarity_score = Column(Float)  # 유사도 점수 (0.0-1.0)
    similarity_percentage = Column(Float)  # 유사도 퍼센트 (0-100)
    risk_level = Column(String(20), index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    years_difference = Column(Integer)  # 경과 년수

    # 이력 정보 (History)
    first_detected = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_detected = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    detection_count = Column(Integer, default=1)  # 총 감지 횟수

    # 유사도 통계
    avg_similarity = Column(Float)  # 평균 유사도
    max_similarity = Column(Float)  # 최고 유사도

    # 관리 상태 (Management Status)
    status = Column(String(20), default='DETECTED', index=True)
    # 상태: DETECTED (감지됨), INVESTIGATING (조사중), VERIFIED (확인됨), RESOLVED (처리완료)

    verification_notes = Column(Text)  # 관리자 메모/검증 노트

    # 메타데이터 (Metadata)
    bbox_data = Column(JSON)  # Bounding box 정보 {"x": 350, "y": 220, "w": 85, "h": 60}
    extra_metadata = Column(JSON)  # 추가 메타데이터 (metadata는 SQLAlchemy 예약어)

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now())

    # 복합 인덱스 (Composite Indexes for Performance)
    __table_args__ = (
        # 지역별 조회 성능 최적화
        Index('idx_location', 'latitude', 'longitude'),
        Index('idx_city_district', 'city', 'district'),

        # 상태별 필터링 최적화
        Index('idx_status_risk', 'status', 'risk_level'),

        # 시간 기반 조회 최적화
        Index('idx_first_detected', 'first_detected'),
        Index('idx_last_detected', 'last_detected'),

        # 관리 대시보드 성능 최적화
        Index('idx_status_city', 'status', 'city'),
    )

    def to_dict(self) -> Dict:
        """
        JSON 직렬화용 딕셔너리 변환
        FastAPI response_model용
        """
        # 방치 기간 계산 (일 단위)
        if self.first_detected:
            days_abandoned = (datetime.utcnow() - self.first_detected).days
        else:
            days_abandoned = 0

        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,

            # Location
            'latitude': self.latitude,
            'longitude': self.longitude,
            'city': self.city,
            'district': self.district,
            'address': self.address,

            # Vehicle Info
            'vehicle_type': self.vehicle_type,

            # Detection
            'similarity_score': self.similarity_score,
            'similarity_percentage': self.similarity_percentage,
            'risk_level': self.risk_level,
            'years_difference': self.years_difference,

            # History
            'first_detected': self.first_detected.isoformat() if self.first_detected else None,
            'last_detected': self.last_detected.isoformat() if self.last_detected else None,
            'detection_count': self.detection_count,
            'days_abandoned': days_abandoned,

            # Similarity Stats
            'avg_similarity': self.avg_similarity,
            'max_similarity': self.max_similarity,

            # Management
            'status': self.status,
            'verification_notes': self.verification_notes,

            # Metadata
            'bbox_data': self.bbox_data,
            'metadata': self.extra_metadata,  # Return as 'metadata' for API compatibility

            # Timestamps
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_detection(self, similarity_score: float, risk_level: str) -> None:
        """
        재감지 시 이력 업데이트

        Args:
            similarity_score: 새로운 유사도 점수 (0.0-1.0)
            risk_level: 위험도 (CRITICAL, HIGH, MEDIUM, LOW)
        """
        self.last_detected = datetime.utcnow()
        self.detection_count += 1
        self.risk_level = risk_level

        # 평균 유사도 계산
        if self.avg_similarity:
            self.avg_similarity = (
                self.avg_similarity * (self.detection_count - 1) + similarity_score
            ) / self.detection_count
        else:
            self.avg_similarity = similarity_score

        # 최고 유사도 업데이트
        if not self.max_similarity or similarity_score > self.max_similarity:
            self.max_similarity = similarity_score

        self.updated_at = datetime.utcnow()

    def mark_as_verified(self, notes: Optional[str] = None) -> None:
        """관리자가 확인 완료 처리"""
        self.status = 'VERIFIED'
        if notes:
            if self.verification_notes:
                self.verification_notes += f"\n[{datetime.utcnow().isoformat()}] {notes}"
            else:
                self.verification_notes = f"[{datetime.utcnow().isoformat()}] {notes}"
        self.updated_at = datetime.utcnow()

    def mark_as_resolved(self, notes: Optional[str] = None) -> None:
        """처리 완료 (견인/제거)"""
        self.status = 'RESOLVED'
        if notes:
            if self.verification_notes:
                self.verification_notes += f"\n[{datetime.utcnow().isoformat()}] {notes}"
            else:
                self.verification_notes = f"[{datetime.utcnow().isoformat()}] {notes}"
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"<AbandonedVehicle("
            f"id={self.id}, "
            f"vehicle_id='{self.vehicle_id}', "
            f"location=({self.latitude}, {self.longitude}), "
            f"risk_level='{self.risk_level}', "
            f"status='{self.status}'"
            f")>"
        )


class AnalysisLog(Base):
    """
    자동 분석 실행 이력 로그
    12시간마다 실행되는 전국 250개 시/군/구 분석 기록
    """
    __tablename__ = 'analysis_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Analysis Info
    analysis_type = Column(String(50))  # 'auto_scheduled', 'manual', 'region_specific'
    region_count = Column(Integer)  # 분석한 지역 수

    # Results
    vehicles_detected = Column(Integer, default=0)  # 새로 감지된 차량 수
    vehicles_updated = Column(Integer, default=0)  # 기존 차량 업데이트 수

    # Performance Metrics
    execution_time_seconds = Column(Float)  # 실행 시간 (초)
    images_processed = Column(Integer)  # 처리한 이미지 수

    # Status
    status = Column(String(20))  # 'completed', 'failed', 'partial'
    error_message = Column(Text)  # 에러 발생 시 메시지

    # Metadata
    regions_analyzed = Column(JSON)  # 분석한 지역 목록
    config = Column(JSON)  # 분석 설정 (threshold, zoom level 등)

    # Timestamp
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    __table_args__ = (
        Index('idx_started_at', 'started_at'),
        Index('idx_status', 'status'),
    )

    def to_dict(self) -> Dict:
        """JSON 직렬화"""
        return {
            'id': self.id,
            'analysis_type': self.analysis_type,
            'region_count': self.region_count,
            'vehicles_detected': self.vehicles_detected,
            'vehicles_updated': self.vehicles_updated,
            'execution_time_seconds': self.execution_time_seconds,
            'images_processed': self.images_processed,
            'status': self.status,
            'error_message': self.error_message,
            'regions_analyzed': self.regions_analyzed,
            'config': self.config,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<AnalysisLog("
            f"id={self.id}, "
            f"type='{self.analysis_type}', "
            f"detected={self.vehicles_detected}, "
            f"status='{self.status}'"
            f")>"
        )
