"""
FastAPI Backend for Abandoned Vehicle Detection System
Analyzes aerial photos from 국토정보플랫폼 to detect long-term abandoned vehicles
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
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

from abandoned_vehicle_detector import AbandonedVehicleDetector
from pdf_processor import PDFProcessor
from ngii_api_service import NGIIAPIService
from demo_mode import get_demo_coordinates, get_demo_analysis_result

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

# Initialize services
detector = AbandonedVehicleDetector(similarity_threshold=0.90)
pdf_processor = PDFProcessor(dpi=300)
ngii_service = NGIIAPIService()

# Store uploaded files temporarily
UPLOAD_DIR = tempfile.mkdtemp()


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
    min_similarity: float = Query(0.90, ge=0.0, le=1.0),
    min_years: int = Query(1, ge=1),
    risk_level: Optional[str] = Query(None, pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
):
    """
    Get filtered list of abandoned vehicles

    Query parameters:
    - min_similarity: Minimum similarity score (0-1)
    - min_years: Minimum years difference
    - risk_level: Filter by risk level
    """
    # This would typically query a database
    # For now, return sample data structure
    return {
        "filters": {
            "min_similarity": min_similarity,
            "min_years": min_years,
            "risk_level": risk_level
        },
        "message": "Run /api/compare-samples first to generate detection results"
    }


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
        }
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
    """
    try:
        # Demo mode (API 키 없이 작동)
        if not use_real_api or not ngii_service.api_key:
            from demo_mode import get_demo_analysis_result
            return get_demo_analysis_result(latitude, longitude, address)

        # Real API mode (VWorld에서 실제 항공사진 다운로드)
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

        return {
            "success": True,
            "mode": "real_api",
            "status_message": f"✅ 실제 항공사진 분석 완료 ({len(detections)}대 차량 탐지)",
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
                "image_resolution": "high (zoom 18)",
                "note": "방치 차량 분석을 위해서는 과거 항공사진이 필요합니다"
            },
            "vehicles": detections
        }

    except Exception as e:
        # 에러 발생 시 데모 모드로 fallback
        from demo_mode import get_demo_analysis_result
        return get_demo_analysis_result(latitude, longitude, address)


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
    """
    result = get_demo_analysis_result(latitude, longitude, address)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
