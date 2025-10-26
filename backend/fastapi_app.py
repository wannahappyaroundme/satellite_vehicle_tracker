"""
FastAPI Backend for Abandoned Vehicle Detection System
Analyzes aerial photos from 국토정보플랫폼 to detect long-term abandoned vehicles
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import cv2
import numpy as np
from datetime import datetime
import os
import tempfile
import json
import logging

from abandoned_vehicle_detector import AbandonedVehicleDetector
from pdf_processor import PDFProcessor
from ngii_api_service import NGIIAPIService
from demo_mode import get_demo_coordinates, get_demo_analysis_result
from aerial_image_cache import get_cache
from logging_config import setup_logging, PerformanceLogger, SecurityLogger, log_performance
from security import rate_limiter, InputValidator, DataProtection, SQLSafetyChecker
from auto_scheduler import get_scheduler
from database import SessionLocal, get_db
from models_sqlalchemy import AbandonedVehicle, AnalysisLog
from analytics_service import get_analytics_service
from vworld_search_service import get_vworld_search_service
from local_gov_cctv_service import LocalGovCCTVService

# Initialize FastAPI app
app = FastAPI(
    title="Abandoned Vehicle Detection API",
    description="Detects long-term abandoned vehicles using aerial photo comparison",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler (Korean error messages + contact info)
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    전역 에러 핸들러 (모든 예외 처리)
    한국어 에러 메시지 + 연락처 정보 포함
    """
    error_message = str(exc)

    # 한국어 에러 메시지
    korean_messages = {
        "ConnectionError": "네트워크 연결에 실패했습니다.",
        "TimeoutError": "요청 시간이 초과되었습니다.",
        "FileNotFoundError": "파일을 찾을 수 없습니다.",
        "ValueError": "잘못된 값이 입력되었습니다.",
        "KeyError": "필수 데이터가 누락되었습니다.",
    }

    # 에러 타입에 따라 한국어 메시지 선택
    error_type = type(exc).__name__
    korean_message = korean_messages.get(error_type, "시스템 오류가 발생했습니다.")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "type": error_type,
                "message_en": error_message,
                "message_ko": korean_message,
                "contact": {
                    "email": "bu5119@hanyang.ac.kr",
                    "phone": "010-5616-5119",
                    "description": "문제가 지속되면 위 연락처로 문의해 주세요."
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    )

# Initialize logging
setup_logging(
    log_level='INFO',
    log_file='logs/fastapi.log',
    json_format=True
)

# Initialize loggers
logger = logging.getLogger(__name__)
perf_logger = PerformanceLogger()
security_logger = SecurityLogger()

# Initialize services
detector = AbandonedVehicleDetector(similarity_threshold=0.90)
pdf_processor = PDFProcessor(dpi=300)
ngii_service = NGIIAPIService()
cctv_service = LocalGovCCTVService()  # 지자체 CCTV 통합 서비스

# Input validator
validator = InputValidator()

# Store uploaded files temporarily
UPLOAD_DIR = tempfile.mkdtemp()

# Create logs directory
os.makedirs('logs', exist_ok=True)


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    전역 Rate Limiting 미들웨어
    """
    client_ip = request.client.host if request.client else "unknown"

    # Rate limit 확인 (일반 엔드포인트: 분당 100회)
    if rate_limiter.is_rate_limited(client_ip, max_requests=100, window_seconds=60):
        security_logger.log_rate_limit(client_ip, str(request.url), 100)

        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": {
                    "type": "RateLimitExceeded",
                    "message_en": "Too many requests. Please try again later.",
                    "message_ko": "요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
                    "retry_after_seconds": 300
                }
            }
        )

    response = await call_next(request)
    return response


# Request logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    요청 로깅 미들웨어
    """
    import time

    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"

    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        # API 요청 로깅
        perf_logger.log_request(
            endpoint=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            duration_ms=duration_ms,
            user_id=client_ip
        )

        return response

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000

        # 에러 로깅
        perf_logger.log_request(
            endpoint=str(request.url.path),
            method=request.method,
            status_code=500,
            duration_ms=duration_ms,
            user_id=client_ip
        )

        raise


# Pydantic models
class ComparisonRequest(BaseModel):
    """Request model for comparing two images"""
    year1: int = Field(..., description="First year (e.g., 2015)")
    year2: int = Field(..., description="Second year (e.g., 2020)")
    similarity_threshold: Optional[float] = Field(0.90, ge=0.0, le=1.0)


class AbandonedVehicleResult(BaseModel):
    """Result model for abandoned vehicle detection"""
    parking_space_id: str
    year1: int
    year2: int
    years_difference: int
    similarity_score: float
    similarity_percentage: float
    threshold: float
    is_abandoned: bool
    risk_level: str
    status: str


class CCTVLocation(BaseModel):
    """CCTV location for verification"""
    id: str
    name: str
    latitude: float
    longitude: float
    stream_url: str
    is_public: bool


# Sample CCTV data (제주시 일도이동 지역)
SAMPLE_CCTV_DATA = [
    {
        "id": "cctv_001",
        "name": "제주시 일도이동 주차장 1번",
        "latitude": 33.5102,
        "longitude": 126.5219,
        "stream_url": "https://example.com/stream/cctv_001",
        "is_public": True
    },
    {
        "id": "cctv_002",
        "name": "제주시 일도이동 주차장 2번",
        "latitude": 33.5105,
        "longitude": 126.5222,
        "stream_url": "https://example.com/stream/cctv_002",
        "is_public": True
    }
]


@app.on_event("startup")
async def startup_event():
    """앱 시작 시 스케줄러 시작"""
    scheduler = get_scheduler()
    scheduler.start()
    logger.info("=" * 60)
    logger.info("✅ FastAPI 앱 시작 - 자동 스케줄러 활성화됨")
    logger.info("⏰ 12시간 간격 실행: 매일 0시, 12시")
    logger.info("📍 분석 대상: 전국 250개 시/군/구")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 스케줄러 중지"""
    scheduler = get_scheduler()
    scheduler.stop()
    logger.info("⏹️  FastAPI 앱 종료 - 자동 스케줄러 중지됨")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Abandoned Vehicle Detection API",
        "version": "1.0.0",
        "status": "running",
        "description": "국토정보플랫폼 항공사진 기반 장기 방치 차량 탐지 시스템"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "abandoned_vehicle_detector": "ready",
            "pdf_processor": "ready"
        }
    }


@app.post("/api/compare-samples")
async def compare_sample_images():
    """
    Compare sample_image1.pdf (2015) vs sample_image2.pdf (2020)
    This is a demo endpoint using the provided sample data
    """
    try:
        # Paths to sample images
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pdf1_path = os.path.join(base_dir, "sample_image1.pdf")
        pdf2_path = os.path.join(base_dir, "sample_image2.pdf")

        # Check if files exist
        if not os.path.exists(pdf1_path) or not os.path.exists(pdf2_path):
            raise HTTPException(
                status_code=404,
                detail="Sample images not found. Please ensure sample_image1.pdf and sample_image2.pdf exist in the project root."
            )

        # Convert PDFs to images
        image1 = pdf_processor.pdf_to_image(pdf1_path)
        image2 = pdf_processor.pdf_to_image(pdf2_path)

        # Extract metadata
        meta1 = pdf_processor.extract_metadata_from_pdf(pdf1_path)
        meta2 = pdf_processor.extract_metadata_from_pdf(pdf2_path)

        # Align images for better comparison
        image1_aligned, image2_aligned = pdf_processor.align_images(image1, image2)

        # Detect parking spaces automatically
        parking_boxes = pdf_processor.detect_parking_spaces(image1_aligned)

        # Compare vehicles
        results = detector.compare_pdf_images(
            image1_aligned,
            image2_aligned,
            meta1['year'],
            meta2['year'],
            parking_boxes[:10]  # Limit to first 10 detected spaces for demo
        )

        # Filter to only abandoned vehicles
        abandoned_vehicles = detector.filter_abandoned_vehicles(results)

        # Create visualization
        abandoned_boxes = [
            (r['bbox']['x'], r['bbox']['y'], r['bbox']['w'], r['bbox']['h'])
            for r in abandoned_vehicles if 'bbox' in r
        ]

        visualization = pdf_processor.create_comparison_visualization(
            image1_aligned,
            image2_aligned,
            meta1['year'],
            meta2['year'],
            abandoned_boxes
        )

        # Save visualization
        viz_path = os.path.join(UPLOAD_DIR, "comparison_result.jpg")
        pdf_processor.save_image(visualization, viz_path)

        # Prepare status message
        if len(abandoned_vehicles) == 0:
            status_message = "✅ 방치 차량이 발견되지 않았습니다. 해당 지역은 정상적으로 관리되고 있는 것으로 보입니다."
            status_en = "No abandoned vehicles detected. The area appears to be normally managed."
        else:
            status_message = f"⚠️ {len(abandoned_vehicles)}대의 방치 의심 차량이 발견되었습니다."
            status_en = f"{len(abandoned_vehicles)} suspected abandoned vehicle(s) detected."

        return {
            "success": True,
            "status_message": status_message,
            "status_message_en": status_en,
            "metadata": {
                "image1": meta1,
                "image2": meta2,
                "years_difference": meta2['year'] - meta1['year']
            },
            "analysis": {
                "total_parking_spaces_detected": len(parking_boxes),
                "spaces_analyzed": len(results),
                "abandoned_vehicles_found": len(abandoned_vehicles),
                "detection_threshold": detector.similarity_threshold,
                "is_clean": len(abandoned_vehicles) == 0
            },
            "results": results,
            "abandoned_vehicles": abandoned_vehicles,
            "visualization_path": viz_path,
            "cctv_locations": SAMPLE_CCTV_DATA
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing images: {str(e)}")


@app.post("/api/upload-aerial-photos")
async def upload_aerial_photos(
    photo_year1: UploadFile = File(...),
    photo_year2: UploadFile = File(...),
    year1: int = Query(..., description="First year"),
    year2: int = Query(..., description="Second year"),
    similarity_threshold: float = Query(0.90, ge=0.0, le=1.0)
):
    """
    Upload two aerial photos (PDFs) for comparison
    """
    try:
        # Save uploaded files
        pdf1_path = os.path.join(UPLOAD_DIR, f"uploaded_{year1}.pdf")
        pdf2_path = os.path.join(UPLOAD_DIR, f"uploaded_{year2}.pdf")

        with open(pdf1_path, "wb") as f:
            f.write(await photo_year1.read())

        with open(pdf2_path, "wb") as f:
            f.write(await photo_year2.read())

        # Process PDFs
        image1 = pdf_processor.pdf_to_image(pdf1_path)
        image2 = pdf_processor.pdf_to_image(pdf2_path)

        # Align images
        image1_aligned, image2_aligned = pdf_processor.align_images(image1, image2)

        # Update detector threshold
        detector.similarity_threshold = similarity_threshold

        # Detect parking spaces
        parking_boxes = pdf_processor.detect_parking_spaces(image1_aligned)

        # Compare vehicles
        results = detector.compare_pdf_images(
            image1_aligned,
            image2_aligned,
            year1,
            year2,
            parking_boxes
        )

        # Filter abandoned vehicles
        abandoned_vehicles = detector.filter_abandoned_vehicles(results)

        return {
            "success": True,
            "analysis": {
                "total_parking_spaces": len(parking_boxes),
                "spaces_analyzed": len(results),
                "abandoned_vehicles": len(abandoned_vehicles),
                "threshold": similarity_threshold
            },
            "results": results,
            "abandoned_vehicles": abandoned_vehicles
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing uploads: {str(e)}")


@app.get("/api/abandoned-vehicles")
async def get_abandoned_vehicles(
    min_similarity: float = Query(0.85, ge=0.0, le=1.0, description="최소 유사도 (0-1)"),
    risk_level: Optional[str] = Query(None, pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$", description="위험도 필터"),
    city: Optional[str] = Query(None, description="시/도 필터"),
    district: Optional[str] = Query(None, description="시/군/구 필터"),
    status: Optional[str] = Query(None, description="상태 필터 (DETECTED/INVESTIGATING/VERIFIED/RESOLVED)"),
    limit: int = Query(100, ge=1, le=1000, description="최대 결과 수")
):
    """
    저장된 방치 차량 조회 (SQLite DB)

    Query parameters:
    - min_similarity: 최소 유사도 (기본값: 0.85)
    - risk_level: 위험도 필터 (LOW/MEDIUM/HIGH/CRITICAL)
    - city: 시/도 필터 (예: "서울특별시")
    - district: 시/군/구 필터 (예: "강남구")
    - status: 상태 필터 (DETECTED/INVESTIGATING/VERIFIED/RESOLVED)
    - limit: 최대 결과 수 (기본값: 100)
    """
    db = SessionLocal()
    try:
        # Build query with filters
        query = db.query(AbandonedVehicle)

        # Similarity filter
        query = query.filter(AbandonedVehicle.similarity_score >= min_similarity)

        # Risk level filter
        if risk_level:
            query = query.filter(AbandonedVehicle.risk_level == risk_level)

        # City filter
        if city:
            query = query.filter(AbandonedVehicle.city == city)

        # District filter
        if district:
            query = query.filter(AbandonedVehicle.district == district)

        # Status filter
        if status:
            query = query.filter(AbandonedVehicle.status == status.upper())

        # Order by risk level and latest detection
        query = query.order_by(
            AbandonedVehicle.risk_level.desc(),
            AbandonedVehicle.last_detected.desc()
        )

        # Limit results
        query = query.limit(limit)

        # Execute query
        vehicles = query.all()

        # Convert to dict
        results = [v.to_dict() for v in vehicles]

        return {
            "success": True,
            "count": len(results),
            "filters": {
                "min_similarity": min_similarity,
                "risk_level": risk_level,
                "city": city,
                "district": district,
                "status": status
            },
            "abandoned_vehicles": results,
            "message": "SQLite DB에서 조회 (영구 저장소)",
            "storage_type": "sqlite"
        }

    except Exception as e:
        logger.error(f"DB query failed: {e}")
        raise HTTPException(status_code=500, detail=f"조회 실패: {str(e)}")
    finally:
        db.close()


@app.get("/api/cctv-locations")
async def get_cctv_locations(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: Optional[float] = 1.0
):
    """
    Get nearby CCTV locations for verification

    Query parameters:
    - latitude: Center latitude
    - longitude: Center longitude
    - radius_km: Search radius in kilometers
    """
    return {
        "cctv_locations": SAMPLE_CCTV_DATA,
        "count": len(SAMPLE_CCTV_DATA),
        "search_params": {
            "latitude": latitude,
            "longitude": longitude,
            "radius_km": radius_km
        }
    }


@app.get("/api/cctv/{cctv_id}/stream")
async def get_cctv_stream(cctv_id: str):
    """
    Get CCTV stream URL for verification
    In production, this would return actual CCTV feed
    """
    cctv = next((c for c in SAMPLE_CCTV_DATA if c['id'] == cctv_id), None)

    if not cctv:
        raise HTTPException(status_code=404, detail=f"CCTV {cctv_id} not found")

    return {
        "cctv_id": cctv_id,
        "stream_url": cctv['stream_url'],
        "name": cctv['name'],
        "is_public": cctv['is_public'],
        "message": "In production, this would return live CCTV stream"
    }


@app.get("/api/visualization/{filename}")
async def get_visualization(filename: str):
    """
    Get saved visualization image
    """
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Visualization not found")

    return FileResponse(file_path, media_type="image/jpeg")


@app.get("/api/statistics")
async def get_statistics():
    """
    Get system statistics
    """
    cache = get_cache()
    cache_stats = cache.get_stats()

    return {
        "system": {
            "model": "ResNet50",
            "similarity_threshold": detector.similarity_threshold,
            "device": str(detector.device)
        },
        "statistics": {
            "total_analyses": 0,  # Would come from database
            "abandoned_vehicles_detected": 0,
            "areas_monitored": 1
        },
        "cache": cache_stats
    }


@app.get("/api/cache/stats")
async def get_cache_stats():
    """
    캐시 통계 조회

    Returns:
        캐시 히트율, 저장된 이미지 수, 디스크 사용량 등
    """
    cache = get_cache()
    return cache.get_stats()


@app.post("/api/cache/cleanup")
async def cleanup_cache():
    """
    만료된 캐시 정리 (24시간 이상 지난 항목)

    Returns:
        삭제된 캐시 개수
    """
    cache = get_cache()
    deleted_count = cache.cleanup_expired()

    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": f"{deleted_count}개의 만료된 캐시를 삭제했습니다"
    }


@app.delete("/api/cache/clear")
async def clear_all_cache():
    """
    모든 캐시 삭제 (주의: 복구 불가능)

    Returns:
        삭제된 캐시 개수
    """
    cache = get_cache()
    deleted_count = cache.clear_all()

    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": f"모든 캐시({deleted_count}개)를 삭제했습니다"
    }


# ===== REAL-TIME LOCATION & AERIAL IMAGE ENDPOINTS =====

@app.get("/api/search-address")
async def search_address(
    query: str = Query(None, description="전체 주소 문자열"),
    sido: str = Query(None, description="시/도"),
    sigungu: str = Query(None, description="시/군/구"),
    dong: str = Query(None, description="동/읍/면"),
    jibun: str = Query(None, description="지번")
):
    """
    주소 검색 → 좌표 변환

    VWorld API를 사용하여 주소를 좌표로 변환
    API 키가 유효하지 않으면 데모 모드로 동작
    """
    # Demo mode로 대체
    from demo_mode import get_demo_coordinates

    # API 키가 없거나 유효하지 않으면 데모 모드 사용
    if not ngii_service.api_key or ngii_service.api_key == '여기에_발급받은_API_키를_입력하세요':
        return get_demo_coordinates(sido, sigungu)

    # API 키가 있으면 실제 API 호출 시도
    result = ngii_service.search_address(
        sido=sido,
        sigungu=sigungu,
        dong=dong,
        jibun=jibun,
        query=query
    )

    # API 호출 실패 시 데모 모드로 fallback
    if not result.get('success'):
        return get_demo_coordinates(sido, sigungu)

    return result


@app.post("/api/analyze-location")
async def analyze_location(
    latitude: float = Query(..., description="위도"),
    longitude: float = Query(..., description="경도"),
    address: str = Query("위치 분석", description="주소"),
    use_real_api: bool = Query(False, description="실제 VWorld API 사용 (API 키 필요)")
):
    """
    실시간 위치 분석: 항공사진 다운로드 + 방치차량 탐지

    Parameters:
    - latitude: 분석할 위치의 위도
    - longitude: 분석할 위치의 경도
    - address: 주소 (표시용)
    - use_real_api: True면 VWorld API, False면 데모 모드

    ⭐ VWorld API 결과는 자동으로 DB에 저장됩니다!
    """
    try:
        # Demo mode (API 키 없이 작동)
        if not use_real_api or not ngii_service.api_key:
            from demo_mode import get_demo_analysis_result
            return get_demo_analysis_result(latitude, longitude, address)

        # Real API mode (VWorld에서 실제 항공사진 다운로드)
        # SQLite DB 사용

        # 현재 항공사진 다운로드 (zoom 18 = 고해상도)
        current_result = ngii_service.download_high_resolution_area(
            latitude=latitude,
            longitude=longitude,
            width_tiles=3,
            height_tiles=3,
            zoom=18,
            output_path=None  # numpy array로 반환
        )

        if not current_result.get('success'):
            # API 실패 시 데모 모드로 fallback
            from demo_mode import get_demo_analysis_result
            return get_demo_analysis_result(latitude, longitude, address)

        current_image = current_result['image_array']

        # 과거 이미지는 사용자가 업로드해야 함 (VWorld는 최신 이미지만 제공)
        # 여기서는 현재 이미지를 분석만 수행 (차량 탐지)
        # 실제 방치 차량 탐지는 두 개 이미지 비교가 필요하므로
        # 현재는 차량 탐지만 수행

        # 간단한 차량 탐지 (YOLO 사용)
        from vehicle_detector import VehicleDetector
        vehicle_det = VehicleDetector()
        detections = vehicle_det.detect_vehicles(current_image)

        # ⭐ 감지된 차량을 SQLite DB에 저장 (고정된 방치 차량으로!)
        # 유사도가 90% 이상인 차량만 방치 차량으로 간주
        db = SessionLocal()
        saved_vehicles = []
        try:
            # Extract city/district from address
            parts = address.split()
            city = parts[0] if len(parts) >= 1 else None
            district = parts[1] if len(parts) >= 2 else None

            for detection in detections:
                # 방치 차량으로 간주되는 조건 (예: confidence >= 0.9)
                if detection.get('confidence', 0) >= 0.9:
                    # Generate unique vehicle ID
                    import hashlib
                    bbox = detection.get('bbox', [])
                    id_string = f'{latitude}{longitude}{bbox}'
                    vehicle_id = f"vehicle_{hashlib.md5(id_string.encode()).hexdigest()[:16]}"

                    # Check if vehicle already exists
                    existing = db.query(AbandonedVehicle).filter(
                        AbandonedVehicle.vehicle_id == vehicle_id
                    ).first()

                    if not existing:
                        # Create new vehicle
                        confidence = detection.get('confidence', 0.9)
                        vehicle = AbandonedVehicle(
                            vehicle_id=vehicle_id,
                            latitude=latitude,
                            longitude=longitude,
                            city=city,
                            district=district,
                            address=address,
                            vehicle_type=detection.get('vehicle_type', 'car'),
                            similarity_score=confidence,
                            similarity_percentage=confidence * 100,
                            risk_level="HIGH" if confidence >= 0.95 else "MEDIUM",
                            years_difference=1,  # 실제로는 이미지 비교에서 얻어야 함
                            bbox_data=detection.get('bbox', {})
                        )
                        db.add(vehicle)
                        db.commit()
                        db.refresh(vehicle)
                        saved_vehicles.append(vehicle.to_dict())
        finally:
            db.close()

        return {
            "success": True,
            "mode": "real_api",
            "status_message": f"✅ 실제 항공사진 분석 완료 ({len(detections)}대 차량 탐지, {len(saved_vehicles)}대 DB 저장)",
            "metadata": {
                "address": address,
                "latitude": latitude,
                "longitude": longitude,
                "image_size": current_result['image_size'],
                "tiles_downloaded": current_result['tiles_downloaded'],
                "mode": "real_api"
            },
            "analysis": {
                "vehicles_detected": len(detections),
                "vehicles_saved_to_db": len(saved_vehicles),
                "image_resolution": "high (zoom 18)",
                "note": "방치 차량 분석을 위해서는 과거 항공사진이 필요합니다"
            },
            "vehicles": detections,
            "saved_vehicles": saved_vehicles
        }

    except Exception as e:
        # 에러 발생 시 데모 모드로 fallback
        from demo_mode import get_demo_analysis_result
        return get_demo_analysis_result(latitude, longitude, address)


# ===== ADMIN ENDPOINTS (방치 차량 관리) =====

@app.get("/api/admin/vehicles/all")
async def admin_get_all_vehicles(
    status: Optional[str] = Query(None, description="상태 필터: DETECTED, INVESTIGATING, VERIFIED, RESOLVED"),
    risk_level: Optional[str] = Query(None, description="위험도 필터: CRITICAL, HIGH, MEDIUM, LOW")
):
    """
    전국 모든 방치 차량 조회 (관리자용)

    Query Parameters:
    - status: 상태 필터
    - risk_level: 위험도 필터
    """
    db = SessionLocal()
    try:
        query = db.query(AbandonedVehicle)

        if status:
            query = query.filter(AbandonedVehicle.status == status.upper())

        if risk_level:
            query = query.filter(AbandonedVehicle.risk_level == risk_level.upper())

        vehicles = query.all()
        vehicles_dict = [v.to_dict() for v in vehicles]

        return {
            "success": True,
            "total": len(vehicles_dict),
            "filters": {
                "status": status,
                "risk_level": risk_level
            },
            "vehicles": vehicles_dict
        }
    finally:
        db.close()


@app.get("/api/admin/vehicles/statistics")
async def admin_get_statistics():
    """
    전국 방치 차량 통계 (관리자용)

    Returns:
        전체 차량 수, 상태별/위험도별/차량타입별 통계
    """
    db = SessionLocal()
    try:
        # 총 차량 수
        total_vehicles = db.query(AbandonedVehicle).count()

        # 상태별 통계
        by_status = {}
        for status in ['DETECTED', 'INVESTIGATING', 'VERIFIED', 'RESOLVED']:
            count = db.query(AbandonedVehicle).filter(
                AbandonedVehicle.status == status
            ).count()
            by_status[status] = count

        # 위험도별 통계
        by_risk_level = {}
        for risk in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = db.query(AbandonedVehicle).filter(
                AbandonedVehicle.risk_level == risk
            ).count()
            by_risk_level[risk] = count

        # 차량 타입별 통계
        from sqlalchemy import func
        vehicle_types = db.query(
            AbandonedVehicle.vehicle_type,
            func.count(AbandonedVehicle.id)
        ).group_by(AbandonedVehicle.vehicle_type).all()

        by_vehicle_type = {vtype: count for vtype, count in vehicle_types if vtype}

        # 시/도별 통계
        cities = db.query(
            AbandonedVehicle.city,
            func.count(AbandonedVehicle.id)
        ).group_by(AbandonedVehicle.city).all()

        by_city = {city: count for city, count in cities if city}

        return {
            "success": True,
            "statistics": {
                "total_vehicles": total_vehicles,
                "by_status": by_status,
                "by_risk_level": by_risk_level,
                "by_vehicle_type": by_vehicle_type,
                "by_city": by_city
            }
        }
    finally:
        db.close()


@app.put("/api/admin/vehicles/{vehicle_id}/status")
async def admin_update_vehicle_status(
    vehicle_id: str,
    status: str = Query(..., pattern="^(DETECTED|INVESTIGATING|VERIFIED|RESOLVED)$"),
    notes: Optional[str] = Query(None, description="메모")
):
    """
    방치 차량 상태 업데이트 (관리자용)

    Parameters:
    - vehicle_id: 차량 ID
    - status: 새 상태 (DETECTED, INVESTIGATING, VERIFIED, RESOLVED)
    - notes: 메모 (선택)
    """
    db = SessionLocal()
    try:
        vehicle = db.query(AbandonedVehicle).filter(
            AbandonedVehicle.vehicle_id == vehicle_id
        ).first()

        if not vehicle:
            raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")

        # Update status using model method
        if status.upper() == 'VERIFIED':
            vehicle.mark_as_verified(notes)
        elif status.upper() == 'RESOLVED':
            vehicle.mark_as_resolved(notes)
        else:
            vehicle.status = status.upper()
            if notes:
                if vehicle.verification_notes:
                    vehicle.verification_notes += f"\n[{datetime.now().isoformat()}] {notes}"
                else:
                    vehicle.verification_notes = f"[{datetime.now().isoformat()}] {notes}"

        db.commit()
        db.refresh(vehicle)

        return {
            "success": True,
            "message": f"차량 {vehicle_id} 상태가 {status}로 업데이트되었습니다",
            "vehicle": vehicle.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"업데이트 실패: {str(e)}")
    finally:
        db.close()


@app.delete("/api/admin/vehicles/{vehicle_id}")
async def admin_delete_vehicle(vehicle_id: str):
    """
    방치 차량 삭제 (관리자용 - 처리 완료 시)

    Parameters:
    - vehicle_id: 차량 ID
    """
    db = SessionLocal()
    try:
        vehicle = db.query(AbandonedVehicle).filter(
            AbandonedVehicle.vehicle_id == vehicle_id
        ).first()

        if not vehicle:
            raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")

        db.delete(vehicle)
        db.commit()

        return {
            "success": True,
            "message": f"차량 {vehicle_id}가 삭제되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"삭제 실패: {str(e)}")
    finally:
        db.close()


# ===== UTILITY ENDPOINTS =====

@app.post("/api/admin/trigger-analysis")
async def trigger_analysis():
    """
    수동으로 방치 차량 분석 실행 (관리자/테스트용)

    자동 스케줄러를 기다리지 않고 즉시 250개 지역 분석을 실행합니다.
    """
    scheduler = get_scheduler()
    scheduler.run_now()

    return {
        "success": True,
        "message": "전국 250개 시/군/구 방치 차량 분석이 백그라운드에서 시작되었습니다",
        "note": "분석 완료까지 수 분이 소요될 수 있습니다. /api/abandoned-vehicles로 결과를 확인하세요.",
        "schedule": "매일 0시, 12시 자동 실행"
    }


@app.get("/api/reverse-geocode")
async def reverse_geocode(
    lat: float = Query(..., description="위도"),
    lon: float = Query(..., description="경도")
):
    """
    역지오코딩 프록시 (CORS 문제 해결)

    Nominatim API를 백엔드에서 호출하여 CORS 문제 방지
    """
    import httpx

    try:
        # Nominatim API 호출 (비동기)
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                'https://nominatim.openstreetmap.org/reverse',
                params={
                    'lat': lat,
                    'lon': lon,
                    'format': 'json',
                    'accept-language': 'ko',
                    'addressdetails': 1
                },
                headers={
                    'User-Agent': 'AbandonedVehicleDetection/1.0'
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "address": data.get('display_name', f"위도: {lat}, 경도: {lon}"),
                    "data": data
                }
            else:
                return {
                    "success": False,
                    "address": f"위도: {lat}, 경도: {lon}",
                    "error": f"Status code: {response.status_code}"
                }

    except Exception as e:
        # 에러 시 좌표 반환
        return {
            "success": False,
            "address": f"위도: {lat:.6f}, 경도: {lon:.6f}",
            "error": str(e)
        }


# ===== DEMO MODE ENDPOINTS (No API Key Required) =====

@app.get("/api/demo/address/search")
async def demo_address_search(
    sido: str = Query(None, description="시/도"),
    sigungu: str = Query(None, description="시/군/구"),
    dong: str = Query(None, description="동/읍/면"),
    jibun: str = Query(None, description="지번")
):
    """
    🎭 데모 모드: 주소 검색 (API 키 불필요)
    Mock 데이터로 좌표 반환
    """
    result = get_demo_coordinates(sido, sigungu)
    return result


@app.post("/api/demo/analyze-location")
async def demo_analyze_location(
    latitude: float = Query(..., description="위도"),
    longitude: float = Query(..., description="경도"),
    address: str = Query("알 수 없는 위치", description="주소")
):
    """
    🎭 데모 모드: 방치 차량 분석 (API 키 불필요)
    Mock 데이터로 방치 차량 생성

    보안:
    - 좌표 유효성 검증
    - 주소 새니타이징 (XSS 방지)
    - SQL Injection 패턴 감지
    """
    # 입력 검증
    if not validator.validate_coordinates(latitude, longitude):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid coordinates",
                "error_ko": "유효하지 않은 좌표입니다.",
                "latitude_range": "(-90, 90)",
                "longitude_range": "(-180, 180)"
            }
        )

    # 주소 새니타이징
    address = validator.sanitize_string(address, max_length=200)

    # SQL Injection 패턴 감지
    if SQLSafetyChecker.is_sql_injection(address):
        security_logger.log_suspicious_activity(
            ip_address="unknown",
            activity="sql_injection_attempt",
            details={"address": address}
        )
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid input detected",
                "error_ko": "유효하지 않은 입력이 감지되었습니다."
            }
        )

    # 주소 형식 검증
    if not validator.validate_korean_address(address):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid address format",
                "error_ko": "주소 형식이 올바르지 않습니다."
            }
        )

    result = get_demo_analysis_result(latitude, longitude, address)
    return result


# ===== ADMIN DASHBOARD ENDPOINTS =====

@app.get("/api/admin/statistics")
async def get_admin_statistics(db: Session = Depends(get_db)):
    """
    관리자 대시보드 통계 정보

    Returns:
        - 총 방치 차량 수
        - 위험도별 분포
        - 지역별 분포
        - 최근 분석 이력
    """
    try:
        # 총 방치 차량 수
        total_vehicles = db.query(AbandonedVehicle).count()

        # 위험도별 분포
        risk_distribution = {
            "CRITICAL": db.query(AbandonedVehicle).filter(AbandonedVehicle.risk_level == "CRITICAL").count(),
            "HIGH": db.query(AbandonedVehicle).filter(AbandonedVehicle.risk_level == "HIGH").count(),
            "MEDIUM": db.query(AbandonedVehicle).filter(AbandonedVehicle.risk_level == "MEDIUM").count(),
            "LOW": db.query(AbandonedVehicle).filter(AbandonedVehicle.risk_level == "LOW").count()
        }

        # 지역별 상위 10개
        from sqlalchemy import func
        city_distribution = db.query(
            AbandonedVehicle.city,
            func.count(AbandonedVehicle.id).label('count')
        ).group_by(AbandonedVehicle.city).order_by(func.count(AbandonedVehicle.id).desc()).limit(10).all()

        # 최근 분석 이력
        recent_analyses = db.query(AnalysisLog).order_by(AnalysisLog.started_at.desc()).limit(10).all()

        return {
            "success": True,
            "statistics": {
                "total_vehicles": total_vehicles,
                "risk_distribution": risk_distribution,
                "city_distribution": [{"city": city, "count": count} for city, count in city_distribution],
                "recent_analyses": [
                    {
                        "id": log.id,
                        "analysis_type": log.analysis_type,
                        "status": log.status,
                        "started_at": log.started_at.isoformat() if log.started_at else None,
                        "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                        "regions_analyzed": log.region_count,
                        "vehicles_found": log.vehicles_detected,
                        "vehicles_updated": log.vehicles_updated
                    }
                    for log in recent_analyses
                ]
            }
        }
    except Exception as e:
        logger.error(f"통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")


@app.get("/api/admin/scheduler-status")
async def get_scheduler_status():
    """
    스케줄러 상태 조회

    Returns:
        - 스케줄러 실행 여부
        - 다음 실행 예정 시간
        - 현재 실행 중인 작업
    """
    try:
        scheduler = get_scheduler()

        return {
            "success": True,
            "scheduler": {
                "is_running": scheduler.is_running,
                "next_run_time": "매일 0시, 12시",
                "schedule": "0 0,12 * * *"
            }
        }
    except Exception as e:
        logger.error(f"스케줄러 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"스케줄러 상태 조회 실패: {str(e)}")


@app.post("/api/admin/update-vehicle-status")
async def update_vehicle_status(
    vehicle_id: int,
    status: str = Query(..., description="처리 상태: pending, verified, resolved, false_positive"),
    db: Session = Depends(get_db)
):
    """
    방치 차량 상태 업데이트 (관리자용)

    Args:
        vehicle_id: 차량 ID
        status: 처리 상태

    Returns:
        업데이트된 차량 정보
    """
    try:
        vehicle = db.query(AbandonedVehicle).filter(AbandonedVehicle.id == vehicle_id).first()

        if not vehicle:
            raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")

        # 상태 업데이트
        vehicle.status = status
        vehicle.updated_at = datetime.now()

        db.commit()
        db.refresh(vehicle)

        return {
            "success": True,
            "message": f"차량 상태가 '{status}'로 업데이트되었습니다",
            "vehicle": vehicle.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"차량 상태 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail=f"차량 상태 업데이트 실패: {str(e)}")


@app.delete("/api/admin/delete-vehicle/{vehicle_id}")
async def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """
    방치 차량 삭제 (관리자용)

    Args:
        vehicle_id: 차량 ID

    Returns:
        삭제 결과
    """
    try:
        vehicle = db.query(AbandonedVehicle).filter(AbandonedVehicle.id == vehicle_id).first()

        if not vehicle:
            raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")

        db.delete(vehicle)
        db.commit()

        return {
            "success": True,
            "message": f"차량 ID {vehicle_id}가 삭제되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"차량 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=f"차량 삭제 실패: {str(e)}")


# ===== DATA ANALYTICS ENDPOINTS =====

@app.get("/api/analytics/clustering")
async def analyze_clustering(
    eps_km: float = Query(0.5, description="클러스터 반경 (km)"),
    min_samples: int = Query(3, description="최소 차량 수"),
    db: Session = Depends(get_db)
):
    """
    DBSCAN 클러스터링 분석

    Args:
        eps_km: 클러스터 반경 (km)
        min_samples: 클러스터 최소 차량 수

    Returns:
        클러스터별 차량 밀집 지역 및 통계
    """
    try:
        # DB에서 모든 방치 차량 조회
        vehicles_db = db.query(AbandonedVehicle).all()
        vehicles = [v.to_dict() for v in vehicles_db]

        # 클러스터링 수행
        analytics = get_analytics_service()
        result = analytics.perform_clustering(
            vehicles=vehicles,
            eps_km=eps_km,
            min_samples=min_samples
        )

        return result
    except Exception as e:
        logger.error(f"클러스터링 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=f"클러스터링 분석 실패: {str(e)}")


@app.get("/api/analytics/heatmap")
async def generate_heatmap(
    grid_size: float = Query(0.01, description="그리드 크기 (degrees, 약 1km)"),
    db: Session = Depends(get_db)
):
    """
    히트맵 데이터 생성 (위험도 가중 밀도)

    Args:
        grid_size: 그리드 크기 (degrees)

    Returns:
        그리드별 차량 밀도 및 위험도
    """
    try:
        # DB에서 모든 방치 차량 조회
        vehicles_db = db.query(AbandonedVehicle).all()
        vehicles = [v.to_dict() for v in vehicles_db]

        # 히트맵 생성
        analytics = get_analytics_service()
        result = analytics.generate_heatmap_data(
            vehicles=vehicles,
            grid_size=grid_size
        )

        return result
    except Exception as e:
        logger.error(f"히트맵 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"히트맵 생성 실패: {str(e)}")


@app.get("/api/analytics/by-city")
async def analyze_by_city(db: Session = Depends(get_db)):
    """
    시/도별 통계 분석

    Returns:
        시/도별 차량 수, 위험도 분포, 평균 유사도
    """
    try:
        # DB에서 모든 방치 차량 조회
        vehicles_db = db.query(AbandonedVehicle).all()
        vehicles = [v.to_dict() for v in vehicles_db]

        # 시/도별 분석
        analytics = get_analytics_service()
        result = analytics.analyze_by_city(vehicles=vehicles)

        return result
    except Exception as e:
        logger.error(f"시/도별 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=f"시/도별 분석 실패: {str(e)}")


@app.get("/api/analytics/trends")
async def analyze_trends(
    days: int = Query(30, description="분석 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    시간대별 트렌드 분석

    Args:
        days: 분석 기간 (일)

    Returns:
        일별 차량 추가 추이 및 위험도 분포
    """
    try:
        # DB에서 모든 방치 차량 조회
        vehicles_db = db.query(AbandonedVehicle).all()
        vehicles = [v.to_dict() for v in vehicles_db]

        # 트렌드 분석
        analytics = get_analytics_service()
        result = analytics.analyze_trends(vehicles=vehicles, days=days)

        return result
    except Exception as e:
        logger.error(f"트렌드 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=f"트렌드 분석 실패: {str(e)}")


# ===== VWORLD ADDITIONAL API ENDPOINTS =====

@app.get("/api/vworld/search-poi")
async def search_poi(
    query: str = Query(..., description="검색어 (예: 주차장, CCTV)"),
    lat: Optional[float] = Query(None, description="중심 위도"),
    lon: Optional[float] = Query(None, description="중심 경도"),
    radius: int = Query(1000, description="검색 반경 (미터)"),
    count: int = Query(10, description="결과 개수")
):
    """
    VWorld POI (Point of Interest) 검색

    Args:
        query: 검색어
        lat: 중심 위도
        lon: 중심 경도
        radius: 검색 반경 (미터)
        count: 결과 개수

    Returns:
        POI 검색 결과
    """
    try:
        search_service = get_vworld_search_service()
        result = search_service.search_poi(
            query=query,
            lat=lat,
            lon=lon,
            radius=radius,
            count=count
        )
        return result
    except Exception as e:
        logger.error(f"POI 검색 실패: {e}")
        raise HTTPException(status_code=500, detail=f"POI 검색 실패: {str(e)}")


@app.get("/api/vworld/parking-lots")
async def search_parking_lots(
    lat: float = Query(..., description="중심 위도"),
    lon: float = Query(..., description="중심 경도"),
    radius: int = Query(2000, description="검색 반경 (미터)")
):
    """
    주차장 검색

    Args:
        lat: 중심 위도
        lon: 중심 경도
        radius: 검색 반경 (미터)

    Returns:
        주변 주차장 목록
    """
    try:
        search_service = get_vworld_search_service()
        result = search_service.search_parking_lots(lat=lat, lon=lon, radius=radius)
        return result
    except Exception as e:
        logger.error(f"주차장 검색 실패: {e}")
        raise HTTPException(status_code=500, detail=f"주차장 검색 실패: {str(e)}")


@app.get("/api/vworld/cctv")
async def search_cctv(
    lat: float = Query(..., description="중심 위도"),
    lon: float = Query(..., description="중심 경도"),
    radius: int = Query(1000, description="검색 반경 (미터)"),
    cctv_type: Optional[str] = Query(None, description="CCTV 타입 필터 (traffic/security/parking)")
):
    """
    지자체 CCTV 검색 (실제 공공데이터 기반)

    Args:
        lat: 중심 위도
        lon: 중심 경도
        radius: 검색 반경 (미터)
        cctv_type: CCTV 타입 필터 (optional)

    Returns:
        주변 CCTV 목록 (거리순 정렬)
    """
    try:
        # 지자체 CCTV 통합 서비스 사용
        result = cctv_service.search_nearby_cctv(
            lat=lat,
            lon=lon,
            radius=radius,
            cctv_type=cctv_type
        )

        # 지역 정보 추가
        region = cctv_service.get_region_info(lat, lon)
        result['region'] = region

        logger.info(f"CCTV 검색 성공: {result['total_count']}개 발견 ({region})")
        return result
    except Exception as e:
        logger.error(f"CCTV 검색 실패: {e}")
        raise HTTPException(status_code=500, detail=f"CCTV 검색 실패: {str(e)}")


@app.get("/api/cctv/{cctv_id}")
async def get_cctv_info(cctv_id: str):
    """
    특정 CCTV 상세 정보 조회

    Args:
        cctv_id: CCTV ID

    Returns:
        CCTV 상세 정보
    """
    try:
        cctv_info = cctv_service.get_cctv_info(cctv_id)

        if not cctv_info:
            raise HTTPException(status_code=404, detail=f"CCTV {cctv_id}를 찾을 수 없습니다")

        return {
            'success': True,
            'cctv': cctv_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CCTV 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"CCTV 정보 조회 실패: {str(e)}")


@app.get("/api/cctv/{cctv_id}/stream")
async def get_cctv_stream(cctv_id: str):
    """
    CCTV 스트림 URL 조회

    Args:
        cctv_id: CCTV ID

    Returns:
        스트림 URL 및 CCTV 정보
    """
    try:
        cctv_info = cctv_service.get_cctv_info(cctv_id)

        if not cctv_info:
            raise HTTPException(status_code=404, detail=f"CCTV {cctv_id}를 찾을 수 없습니다")

        stream_url = cctv_service.get_cctv_stream_url(cctv_id)

        return {
            'success': True,
            'cctv_id': cctv_id,
            'stream_url': stream_url,
            'cctv_name': cctv_info['name'],
            'region': cctv_info['region'],
            'is_public': cctv_info['is_public'],
            'message': '실제 운영 시 지자체 통합관제 시스템 연동 필요'
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CCTV 스트림 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"CCTV 스트림 조회 실패: {str(e)}")


@app.get("/api/vworld/map-tile-url")
async def get_map_tile_url(
    map_type: str = Query("base", description="지도 타입: base, hybrid"),
    z: int = Query(..., description="줌 레벨"),
    x: int = Query(..., description="타일 X 좌표"),
    y: int = Query(..., description="타일 Y 좌표")
):
    """
    VWorld 2D 지도 타일 URL 반환

    Args:
        map_type: 지도 타입 (base, hybrid)
        z: 줌 레벨
        x: 타일 X 좌표
        y: 타일 Y 좌표

    Returns:
        타일 URL
    """
    try:
        search_service = get_vworld_search_service()

        if map_type == 'hybrid':
            url = search_service.get_hybrid_map_tile_url(z, x, y)
        else:
            url = search_service.get_2d_map_tile_url(z, x, y)

        return {
            'success': True,
            'tile_url': url,
            'map_type': map_type
        }
    except Exception as e:
        logger.error(f"타일 URL 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"타일 URL 생성 실패: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
