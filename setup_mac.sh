#!/bin/bash

echo "🍎 Setting up Satellite Vehicle Tracker on macOS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    print_warning "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_error "Python 3.8+ required. Found: $python_version"
    print_status "Installing Python via Homebrew..."
    brew install python@3.11
fi

# Check Node.js version
if ! command -v node &> /dev/null; then
    print_warning "Node.js not found. Installing Node.js..."
    brew install node
fi

node_version=$(node --version | cut -d. -f1 | sed 's/v//')
if [ "$node_version" -lt 16 ]; then
    print_error "Node.js 16+ required. Found: v$node_version"
    print_status "Updating Node.js..."
    brew install node
fi

print_success "Python and Node.js versions verified"

# Install system dependencies for geospatial libraries
print_status "Installing system dependencies..."
brew install gdal geos proj

# Install Python dependencies
print_status "Installing Python dependencies..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
print_status "Installing Python packages..."
pip install -r requirements.txt

# Download YOLO model if it doesn't exist
if [ ! -f "yolov8n.pt" ]; then
    print_status "Downloading YOLO model..."
    python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
fi

cd ..

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Install root dependencies
print_status "Installing root dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating environment file..."
    cp env.example .env
    print_warning "Please edit .env file with your configuration (especially Google Maps API key)"
fi

# Create startup script
print_status "Creating startup script..."
cat > start_mac.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Satellite Vehicle Tracker..."

# Activate Python virtual environment
cd backend
source venv/bin/activate
cd ..

# Start both frontend and backend
npm run dev
EOF

chmod +x start_mac.sh

print_success "Setup complete!"
echo ""
echo "🎉 Your Satellite Vehicle Tracker is ready!"
echo ""
echo "To start the application:"
echo "  ./start_mac.sh"
echo ""
echo "Or manually:"
echo "  cd backend && source venv/bin/activate && python app.py"
echo "  cd frontend && npm start"
echo ""
echo "Access the application at:"
echo "  🌐 Frontend: http://localhost:3000"
echo "  🔧 Backend API: http://localhost:5000"
echo ""
echo "📝 Don't forget to:"
echo "  1. Get a Google Maps API key and add it to .env"
echo "  2. Configure other settings in .env as needed"
echo ""
echo "🛰️ Happy satellite tracking!"
