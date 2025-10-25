#!/bin/bash
echo "🚀 Starting Satellite Vehicle Tracker..."

# Activate Python virtual environment
cd backend
source venv/bin/activate
cd ..

# Start both frontend and backend
npm run dev
