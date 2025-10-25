"""
FastAPI Backend for Abandoned Vehicle Detection System
Analyzes aerial photos from 국토정보플랫폼 to detect long-term abandoned vehicles
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
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
# from auto_scheduler import get_scheduler  # TODO: Enable after DB models setup
from abandoned_vehicle_storage import get_storage  # Use in-memory storage for now

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


# TODO: Enable scheduler after DB setup
# @app.on_event("startup")
# async def startup_event():
#     """앱 시작 시 스케줄러 시작"""
#     scheduler = get_scheduler()
#     scheduler.start()
#     logger.info("✅ FastAPI 앱 시작 - 자동 스케줄러 활성화됨")
#
#
# @app.on_event("shutdown")
# async def shutdown_event():
#     """앱 종료 시 스케줄러 중지"""
#     scheduler = get_scheduler()
#     scheduler.stop()
#     logger.info("⏹️  FastAPI 앱 종료 - 자동 스케줄러 중지됨")


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
    status: Optional[str] = Query(None, description="상태 필터 (detected/verified/removed)"),
    limit: int = Query(100, ge=1, le=1000, description="최대 결과 수")
):
    """
    저장된 방치 차량 조회

    Query parameters:
    - min_similarity: 최소 유사도 (기본값: 0.85)
    - risk_level: 위험도 필터 (LOW/MEDIUM/HIGH/CRITICAL)
    - city: 시/도 필터 (예: "서울특별시")
    - district: 시/군/구 필터 (예: "강남구")
    - status: 상태 필터 (detected/verified/removed)
    - limit: 최대 결과 수 (기본값: 100)
    """
    try:
        # Get storage instance
        storage = get_storage()

        # Get all vehicles from storage
        all_vehicles = storage.get_all_vehicles()

        # Apply filters
        results = []
        for v in all_vehicles:
            # Similarity filter
            if v.get('similarity_percentage', 0) / 100 < min_similarity:
                continue

            # Risk level filter
            if risk_level and v.get('risk_level') != risk_level:
                continue

            # City filter
            if city and city not in v.get('address', ''):
                continue

            # District filter
            if district and district not in v.get('address', ''):
                continue

            # Status filter
            if status and v.get('status') != status:
                continue

            results.append(v)

        # Limit results
        results = results[:limit]

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
            "message": "영구 방치 차량 DB에서 조회 (실시간 업데이트)"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"조회 실패: {str(e)}")


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
        from abandoned_vehicle_storage import get_storage
        storage = get_storage()

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

        # ⭐ 감지된 차량을 DB에 저장 (고정된 방치 차량으로!)
        # 유사도가 90% 이상인 차량만 방치 차량으로 간주
        saved_vehicles = []
        for detection in detections:
            # 방치 차량으로 간주되는 조건 (예: confidence >= 0.9)
            if detection.get('confidence', 0) >= 0.9:
                vehicle_data = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "address": address,
                    "vehicle_type": detection.get('vehicle_type', 'car'),
                    "similarity_score": detection.get('confidence', 0.9),
                    "risk_level": "HIGH" if detection.get('confidence', 0) >= 0.95 else "MEDIUM",
                    "years_difference": 1,  # 실제로는 이미지 비교에서 얻어야 함
                    "bbox": detection.get('bbox', {})
                }

                # DB에 저장
                saved_vehicle = storage.add_vehicle(vehicle_data)
                saved_vehicles.append(saved_vehicle)

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
    status: Optional[str] = Query(None, description="상태 필터: DETECTED, INVESTIGATING, RESOLVED"),
    risk_level: Optional[str] = Query(None, description="위험도 필터: CRITICAL, HIGH, MEDIUM, LOW")
):
    """
    전국 모든 방치 차량 조회 (관리자용)

    Query Parameters:
    - status: 상태 필터
    - risk_level: 위험도 필터
    """
    from abandoned_vehicle_storage import get_storage
    storage = get_storage()

    vehicles = storage.get_all_vehicles(
        status_filter=status,
        risk_level_filter=risk_level
    )

    return {
        "success": True,
        "total": len(vehicles),
        "filters": {
            "status": status,
            "risk_level": risk_level
        },
        "vehicles": vehicles
    }


@app.get("/api/admin/vehicles/statistics")
async def admin_get_statistics():
    """
    전국 방치 차량 통계 (관리자용)

    Returns:
        전체 차량 수, 상태별/위험도별/차량타입별 통계
    """
    from abandoned_vehicle_storage import get_storage
    storage = get_storage()

    stats = storage.get_statistics()

    return {
        "success": True,
        "statistics": stats
    }


@app.put("/api/admin/vehicles/{vehicle_id}/status")
async def admin_update_vehicle_status(
    vehicle_id: str,
    status: str = Query(..., pattern="^(DETECTED|INVESTIGATING|RESOLVED)$"),
    notes: Optional[str] = Query(None, description="메모")
):
    """
    방치 차량 상태 업데이트 (관리자용)

    Parameters:
    - vehicle_id: 차량 ID
    - status: 새 상태 (DETECTED, INVESTIGATING, RESOLVED)
    - notes: 메모 (선택)
    """
    from abandoned_vehicle_storage import get_storage
    storage = get_storage()

    updated_vehicle = storage.update_vehicle_status(vehicle_id, status, notes)

    if not updated_vehicle:
        raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")

    return {
        "success": True,
        "message": f"차량 {vehicle_id} 상태가 {status}로 업데이트되었습니다",
        "vehicle": updated_vehicle
    }


@app.delete("/api/admin/vehicles/{vehicle_id}")
async def admin_delete_vehicle(vehicle_id: str):
    """
    방치 차량 삭제 (관리자용 - 처리 완료 시)

    Parameters:
    - vehicle_id: 차량 ID
    """
    from abandoned_vehicle_storage import get_storage
    storage = get_storage()

    deleted = storage.delete_vehicle(vehicle_id)

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")

    return {
        "success": True,
        "message": f"차량 {vehicle_id}가 삭제되었습니다"
    }


# ===== UTILITY ENDPOINTS =====

# TODO: Enable after DB/scheduler setup
# @app.post("/api/admin/trigger-analysis")
# async def trigger_analysis():
#     """
#     수동으로 방치 차량 분석 실행 (관리자/테스트용)
#
#     자동 스케줄러를 기다리지 않고 즉시 분석을 실행합니다.
#     """
#     scheduler = get_scheduler()
#     scheduler.run_now()
#
#     return {
#         "success": True,
#         "message": "방치 차량 분석이 백그라운드에서 시작되었습니다",
#         "note": "분석 완료까지 수 분이 소요될 수 있습니다. /api/abandoned-vehicles로 결과를 확인하세요."
#     }


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
