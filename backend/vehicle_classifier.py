import cv2
import numpy as np
from ultralytics import YOLO
import torch
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import json

class AdvancedVehicleClassifier:
    def __init__(self, model_path: str = 'yolov8n.pt', confidence_threshold: float = 0.5):
        """
        Advanced vehicle classifier with specific type detection
        
        Args:
            model_path: Path to YOLO model weights
            confidence_threshold: Minimum confidence for detections
        """
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        
        # Enhanced vehicle classification with Korean context
        self.vehicle_types = {
            # Cars
            2: 'car',
            3: 'motorcycle', 
            5: 'bus',
            7: 'truck',
            
            # Additional classifications for Korean vehicles
            'sedan': 'sedan',           # 승용차
            'suv': 'suv',               # SUV
            'sports': 'sports',         # 스포츠카
            'van': 'van',               # 밴
            'pickup': 'pickup',         # 픽업트럭
            'delivery': 'delivery',     # 배송차량
            'taxi': 'taxi',            # 택시
            'ambulance': 'ambulance',   # 구급차
            'police': 'police',         # 경찰차
            'fire_truck': 'fire_truck', # 소방차
            
            # Aircraft
            'aircraft': 'aircraft',     # 항공기
            'helicopter': 'helicopter', # 헬리콥터
            'drone': 'drone',          # 드론
        }
        
        # Korean vehicle brand recognition patterns
        self.korean_brands = {
            'hyundai': ['hyundai', '현대'],
            'kia': ['kia', '기아'],
            'genesis': ['genesis', '제네시스'],
            'ssangyong': ['ssangyong', '쌍용'],
            'renault_samsung': ['renault', 'samsung', '르노삼성']
        }

    def classify_vehicle_detailed(self, image: np.ndarray, detection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform detailed vehicle classification with Korean context
        
        Args:
            image: Input image as numpy array
            detection: Vehicle detection result
            
        Returns:
            Detailed classification with type, brand, and confidence
        """
        try:
            # Extract vehicle region from image
            x1, y1, x2, y2 = detection['bbox']
            vehicle_crop = image[y1:y2, x1:x2]
            
            if vehicle_crop.size == 0:
                return self._default_classification(detection)
            
            # Resize for better analysis
            vehicle_crop = cv2.resize(vehicle_crop, (224, 224))
            
            # Perform detailed analysis
            vehicle_type = self._classify_vehicle_type(vehicle_crop)
            brand_info = self._detect_korean_brand(vehicle_crop)
            size_category = self._classify_size_category(vehicle_crop, detection)
            color_info = self._analyze_vehicle_color(vehicle_crop)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(
                detection['confidence'], vehicle_type['confidence'], brand_info['confidence']
            )
            
            return {
                'vehicle_type': vehicle_type['type'],
                'type_confidence': vehicle_type['confidence'],
                'brand': brand_info['brand'],
                'brand_confidence': brand_info['confidence'],
                'size_category': size_category,
                'color': color_info,
                'overall_confidence': overall_confidence,
                'korean_context': True,
                'classification_details': {
                    'detection_method': 'yolo_plus_analysis',
                    'timestamp': datetime.now().isoformat(),
                    'image_dimensions': {'width': x2-x1, 'height': y2-y1}
                }
            }
            
        except Exception as e:
            print(f"Error in detailed classification: {e}")
            return self._default_classification(detection)

    def _classify_vehicle_type(self, vehicle_crop: np.ndarray) -> Dict[str, Any]:
        """Classify specific vehicle type (sedan, SUV, sports, etc.)"""
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2GRAY)
        
        # Analyze vehicle proportions
        height, width = gray.shape
        aspect_ratio = width / height
        
        # Analyze vehicle shape characteristics
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate shape features
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            
            # Analyze vehicle characteristics
            vehicle_type, confidence = self._analyze_vehicle_characteristics(
                aspect_ratio, area, perimeter, vehicle_crop
            )
            
            return {
                'type': vehicle_type,
                'confidence': confidence
            }
        
        return {'type': 'car', 'confidence': 0.5}

    def _analyze_vehicle_characteristics(self, aspect_ratio: float, area: float, 
                                       perimeter: float, vehicle_crop: np.ndarray) -> Tuple[str, float]:
        """Analyze vehicle characteristics to determine type"""
        
        # Analyze roof line and body shape
        gray = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # Check for SUV characteristics (higher, boxier)
        if aspect_ratio < 1.5 and height > width * 0.6:
            return 'suv', 0.8
        
        # Check for sports car characteristics (lower, longer)
        if aspect_ratio > 2.0 and height < width * 0.4:
            return 'sports', 0.7
        
        # Check for truck characteristics (very boxy, high)
        if aspect_ratio < 1.2 and height > width * 0.7:
            return 'truck', 0.8
        
        # Check for van characteristics (tall, rectangular)
        if 1.3 < aspect_ratio < 1.8 and height > width * 0.6:
            return 'van', 0.7
        
        # Check for pickup truck (truck bed visible)
        if self._has_pickup_characteristics(vehicle_crop):
            return 'pickup', 0.8
        
        # Default to sedan for normal proportions
        if 1.5 < aspect_ratio < 2.0:
            return 'sedan', 0.6
        
        return 'car', 0.5

    def _has_pickup_characteristics(self, vehicle_crop: np.ndarray) -> bool:
        """Check if vehicle has pickup truck characteristics"""
        gray = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2GRAY)
        
        # Look for distinct cab and bed separation
        height, width = gray.shape
        
        # Analyze vertical sections
        left_section = gray[:, :width//3]
        middle_section = gray[:, width//3:2*width//3]
        right_section = gray[:, 2*width//3:]
        
        # Check for cab (darker, more complex) vs bed (lighter, simpler)
        left_std = np.std(left_section)
        right_std = np.std(right_section)
        
        # Pickup trucks typically have more complex cab area
        return left_std > right_std * 1.5

    def _detect_korean_brand(self, vehicle_crop: np.ndarray) -> Dict[str, Any]:
        """Detect Korean vehicle brands"""
        # This would typically use a trained brand recognition model
        # For now, return placeholder with some basic analysis
        
        # Analyze vehicle shape patterns that might indicate brand
        gray = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2GRAY)
        
        # Simple heuristics for Korean brands (would be replaced with actual ML model)
        # Hyundai: Often have distinctive grille patterns
        # Kia: Modern, angular designs
        # Genesis: Luxury features
        
        # Placeholder brand detection
        return {
            'brand': 'unknown',
            'confidence': 0.3,
            'korean_brands_detected': []
        }

    def _classify_size_category(self, vehicle_crop: np.ndarray, detection: Dict[str, Any]) -> str:
        """Classify vehicle size category"""
        width = detection['width']
        height = detection['height']
        
        # Calculate size based on detection dimensions
        size_score = (width * height) / 10000  # Normalize
        
        if size_score > 50:
            return 'large'
        elif size_score > 25:
            return 'medium'
        else:
            return 'small'

    def _analyze_vehicle_color(self, vehicle_crop: np.ndarray) -> Dict[str, Any]:
        """Analyze vehicle color"""
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2HSV)
        
        # Define color ranges
        color_ranges = {
            'white': ([0, 0, 200], [180, 30, 255]),
            'black': ([0, 0, 0], [180, 255, 50]),
            'red': ([0, 50, 50], [10, 255, 255]),
            'blue': ([100, 50, 50], [130, 255, 255]),
            'green': ([40, 50, 50], [80, 255, 255]),
            'yellow': ([20, 50, 50], [40, 255, 255]),
            'gray': ([0, 0, 50], [180, 30, 200]),
            'silver': ([0, 0, 100], [180, 30, 200])
        }
        
        dominant_color = 'unknown'
        max_pixels = 0
        
        for color, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            pixel_count = cv2.countNonZero(mask)
            
            if pixel_count > max_pixels:
                max_pixels = pixel_count
                dominant_color = color
        
        return {
            'primary_color': dominant_color,
            'confidence': min(max_pixels / (vehicle_crop.shape[0] * vehicle_crop.shape[1]), 1.0)
        }

    def _calculate_overall_confidence(self, detection_conf: float, 
                                    type_conf: float, brand_conf: float) -> float:
        """Calculate overall confidence score"""
        # Weighted average with detection confidence having highest weight
        weights = [0.6, 0.3, 0.1]  # detection, type, brand
        scores = [detection_conf, type_conf, brand_conf]
        
        return sum(w * s for w, s in zip(weights, scores))

    def _default_classification(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        """Return default classification when detailed analysis fails"""
        return {
            'vehicle_type': detection.get('class', 'car'),
            'type_confidence': detection.get('confidence', 0.5),
            'brand': 'unknown',
            'brand_confidence': 0.0,
            'size_category': 'medium',
            'color': {'primary_color': 'unknown', 'confidence': 0.0},
            'overall_confidence': detection.get('confidence', 0.5),
            'korean_context': False,
            'classification_details': {
                'detection_method': 'basic_yolo',
                'timestamp': datetime.now().isoformat()
            }
        }

    def get_parking_duration_analysis(self, vehicle_id: str, detections: List[Dict]) -> Dict[str, Any]:
        """Analyze parking duration for a vehicle"""
        if len(detections) < 2:
            return {'duration_hours': 0, 'status': 'insufficient_data'}
        
        # Sort by timestamp
        detections.sort(key=lambda x: x['timestamp'])
        
        first_seen = detections[0]['timestamp']
        last_seen = detections[-1]['timestamp']
        
        duration = (last_seen - first_seen).total_seconds() / 3600
        
        # Analyze movement pattern
        movements = []
        for i in range(1, len(detections)):
            prev = detections[i-1]
            curr = detections[i]
            
            distance = self._calculate_distance(
                prev['latitude'], prev['longitude'],
                curr['latitude'], curr['longitude']
            )
            movements.append(distance)
        
        avg_movement = np.mean(movements) if movements else 0
        is_stationary = avg_movement < 10  # Less than 10m average movement
        
        return {
            'duration_hours': duration,
            'first_seen': first_seen.isoformat(),
            'last_seen': last_seen.isoformat(),
            'is_stationary': is_stationary,
            'avg_movement_meters': avg_movement,
            'status': 'parked' if is_stationary and duration > 2 else 'moving'
        }

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in meters"""
        from math import radians, cos, sin, asin, sqrt
        
        # Haversine formula
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Earth's radius in meters
        
        return c * r
