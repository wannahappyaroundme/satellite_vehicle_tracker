# Local Testing Guide

This guide explains how to test the Satellite Vehicle Tracker application locally before deploying.

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn
- Git

## Quick Start (Recommended)

### Method 1: Using the Start Script (Mac)

```bash
./start_mac.sh
```

However, this script only starts the frontend. To start both frontend and backend, follow Method 2.

### Method 2: Manual Start (Recommended)

#### Terminal 1: Start Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

The backend should start on: `http://localhost:5000`

#### Terminal 2: Start Frontend

```bash
cd frontend
npm start
```

The frontend should start on: `http://localhost:3000`

**Access the app:** Open `http://localhost:3000` in your browser

## Initial Setup (First Time Only)

If you haven't set up the project yet:

### 1. Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (happens automatically on first run)
python app.py
```

### 2. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Testing Checklist

### ✅ Backend API Tests

1. **Health Check**
   ```bash
   curl http://localhost:5000/api/health
   ```
   Expected: `{"status":"healthy","timestamp":"..."}`

2. **Test Vehicle Search**
   ```bash
   curl "http://localhost:5000/api/search-vehicles?lat=37.5665&lng=126.9780&radius=0.01"
   ```

3. **Test Storage Analysis**
   ```bash
   curl "http://localhost:5000/api/storage-analysis?lat=37.5665&lng=126.9780&radius=0.01"
   ```

### ✅ Frontend Tests

1. **Check Homepage Loads**
   - Open `http://localhost:3000`
   - Verify the map and sidebar are visible
   - Check that there are no console errors (F12 Developer Tools)

2. **Test Search Panel**
   - Enter coordinates (e.g., Seoul: 37.5665, 126.9780)
   - Select search radius
   - Click "Search Vehicles"
   - Verify no errors in console

3. **Test Upload Panel**
   - Click "Upload" tab
   - Try uploading an image (satellite imagery)
   - Verify detection works or shows appropriate error

4. **Test Vehicle List**
   - Click "Vehicles" tab
   - Verify vehicles list appears (if any detected)

5. **Test Storage Analysis**
   - Click "Storage" tab
   - Verify analysis results appear

6. **Test Long-Term Detection**
   - Click "Long-Term" tab
   - Enter coordinates and analyze

### ✅ Integration Tests

1. **Upload and Detect Workflow**
   - Upload a satellite image with vehicles
   - Verify vehicles appear on map
   - Click on a vehicle marker
   - Verify popup shows vehicle details

2. **Search and Analyze Workflow**
   - Search for vehicles in an area
   - Click "Storage Analysis"
   - Verify recommended locations appear on map

## Common Issues & Solutions

### Issue 1: Backend Not Starting

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 2: Frontend Shows Blank Page

**Error:** Blank page at `http://localhost:3000`

**Solution:**
1. Check if `homepage` in `frontend/package.json` is set to `"."`
2. Restart the frontend server:
   ```bash
   cd frontend
   npm start
   ```

### Issue 3: Proxy Errors

**Error:** `Proxy error: Could not proxy request ... ECONNREFUSED`

**Solution:**
- Make sure the backend is running on port 5000
- Check `proxy` setting in `frontend/package.json` is `"http://localhost:5000"`

### Issue 4: Port Already in Use

**Error:** `Something is already running on port 3000`

**Solution:**
```bash
# Find process using the port
lsof -ti:3000

# Kill the process
kill -9 $(lsof -ti:3000)

# Or use a different port
PORT=3001 npm start
```

### Issue 5: GDAL/Rasterio Installation Issues

**Error:** `ERROR: Failed building wheel for GDAL`

**Solution (Mac):**
```bash
brew install gdal
pip install --no-cache-dir gdal==3.8.0
```

**Solution (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y gdal-bin libgdal-dev
pip install --no-cache-dir gdal==3.8.0
```

## Build & Test Production Bundle

### Test Production Build Locally

```bash
# Build frontend
cd frontend
npm run build

# Serve the build locally (install serve if needed)
npm install -g serve
serve -s build -l 3000
```

### Test TypeScript Linting

```bash
cd frontend
npm run lint
```

Expected: No type errors

### Test Python Linting

```bash
cd backend
pip install flake8
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

Expected: No critical errors

## Performance Testing

### Backend Load Test (Optional)

```bash
# Install Apache Bench (comes with Apache)
# Mac: Already installed
# Ubuntu: sudo apt-get install apache2-utils

# Test health endpoint
ab -n 1000 -c 10 http://localhost:5000/api/health
```

### Frontend Performance Audit

1. Open `http://localhost:3000` in Chrome
2. Press F12 to open DevTools
3. Go to "Lighthouse" tab
4. Run audit for Performance, Accessibility, Best Practices, SEO

## Database Testing

### Check Database

```bash
cd backend/instance
sqlite3 satellite_tracker.db

# In SQLite shell:
.tables
SELECT COUNT(*) FROM vehicle_location;
.quit
```

### Reset Database (If Needed)

```bash
cd backend/instance
rm satellite_tracker.db
# Database will be recreated on next backend start
```

## Environment Variables (Optional)

Create a `.env` file in the `backend` directory:

```bash
# backend/.env
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///satellite_tracker.db
SECRET_KEY=your-secret-key-here
```

## Testing with Real Data

### Download Sample Satellite Imagery

1. Visit [Google Earth Engine](https://earthengine.google.com/)
2. Or use [Sentinel Hub](https://www.sentinel-hub.com/)
3. Download a satellite image of a parking lot or airport
4. Upload through the UI

### Test Coordinates (Known Locations)

- **Seoul, South Korea:** `37.5665, 126.9780`
- **Incheon Airport:** `37.4602, 126.4407`
- **New York City:** `40.7128, -74.0060`
- **Los Angeles Airport:** `33.9416, -118.4085`

## Automated Testing (Future Enhancement)

### Backend Unit Tests

```bash
cd backend
pytest tests/
```

### Frontend Unit Tests

```bash
cd frontend
npm test
```

## Monitoring Logs

### Backend Logs

The Flask development server outputs logs to the terminal where you started it.

### Frontend Logs

Open browser DevTools (F12) and check the Console tab.

## Next Steps After Local Testing

1. ✅ All tests pass locally
2. Commit and push changes to GitHub
3. GitHub Actions will run automated tests
4. If tests pass, Docker images are built and pushed
5. Deploy to production server

## Troubleshooting

If you encounter any issues not covered here:

1. Check the terminal output for error messages
2. Check browser console (F12) for frontend errors
3. Check GitHub Issues for similar problems
4. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Your environment (OS, Python version, Node version)

## Quick Reference Commands

```bash
# Start backend
cd backend && source venv/bin/activate && python app.py

# Start frontend
cd frontend && npm start

# Check backend health
curl http://localhost:5000/api/health

# Build frontend for production
cd frontend && npm run build

# Run tests
cd backend && pytest
cd frontend && npm test

# Lint code
cd backend && flake8 .
cd frontend && npm run lint
```

---

**Happy Testing! 🚀**

