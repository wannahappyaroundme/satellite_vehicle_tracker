# 🚗 Abandoned Vehicle Detection System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.120-009688.svg)](https://fastapi.tiangolo.com/)

> Automatic Detection of Long-term Abandoned Vehicles Using VWorld Aerial Imagery and AI

**English** | [한국어](./README.md)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [VWorld API Setup](#-vworld-api-setup)
- [Usage](#-usage)
- [Caching System](#-caching-system)
- [Project Structure](#-project-structure)
- [License](#-license)

---

## 🎯 Overview

The Abandoned Vehicle Detection System automatically identifies vehicles that have been parked in the same location for extended periods using real-time aerial imagery from the **VWorld API** and **ResNet50 deep learning model**.

### Core Principle

1. 📍 User inputs address or coordinates
2. 🛰️ Download high-resolution aerial images from VWorld API (12cm GSD)
3. 🤖 Extract vehicle features using ResNet50
4. 📊 Detect abandonment through time-series comparison (≥90% similarity)
5. ⚠️ Classify risk levels (CRITICAL / HIGH / MEDIUM / LOW)

### Why This System?

- **Public Safety**: Abandoned vehicles may be stolen or illegally dumped
- **Urban Aesthetics**: Reduce parking space waste from abandoned vehicles
- **Automation**: 24/7 AI monitoring instead of manual inspection
- **Cost-Effective**: Free VWorld API + 24-hour caching ≈ $0.03/month

---

## ✨ Key Features

### 1. Real-Time Aerial Image Analysis
- ✅ VWorld WMTS API integration (12cm resolution)
- ✅ Automatic address geocoding
- ✅ Automatic 3×3 tile merging (768×768 pixels)

### 2. AI-Based Abandoned Vehicle Detection
- ✅ ResNet50 feature extraction (ImageNet pretrained)
- ✅ Cosine similarity-based comparison
- ✅ Automatic risk classification:
  - **CRITICAL**: Similarity ≥95% & 3+ years
  - **HIGH**: Similarity ≥90% & 2+ years
  - **MEDIUM**: Similarity ≥85%
  - **LOW**: <85%

### 3. 24-Hour Caching System ⭐
- ✅ Server-side disk caching
- ✅ First request: VWorld API call (~5 seconds)
- ✅ Subsequent requests: Instant from cache (~0.1 seconds, **100x faster**)
- ✅ Automatic expiration and cleanup (24-hour TTL)
- ✅ 80% reduction in API calls

### 4. User-Friendly Interface
- ✅ Responsive web design (React + TypeScript)
- ✅ Real-time map display (Leaflet)
- ✅ Sample data analysis (demo mode)
- ✅ Real location analysis
- ✅ CCTV verification (placeholder)

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** 0.120.0 - High-performance Python web framework
- **PyTorch** 2.1.1 - ResNet50 deep learning model
- **OpenCV** 4.8.1 - Image processing
- **Pillow** 10.1.0 - Tile merging
- **SQLAlchemy** 2.0.23 - ORM (optional)

### Frontend
- **React** 18 - UI library
- **TypeScript** - Type safety
- **Leaflet** - Map display
- **Styled Components** - CSS-in-JS
- **Axios** - HTTP client

### AI/ML
- **ResNet50** - Feature extraction (torchvision)
- **YOLOv8** - Vehicle detection (optional)
- **scikit-learn** - Cosine similarity

### APIs & Data
- **VWorld API** - Aerial imagery, geocoding (free)
- **NGII** - Korean geographic data

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+
- **Python** 3.11+
- **VWorld API Key** ([How to get](#-vworld-api-setup))
- **Git**

### 1. Clone Repository

```bash
git clone https://github.com/wannahappyaroundme/satellite_vehicle_tracker.git
cd satellite_vehicle_tracker
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 4. Environment Variables

Add your VWorld API key to `.env` file in project root:

```bash
# VWorld API Configuration
NGII_API_KEY=paste-your-api-key-here

# Backend Settings
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///satellite_tracker.db

# Cache Settings (optional)
CACHE_TTL_HOURS=24
CACHE_MAX_SIZE_GB=5
```

### 5. Run Servers

**Backend (FastAPI):**
```bash
cd backend
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

**Frontend (React):**
```bash
cd frontend
npm start
```

**Open in browser:**
```
http://localhost:3000
```

---

## 🔑 VWorld API Setup

### 1. Sign Up and Apply for API

1. Visit **https://www.vworld.kr**
2. Sign up and login
3. Go to **My Page** → **Open API Management** → **Apply**

### 2. Application Information

```
Service Name: Abandoned Vehicle Detection System
Service URL: http://localhost:3000
Purpose: Public Safety / Vehicle Management
```

### 3. Select APIs (Only 3!)

- ☑️ **WMTS/TMS API** (Required) - Aerial image tiles
- ☑️ **Geocoder API** (Required) - Address → Coordinates
- ☑️ **WMS/WFS API** (Optional) - Large area download

### 4. Wait for Approval

- Usually approved within **1-2 days** (email notification)
- Active 1-2 hours after approval

### 5. Get API Key and Configure

```bash
# Edit .env file
NGII_API_KEY=8F1EC6DE-5BBA-329A-94AE-BD66BE1DB672
```

### 6. Test

```bash
cd backend
python test_ngii_api.py

# Success output:
# ✓ Address search successful!
# ✓ Aerial image download successful!
```

**Detailed Guide**: [VWORLD_API_GUIDE.md](./VWORLD_API_GUIDE.md)

---

## 📱 Usage

### Sample Image Analysis (Demo)

1. Click **"Abandoned Vehicle Detection"** tab
2. Click **"Start Sample Analysis"** button
3. View comparison results: 2015 vs 2020 Jeju aerial photos

### Real Location Analysis ⭐

1. Click **"Abandoned Vehicle Detection"** tab
2. Click **"Analyze Real Location"** button
3. Enter address (e.g., `Seoul Gangnam-gu`)
4. Click **"Start Analysis"**
5. Auto-download VWorld aerial images → AI analysis → Display results

### Check Abandoned Vehicles

In analysis results:
- **Red border**: Suspected abandoned vehicle
- **Risk badge**: CRITICAL / HIGH / MEDIUM / LOW
- **Similarity**: ≥90% = High likelihood of abandonment
- **CCTV verification**: Real-time check (placeholder)

---

## 💾 Caching System

### Why Caching?

VWorld API calls take **5-10 seconds**, but caching reduces this to **0.1 seconds**!

### How It Works

```python
# First request (Gangnam Station)
result = service.download_aerial_image(37.4979, 127.0276)
# → VWorld API call (~5 seconds)
# → Save result to cache/aerial_images/

# Second request (same location)
result = service.download_aerial_image(37.4979, 127.0276)
# → Instantly return from cache (~0.1 seconds) ⚡
```

### Check Cache Statistics

```bash
curl http://localhost:8000/api/cache/stats

# Output:
# {
#   "total_requests": 100,
#   "cache_hits": 85,
#   "hit_rate_percent": 85.0,
#   "total_size_mb": 42.5
# }
```

### Cache Management

```bash
# Clean expired cache (24+ hours)
curl -X POST http://localhost:8000/api/cache/cleanup

# Clear all cache
curl -X DELETE http://localhost:8000/api/cache/clear
```

### Cost & Storage

- **100 requests/day**: 50MB
- **Monthly usage**: 1.5GB
- **Storage cost**: $0.03/month (~40 KRW)
- **API reduction**: 80% (with cache hit rate)

---

## 📂 Project Structure

```
satellite_project/
├── backend/
│   ├── fastapi_app.py              # FastAPI main server
│   ├── ngii_api_service.py         # VWorld API + caching
│   ├── aerial_image_cache.py       # Caching system
│   ├── abandoned_vehicle_detector.py  # ResNet50 detector
│   ├── pdf_processor.py            # Image processing
│   ├── demo_mode.py                # Demo data
│   ├── test_ngii_api.py            # API test
│   ├── test_cache_system.py        # Cache test
│   ├── cache/                      # Cache storage
│   │   └── aerial_images/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AbandonedVehiclePanel.tsx  # Detection UI
│   │   │   └── SearchPanel.tsx            # Search UI
│   │   ├── services/
│   │   │   └── api.ts              # API client
│   │   └── App.tsx
│   ├── package.json
│   └── tsconfig.json
│
├── sample_image1.pdf               # Sample aerial (2015)
├── sample_image2.pdf               # Sample aerial (2020)
├── .env                            # Environment variables (API key)
├── CLAUDE.md                       # Development guide
├── VWORLD_API_GUIDE.md             # VWorld API guide
├── README.md                       # Korean docs
└── README_EN.md                    # English docs (this file)
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# VWorld API connection test
python test_ngii_api.py

# Caching system performance test
python test_cache_system.py
```

### Frontend Tests

```bash
cd frontend

# TypeScript type check
npm run lint

# Run tests
npm test
```

---

## 🤝 Contributing

Contributions are welcome! Please send a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Support

### VWorld API
- 📞 **+82-1661-0115** (Weekdays 09:00~18:00 KST)
- 🌐 https://www.vworld.kr
- 📧 support@vworld.kr

### Project
- 🐛 **Issues**: [GitHub Issues](https://github.com/wannahappyaroundme/satellite_vehicle_tracker/issues)

---

## 📄 License

MIT License - Free to use!

---

## 🙏 Acknowledgments

- **VWorld** - Free aerial imagery API
- **NGII** - Korean geographic data
- **FastAPI** - Excellent Python web framework
- **PyTorch** - ResNet50 pretrained models

---

**Made with ❤️ for safer streets**

[⬆ Back to top](#-abandoned-vehicle-detection-system)
