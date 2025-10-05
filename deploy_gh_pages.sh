#!/bin/bash

echo "🚀 Deploying Satellite Vehicle Tracker to GitHub Pages..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not initialized. Please run 'git init' first"
    exit 1
fi

# Check if GitHub remote is set
if ! git remote get-url origin >/dev/null 2>&1; then
    print_warning "GitHub remote not set. Please add your GitHub repository:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/satellite-vehicle-tracker.git"
    exit 1
fi

print_status "Building frontend application..."

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    print_status "Installing dependencies..."
    npm install
fi

# Build the application
print_status "Building React application..."
npm run build

# Check if build was successful by looking for the build directory
if [ ! -d "frontend/build" ]; then
    echo "❌ Build failed. Please check for errors above."
    exit 1
fi

print_success "Build completed successfully!"

# Deploy to GitHub Pages
print_status "Deploying to GitHub Pages..."
npm run deploy

if [ $? -eq 0 ]; then
    print_success "Deployment to GitHub Pages completed!"
    echo ""
    echo "🌐 Your application is now available at:"
    echo "   https://$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\)\/\([^.]*\).*/\1.github.io\/\2/')"
    echo ""
    echo "📝 Note: It may take a few minutes for the changes to be visible."
    echo ""
    echo "🔧 To update your deployment:"
    echo "   1. Make changes to your code"
    echo "   2. Run this script again: ./deploy_gh_pages.sh"
    echo ""
    echo "📚 For backend deployment, see the main README.md"
else
    echo "❌ Deployment failed. Please check the error messages above."
    exit 1
fi

# Script completed
