# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**장기 방치 차량 탐지 시스템 (Abandoned Vehicle Detection System)**

This is a full-stack application that detects long-term abandoned vehicles by comparing aerial photos from different years using AI-powered computer vision. The system uses ResNet feature extraction and cosine similarity to identify vehicles that haven't moved over 1+ year periods.

**Primary Use Case:** Analyze aerial photos from 국토정보플랫폼 (National Geographic Information Platform) to detect vehicles abandoned in the same location for 1+ years, with CCTV verification capability.

**Tech Stack:**
- Backend: Python FastAPI (new) + Flask (legacy) with ResNet/YOLO for AI detection
- Frontend: React + TypeScript with Leaflet for mapping
- Database: SQLite (SQLAlchemy ORM)
- AI Models:
  - ResNet50 for feature extraction (abandoned vehicle detection)
  - YOLOv8 for object detection (legacy vehicle tracking)
  - Custom classifiers for vehicle type analysis

## Essential Commands

### Development Setup
```bash
# Install all dependencies (backend + frontend)
npm run install:all

# Install backend dependencies (including new FastAPI + pdf2image)
cd backend && pip install -r requirements.txt

# Run both frontend and backend concurrently (recommended for development)
npm run dev
# This starts:
# - Frontend on http://localhost:3000
# - Flask backend on http://localhost:5000
# Note: FastAPI server (port 8000) needs to be started separately if needed

# OR start servers individually:

# Start FastAPI server (NEW - for abandoned vehicle detection)
cd backend && python fastapi_app.py
# Runs on http://localhost:8000

# Start Flask server (LEGACY - for general vehicle tracking)
cd backend && python app.py
# Runs on http://localhost:5000

# Start frontend (runs on port 3000)
cd frontend && npm start
```

### Testing Abandoned Vehicle Detection
```bash
# Test with sample PDFs (2015 vs 2020 comparison)
python test_abandoned_detection.py

# This requires poppler for PDF conversion:
# macOS: brew install poppler
# Ubuntu: sudo apt-get install poppler-utils
```

### API Testing
```bash
# Test FastAPI abandoned vehicle detection endpoint
curl -X POST http://localhost:8000/api/compare-samples

# Get CCTV locations for verification
curl http://localhost:8000/api/cctv-locations

# View API docs (automatic with FastAPI)
open http://localhost:8000/docs
```

### Testing & Linting
```bash
# Frontend TypeScript type checking
cd frontend && npm run lint

# Backend Python linting
cd backend && python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Frontend tests
cd frontend && npm test
```

### Build & Deployment
```bash
# Build frontend for production
npm run build

# Deploy frontend to GitHub Pages
cd frontend && npm run deploy

# Full stack Docker deployment
./deploy.sh
```

## Architecture Overview

### NEW: Abandoned Vehicle Detection System

**Core Algorithm Flow:**
1. **PDF Input:** Receive aerial photos from 국토정보플랫폼 (GeoTIFF format or PDF)
2. **Image Processing:** Convert PDF to image, align images from different years
3. **Parking Space Detection:** Auto-detect parking spaces or use GeoJSON coordinates
4. **Feature Extraction:** Use ResNet50 to extract 2048-dimensional feature vectors from each parking space
5. **Similarity Comparison:** Calculate cosine similarity between year1 and year2 features
6. **Abandoned Detection:** If similarity >= 90% → vehicle likely abandoned (hasn't moved)
7. **Risk Assessment:** Calculate risk level (CRITICAL/HIGH/MEDIUM/LOW) based on similarity + years
8. **CCTV Verification:** Display nearby public CCTV for manual verification

**Key Files:**
- `backend/abandoned_vehicle_detector.py` - Core ResNet-based detection engine
- `backend/pdf_processor.py` - PDF/image processing utilities
- `backend/fastapi_app.py` - FastAPI REST API server
- `frontend/src/components/AbandonedVehiclePanel.tsx` - React UI for detection results
- `test_abandoned_detection.py` - Test script using sample_image1.pdf and sample_image2.pdf

**Sample Data:**
- `sample_image1.pdf` - 2015년 4월 17일, 제주시 일도이동 923 항공사진
- `sample_image2.pdf` - 2020년 4월 29일, same location (5 years later)

### Backend Architecture

The system now has TWO backend servers:

#### FastAPI Server (NEW - Port 8000)
**Purpose:** Abandoned vehicle detection with year-over-year comparison

**Core Services:**
- `abandoned_vehicle_detector.py` - ResNet50 feature extraction + cosine similarity
  - Uses pretrained ResNet50 with final layer removed
  - Extracts 2048-dim feature vectors
  - Default threshold: 0.90 (90% similarity = abandoned)
  - Risk levels: CRITICAL (95%+ similarity, 3+ years), HIGH (90%+, 2+ years), MEDIUM (85%+), LOW

- `pdf_processor.py` - PDF/GeoTIFF processing
  - Converts PDF aerial photos to numpy arrays
  - Aligns images from different years using ORB feature matching
  - Auto-detects parking spaces using contour detection
  - Creates comparison visualizations with red boxes for abandoned vehicles

**FastAPI Endpoints:**
- `POST /api/compare-samples` - Compare sample_image1.pdf vs sample_image2.pdf
- `POST /api/upload-aerial-photos` - Upload two PDFs for custom comparison
- `GET /api/abandoned-vehicles` - Query abandoned vehicles with filters
- `GET /api/cctv-locations` - Get nearby CCTV for verification
- `GET /api/cctv/{id}/stream` - Get CCTV stream URL
- `GET /api/visualization/{filename}` - Download comparison visualization

#### Flask Server (LEGACY - Port 5000)
**Purpose:** General vehicle tracking and real-time detection

**Core Services:**
- `vehicle_detector.py` - YOLO-based vehicle detection from satellite imagery
- `vehicle_classifier.py` - Advanced classification (SUV, sedan, truck, color, brand)
- `long_term_detector.py` - Detects vehicles that haven't moved for extended periods
- `storage_analyzer.py` - Analyzes areas for vehicle storage potential using clustering
- `south_korea_satellite.py` - Integration with KOMPSAT, Sentinel-2, Landsat data sources
- `ngii_api_service.py` - Integration with 국토정보플랫폼 (National Geographic Information Platform) API
- `demo_mode.py` - Demo mode with mock data when API keys are not available

**Flask Endpoints:**
- Vehicle detection: `/api/upload-image`, `/api/search-vehicles`, `/api/aircraft-search`
- Storage analysis: `/api/storage-analysis`
- Long-term detection: `/api/long-term-stopped`, `/api/vehicle-history/<id>`, `/api/area-summary`
- South Korea data: `/api/south-korea/coverage`, `/api/south-korea/imagery`, `/api/south-korea/cities`

**Database Models (`models.py`):**
- `Vehicle` - Base vehicle entity with unique vehicle_id
- `VehicleLocation` - Timestamped location records with coordinates, confidence, vehicle_type
- `StorageAnalysis` - Storage potential analysis results with recommendations

### Frontend Architecture (React + TypeScript)

**Component Structure:**
The UI is tab-based with specialized panels for different functions:

**NEW Component:**
- `AbandonedVehiclePanel.tsx` - 장기 방치 차량 탐지 interface
  - Triggers `/api/compare-samples` endpoint
  - Displays abandoned vehicles in red-bordered cards
  - Shows risk level badges (CRITICAL/HIGH/MEDIUM/LOW)
  - CCTV verification popup with stream placeholder
  - Side-by-side year comparison visualization

**Legacy Components:**
- `UploadPanel.tsx` - Satellite image upload and vehicle detection trigger
- `SearchPanel.tsx` - Geographic search with filters (type, time range, confidence)
- `StorageAnalysis.tsx` - Storage potential analysis visualization
- `LongTermDetector.tsx` - Long-term stopped vehicle detection interface
- `VehicleList.tsx` - List view of detected vehicles
- `VehicleHoverCard.tsx` - Airbnb-style popup cards showing vehicle details

**State Management:**
Uses React hooks (useState, useEffect) with no external state management library. State is primarily managed in `App.tsx` and passed to child components.

**API Communication:**
- FastAPI calls: Direct axios to `http://localhost:8000/api/` (abandoned vehicle detection)
- Flask calls: Through `src/services/api.ts` using axios to `http://localhost:5000/api/` (legacy features)

**Map Integration:**
Uses Leaflet (not Google Maps) for interactive mapping. Vehicle markers rendered using react-leaflet.

**TypeScript Types:**
Core interfaces defined in `src/types.ts`:
- `VehicleData` - Vehicle detection with coordinates and metadata
- `StorageAnalysisData` - Storage analysis results
- `VehicleCluster` - Grouped vehicles with metrics

### Abandoned Vehicle Detection Data Flow

1. **Sample Analysis Flow:**
   - User clicks "샘플 이미지 분석 시작" in `AbandonedVehiclePanel`
   - Frontend calls `POST /api/compare-samples`
   - Backend loads `sample_image1.pdf` (2015) and `sample_image2.pdf` (2020)
   - PDFs converted to images using `pdf2image`
   - Images aligned using ORB feature matching
   - Parking spaces auto-detected using contour analysis
   - For each parking space:
     - Extract ResNet50 features from 2015 image
     - Extract ResNet50 features from 2020 image
     - Calculate cosine similarity
     - If similarity >= 90% → mark as abandoned
   - Return results with risk levels and CCTV locations
   - Frontend displays results with red borders, risk badges

2. **Custom Upload Flow:**
   - User uploads two PDF aerial photos via `POST /api/upload-aerial-photos`
   - Same processing pipeline as sample analysis
   - User can specify custom years and similarity threshold

3. **CCTV Verification Flow:**
   - User clicks "CCTV로 검증하기" on abandoned vehicle card
   - Frontend finds nearest CCTV from `cctv_locations` array
   - Opens popup with CCTV info and stream URL placeholder
   - In production, would display live CCTV feed for manual verification

## Development Guidelines

### Adding Abandoned Vehicle Detection Features

When enhancing detection capabilities:
1. Update ResNet model or similarity algorithm in `abandoned_vehicle_detector.py`
2. Modify preprocessing in `pdf_processor.py` if needed
3. Add new FastAPI endpoints in `fastapi_app.py`
4. Update UI in `AbandonedVehiclePanel.tsx`
5. Test with sample PDFs using `test_abandoned_detection.py`

### Working with GeoTIFF Files

For production use with actual GeoTIFF files:
1. Use `crop_parking_space()` method with GeoJSON parking space coordinates
2. Process in batch using `batch_detect_abandoned_vehicles()`
3. GeoTIFF processing requires rasterio and GDAL

### Adjusting Detection Sensitivity

**Similarity Threshold:**
- Default: 0.90 (90% similarity = abandoned)
- Higher threshold (e.g., 0.95) = fewer false positives, may miss some abandoned vehicles
- Lower threshold (e.g., 0.85) = more detections, more false positives
- Configurable per request via `similarity_threshold` parameter

**Risk Level Calculation:**
```python
CRITICAL: similarity >= 95% AND years >= 3
HIGH:     similarity >= 90% AND years >= 2
MEDIUM:   similarity >= 85%
LOW:      similarity < 85%
```

### Database Schema Changes

1. Modify model definitions in `backend/models.py`
2. Create migration (manual - no Alembic configured)
3. Update `to_dict()` methods for API serialization
4. Update TypeScript interfaces to match new fields

### Working with AI Models

**ResNet50 (Abandoned Vehicle Detection):**
- Pretrained on ImageNet, used for feature extraction only
- Input: 224x224 RGB images (automatically resized)
- Output: 2048-dimensional feature vector
- Model loaded once at FastAPI startup
- GPU acceleration if available (checks for CUDA)

**YOLOv8 (Legacy Vehicle Detection):**
- Default: `yolov8n.pt` (nano - fastest, included in repo)
- Can swap to yolov8s/m/l for better accuracy
- Configure via `YOLO_MODEL_PATH` environment variable

**Model Files:**
- YOLO weights: `backend/yolov8n.pt` (6.5MB)
- ResNet50: Downloaded automatically by torchvision

### Environment Configuration

Key environment variables (`.env` file):

**FastAPI (Abandoned Vehicle Detection):**
- `FASTAPI_PORT` - FastAPI server port (default: 8000)
- `PDF_DPI` - PDF conversion resolution (default: 300)
- `ABANDONED_SIMILARITY_THRESHOLD` - Detection threshold (default: 0.90)

**Flask (Legacy):**
- `SECRET_KEY` - Flask session secret
- `DATABASE_URL` - Database connection (default: SQLite)
- `YOLO_MODEL_PATH` - Path to YOLO weights
- `CONFIDENCE_THRESHOLD` - Minimum detection confidence (default: 0.5)

**Frontend:**
- `REACT_APP_API_URL` - Backend URL (switches between FastAPI/Flask as needed)

**NGII API (국토정보플랫폼):**
- `NGII_API_KEY` - API key for National Geographic Information Platform
- `NGII_SERVICE_URL` - NGII service endpoint URL
- Demo mode automatically activates if API key is not configured

### CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/`) runs on push/PR:
1. Installs Python 3.11 and Node.js 18
2. Installs GDAL system dependencies
3. Installs backend dependencies (now includes FastAPI, pdf2image, PyMuPDF)
4. Installs frontend dependencies
5. Runs Python linting (flake8)
6. Runs TypeScript linting

**Important:**
- GDAL must be installed at system level before Python dependencies
- Poppler required for pdf2image (not in requirements.txt, system dependency)

### Docker Deployment

Full stack deployment via Docker Compose:
- FastAPI service: Port 8000
- Flask service: Port 5000
- Frontend service: Nginx on port 80
- Database: SQLite volume mounted to persist data

## Common Gotchas

1. **Poppler Dependency:** `pdf2image` requires poppler system library. Install before running abandoned vehicle detection:
   - macOS: `brew install poppler`
   - Ubuntu: `apt-get install poppler-utils`

2. **Two Backend Servers:** System now runs TWO servers simultaneously:
   - FastAPI on port 8000 (abandoned vehicle detection)
   - Flask on port 5000 (legacy vehicle tracking)
   - Frontend must route requests to correct backend

3. **PDF Format:** Sample PDFs are from 국토정보플랫폼 with specific metadata format. Custom PDFs need year extraction logic update.

4. **GDAL Installation:** Required for GeoTIFF processing. On Mac use `brew install gdal`, on Ubuntu use `apt-get install gdal-bin libgdal-dev`.

5. **ResNet GPU Memory:** ResNet50 feature extraction can use significant GPU memory. Batch processing limited to avoid OOM errors.

6. **Image Alignment:** ORB feature matching may fail if images too different. Falls back to original images if alignment fails.

7. **Coordinate System:** Uses WGS84 (standard lat/lng). GeoTIFF cropping requires proper coordinate transformation.

8. **CCTV Integration:** Currently returns placeholder URLs. Production requires integration with actual CCTV management systems.

9. **NGII API Access:** The system can integrate with 국토정보플랫폼 (NGII) for real aerial imagery. Set `NGII_API_KEY` in `.env` to enable. Without the key, demo mode with mock data is used automatically. Test the API connection with `python backend/test_ngii_api.py`.

## Testing with Sample Data

### Quick Test (Recommended)
```bash
# Run standalone test script
python test_abandoned_detection.py

# Expected output:
# - Loads sample_image1.pdf (2015) and sample_image2.pdf (2020)
# - Converts PDFs to images
# - Detects parking spaces
# - Compares features using ResNet
# - Generates comparison_result.jpg visualization
# - Saves detection_results.json
```

### API Test
```bash
# Start FastAPI server
cd backend && python fastapi_app.py

# In another terminal, test API
curl -X POST http://localhost:8000/api/compare-samples | jq

# Expected: JSON with abandoned vehicle detections
```

### Frontend Test
```bash
# Start FastAPI backend
cd backend && python fastapi_app.py

# Start frontend
cd frontend && npm start

# Navigate to http://localhost:3000
# Click "방치 차량 탐지 (New!)" tab
# Click "샘플 이미지 분석 시작"
# View results with red-bordered abandoned vehicle cards
```

## Production Deployment Notes

**For Real 국토정보플랫폼 Data:**
1. Update `pdf_processor.py` metadata extraction for actual PDF formats
2. Implement GeoJSON parking space database or detection
3. Integrate with real CCTV stream APIs
4. Add authentication/authorization for CCTV access
5. Scale ResNet inference with GPU/batch processing
6. Consider model optimization (ONNX, TensorRT) for production
7. Implement database for storing detection history
8. Add alerting/notification system for new abandonments

**GeoTIFF Processing:**
Use `batch_detect_abandoned_vehicles()` method with GeoJSON parking spaces:
```python
detector = AbandonedVehicleDetector()
results = detector.batch_detect_abandoned_vehicles(
    parking_spaces=geojson_features,  # List of GeoJSON parking space polygons
    geotiff_year1='path/to/2015.tif',
    geotiff_year2='path/to/2020.tif',
    year1=2015,
    year2=2020
)
```

## Korean Vehicle Detection Training Project

**Location:** `korean_vehicle_detection/`

This is a separate YOLOv8x model training project for detecting Korean vehicles in DOTA satellite imagery.

**Dataset:**
- 340 images with 47,445 annotations
- Train: 237 images (23,976 annotations)
- Val: 68 images
- Test: 35 images
- Classes: small-vehicle, large-vehicle

**Model:** YOLOv8x (68.2M parameters, 258.1 GFLOPs)
**Hardware:** Optimized for Apple Silicon M3 Max (MPS acceleration)

### Training Commands

```bash
# Start training (runs in background, ~100 hours for 100 epochs)
cd korean_vehicle_detection
python scripts/train_yolov8x.py

# Check training progress
python check_training.py

# Monitor with TensorBoard
tensorboard --logdir runs/train/yolov8x_korean_vehicles
# Open http://localhost:6006

# View results CSV
cat runs/train/yolov8x_korean_vehicles/results.csv
```

### Using Trained Model

```python
from ultralytics import YOLO

# Load best model
model = YOLO('korean_vehicle_detection/runs/train/yolov8x_korean_vehicles/weights/best.pt')

# Run inference on test images
results = model.predict(
    source='korean_vehicle_detection/data/test/images',
    save=True,
    conf=0.25,
    device='mps'  # or 'cpu' or 'cuda'
)

# Evaluate performance
metrics = model.val(data='korean_vehicle_detection/data.yaml', device='mps')
print(f'mAP50: {metrics.box.map50:.4f}')
print(f'mAP50-95: {metrics.box.map:.4f}')
```

### Resume Training After Interruption

```python
from ultralytics import YOLO

model = YOLO('korean_vehicle_detection/runs/train/yolov8x_korean_vehicles/weights/last.pt')
model.train(resume=True)
```

### Training Configuration

**Current Settings** (in `scripts/train_yolov8x.py`):
- Device: MPS (Apple Silicon GPU)
- Batch size: 8
- Image size: 1024px
- Optimizer: AdamW (lr=0.001)
- Epochs: 100
- Early stopping: patience=50
- Augmentation: mosaic, mixup, rotation, scaling, flipping

**Adjust if memory issues:**
```python
batch=4,      # reduce from 8
imgsz=640,    # reduce from 1024
```

### Key Files

- `data.yaml` - Dataset configuration for YOLOv8
- `scripts/train_yolov8x.py` - Training script
- `scripts/convert_coco_to_yolo.py` - COCO to YOLO format converter
- `check_training.py` - Quick training progress checker
- `runs/train/yolov8x_korean_vehicles/weights/best.pt` - Best model checkpoint
- `runs/train/yolov8x_korean_vehicles/results.png` - Training graphs

**Note:** This training project is separate from the main application. The main app uses pretrained YOLOv8n for general vehicle detection, while this project trains YOLOv8x specifically on Korean satellite imagery.

## Additional Resources

See also:
- [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md) - Comprehensive local testing instructions
- [KOREAN_SATELLITE_DATA_GUIDE.md](KOREAN_SATELLITE_DATA_GUIDE.md) - South Korea satellite data sources
- [korean_vehicle_detection/README.md](korean_vehicle_detection/README.md) - YOLOv8x training guide (Korean)
- FastAPI docs: http://localhost:8000/docs (when server running)
