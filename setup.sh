#!/bin/bash

echo "🚀 Setting up Satellite Vehicle Tracker..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Python and Node.js found"

# Install backend dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

# Download YOLO model if it doesn't exist
if [ ! -f "yolov8n.pt" ]; then
    echo "🤖 Downloading YOLO model..."
    python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
fi

cd ..

# Install frontend dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment file..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration (especially Google Maps API key)"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "  npm run dev"
echo ""
echo "This will start:"
echo "  - Backend API on http://localhost:5000"
echo "  - Frontend on http://localhost:3000"
echo ""
echo "Don't forget to:"
echo "  1. Get a Google Maps API key and add it to .env"
echo "  2. Configure other settings in .env as needed"
echo ""
echo "Happy tracking! 🛰️"

