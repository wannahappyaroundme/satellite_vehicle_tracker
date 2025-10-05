import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///satellite_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google Maps API
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    # Computer Vision Model Settings
    YOLO_MODEL_PATH = os.environ.get('YOLO_MODEL_PATH') or 'yolov8n.pt'
    CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', '0.5'))
    
    # Storage Analysis Settings
    STORAGE_ANALYSIS_DAYS = int(os.environ.get('STORAGE_ANALYSIS_DAYS', '7'))
    CLUSTER_RADIUS_KM = float(os.environ.get('CLUSTER_RADIUS_KM', '0.5'))

