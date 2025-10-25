# Satellite Vehicle Tracker

thanks to Cursor & gemini

A comprehensive satellite imagery analysis platform that detects vehicles, analyzes storage potential, and provides interactive mapping capabilities.

## Features

### 🚗 Vehicle Detection
- **AI-Powered Detection**: Uses YOLO (You Only Look Once) models to detect vehicles in satellite imagery
- **Multiple Vehicle Types**: Cars, trucks, buses, motorcycles, aircraft, and more
- **Real-time Processing**: Upload satellite images and get instant vehicle detection results
- **Confidence Scoring**: Each detection includes a confidence percentage

### 🗺️ Interactive Mapping
- **Google Maps Integration**: Interactive map interface for visualizing detected vehicles
- **Real-time Updates**: Live updates as new vehicles are detected
- **Custom Markers**: Color-coded markers for different vehicle types
- **Zoom & Pan**: Full map navigation capabilities

### 🔍 Advanced Search
- **Geographic Search**: Search for vehicles within specific areas and time ranges
- **Filter by Type**: Filter results by vehicle type (car, truck, aircraft, etc.)
- **Time-based Filtering**: Search within 24h, 7d, or 30d time windows
- **Confidence Filtering**: Set minimum confidence thresholds

### 📊 Storage Analysis
- **Long-term Storage Detection**: Identify vehicles that may be seeking long-term storage
- **Clustering Analysis**: Group vehicles by location and behavior patterns
- **Potential Scoring**: AI-powered scoring system for storage potential (0-100%)
- **Recommendations**: Generate actionable recommendations for storage locations

### ✈️ Aircraft Detection
- **Specialized Detection**: Optimized algorithms for detecting aircraft in satellite imagery
- **Airport Monitoring**: Track aircraft movements and parking patterns
- **Multi-type Support**: Planes, helicopters, drones, and other aircraft

## Technology Stack

### Backend
- **Python Flask**: RESTful API server
- **YOLO**: Computer vision for object detection
- **OpenCV**: Image processing and manipulation
- **SQLAlchemy**: Database ORM
- **scikit-learn**: Machine learning for clustering and analysis

### Frontend
- **React + TypeScript**: Modern, type-safe frontend
- **Leaflet**: Interactive mapping library
- **Styled Components**: CSS-in-JS styling
- **Axios**: HTTP client for API communication

### Database
- **SQLite**: Default database (easily configurable for PostgreSQL/MySQL)
- **Geospatial Support**: Location-based queries and indexing

## Quick Start

### Prerequisites
- **Python 3.8+** (3.11 recommended)
- **Node.js 16+** (18 recommended)
- **Git**
- **Docker & Docker Compose** (for production deployment)

### 🚀 One-Click Setup

#### For macOS:
```bash
git clone <repository-url>
cd satellite_project
./setup_mac.sh
```

#### For Windows:
```batch
git clone <repository-url>
cd satellite_project
setup_windows.bat
```

#### Manual Installation:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd satellite_project
   ```

2. **Install dependencies**
   ```bash
   # Install all dependencies
   npm run install:all
   
   # Or install separately:
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

3. **Configure environment**
   ```bash
   # Copy environment template
   cp env.example .env
   
   # Edit .env with your configuration
   # At minimum, set your Google Maps API key
   ```

4. **Start the application**
   ```bash
   # Start both frontend and backend
   npm run dev
   
   # Or start separately:
   # Backend (port 5000)
   cd backend && python app.py
   
   # Frontend (port 3000)
   cd frontend && npm start
   ```

5. **Access the application**
   - Open http://localhost:3000 in your browser
   - The backend API will be available at http://localhost:5000

## Usage Guide

### Uploading Satellite Images
1. Navigate to the "Upload" tab
2. Drag and drop an image or click to browse
3. Set the image location (latitude/longitude)
4. Click "Process Image" to detect vehicles
5. View results on the map and in the vehicle list

### Searching for Vehicles
1. Go to the "Search" tab
2. Set your search location and filters
3. Choose vehicle type and time range
4. Click "Search Vehicles" to find matches
5. Use "Storage Analysis" for deeper insights

### Analyzing Storage Potential
1. Run a storage analysis on a specific area
2. Review the potential score and recommendations
3. Explore vehicle clusters and patterns
4. Use the "Storage" tab to view detailed analysis

### 🚨 Long-Term Stopped Vehicle Detection
1. Navigate to the "Long-Term" tab
2. Set your analysis location and time range
3. Click "Detect Long-Term Stopped" to find vehicles that haven't moved
4. Review risk assessments and alerts
5. Use "Get Area Summary" for comprehensive analysis

### 🇰🇷 South Korea Satellite Data Integration
1. Use the South Korea-specific satellite data sources
2. Access KOMPSAT, Sentinel-2, and Landsat imagery
3. Get coverage information for major Korean cities
4. Download satellite imagery for specific locations
5. View real-time satellite pass predictions

### 🎯 Airbnb-Style Vehicle Details
1. Hover over any vehicle marker on the map
2. View detailed vehicle information in a beautiful popup card
3. See vehicle type classification (SUV, sedan, truck, etc.)
4. Check parking duration and risk assessment
5. View confidence percentages and detailed analytics

## API Endpoints

### Vehicle Detection
- `POST /api/upload-image` - Process satellite image for vehicle detection
- `GET /api/search-vehicles` - Search for vehicles in specific area
- `GET /api/aircraft-search` - Search specifically for aircraft

### Storage Analysis
- `GET /api/storage-analysis` - Analyze storage potential for an area

### Long-Term Detection
- `GET /api/long-term-stopped` - Detect long-term stopped vehicles
- `GET /api/vehicle-history/<id>` - Get movement history for a vehicle
- `GET /api/area-summary` - Get comprehensive area analysis

### South Korea Satellite Data
- `GET /api/south-korea/coverage` - Get satellite coverage for Korean locations
- `GET /api/south-korea/imagery` - Get recent satellite imagery
- `GET /api/south-korea/cities` - Get coverage for major Korean cities
- `GET /api/south-korea/download-guide` - Get download instructions

### Vehicle Details
- `GET /api/vehicle/<id>/details` - Get detailed vehicle information with classification

### System
- `GET /api/health` - Health check endpoint

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `dev-secret-key-change-in-production` |
| `DATABASE_URL` | Database connection string | `sqlite:///satellite_tracker.db` |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | Required for production |
| `YOLO_MODEL_PATH` | Path to YOLO model | `yolov8n.pt` |
| `CONFIDENCE_THRESHOLD` | Minimum detection confidence | `0.5` |
| `STORAGE_ANALYSIS_DAYS` | Days to analyze for storage | `7` |
| `CLUSTER_RADIUS_KM` | Clustering radius in km | `0.5` |

### Model Configuration
The system uses YOLOv8 by default, but you can configure different models:
- `yolov8n.pt` - Nano (fastest, lower accuracy)
- `yolov8s.pt` - Small (balanced)
- `yolov8m.pt` - Medium (higher accuracy)
- `yolov8l.pt` - Large (highest accuracy, slower)

## Development

### Project Structure
```
satellite_project/
├── backend/
│   ├── app.py              # Flask application
│   ├── models.py           # Database models
│   ├── vehicle_detector.py # YOLO vehicle detection
│   ├── storage_analyzer.py # Storage analysis algorithms
│   ├── config.py           # Configuration
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   ├── types.ts        # TypeScript types
│   │   └── App.tsx         # Main application
│   └── package.json        # Node dependencies
└── README.md
```

### Adding New Features
1. Backend: Add new endpoints in `app.py`
2. Frontend: Create components in `src/components/`
3. API: Update `src/services/api.ts`
4. Types: Add interfaces in `src/types.ts`

## Deployment

### Production Setup
1. Set production environment variables
2. Use PostgreSQL for production database
3. Configure reverse proxy (nginx)
4. Set up SSL certificates
5. Use process manager (PM2, systemd)

### GitHub Pages Deployment (Frontend Only)
```bash
# Quick deploy to GitHub Pages
./deploy_gh_pages.sh

# Manual deploy
cd frontend && npm run deploy
```

### Docker Deployment (Full Stack)
```bash
# Build and run with Docker Compose
./deploy.sh
```

### Manual Docker Setup
```bash
# Build and start services
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check service health
docker-compose ps
docker-compose logs -f
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:
- Create an issue on GitHub
- Check the documentation
- Review the API endpoints

## 🎯 Key Features for Long-Term Stopped Vehicle Detection

### ✅ Implemented Features:
- **AI-Powered Detection**: Advanced algorithms to identify vehicles that haven't moved for extended periods
- **Advanced Vehicle Classification**: Detect specific vehicle types (SUV, sedan, truck, sports car, etc.)
- **Risk Assessment**: Automatic risk scoring (LOW/MEDIUM/HIGH) based on multiple factors
- **Clustering Analysis**: Group nearby stopped vehicles to identify problem areas
- **Movement Pattern Analysis**: Track vehicle behavior over time to detect stopping patterns
- **Alert System**: Generate alerts for concerning stop patterns
- **Airbnb-Style UI**: Beautiful hover cards with detailed vehicle information
- **South Korea Integration**: Access to KOMPSAT, Sentinel-2, and Landsat satellite data
- **Parking Duration Tracking**: Real-time analysis of how long vehicles have been parked
- **Public Access**: No login required - anyone can access and analyze areas
- **Cross-Platform**: Works on both Mac and Windows with one-click setup

### 🔍 Detection Capabilities:
- **Time-Based Analysis**: Detect vehicles stopped for 6+ hours, 24+ hours, or custom periods
- **Movement Thresholds**: Configurable movement detection (default 50m radius)
- **Confidence Scoring**: AI confidence levels for each detection
- **Historical Analysis**: Analyze up to 30 days of vehicle data
- **Geographic Clustering**: Identify clusters of stopped vehicles in specific areas
- **Vehicle Type Classification**: Distinguish between SUV, sedan, truck, sports car, van, pickup, etc.
- **Korean Brand Recognition**: Detect Hyundai, Kia, Genesis, and other Korean vehicle brands
- **Color Analysis**: Identify vehicle colors (white, black, red, blue, etc.)
- **Size Category Detection**: Classify vehicles as small, medium, or large

### 🚨 Alert Types:
- **Long-Term Stop Alerts**: Vehicles stopped for extended periods
- **Cluster Alerts**: Multiple vehicles stopped in the same area
- **Risk-Based Alerts**: High-risk situations requiring immediate attention
- **Storage Potential Alerts**: Areas with high storage potential

## Roadmap

- [ ] Real-time satellite feed integration
- [ ] Advanced vehicle tracking over time
- [ ] Machine learning model training interface
- [ ] Mobile app development
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration with traffic management systems
- [ ] Automated report generation
- [ ] Email/SMS alert notifications
- [ ] Integration with parking enforcement systems

