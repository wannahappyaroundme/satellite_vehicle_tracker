import cv2
import numpy as np
from ultralytics import YOLO
import torch
from typing import List, Dict, Any

class VehicleDetector:
    def __init__(self, model_path: str = 'yolov8n.pt', confidence_threshold: float = 0.5):
        """
        Initialize the vehicle detector with YOLO model
        
        Args:
            model_path: Path to YOLO model weights
            confidence_threshold: Minimum confidence for detections
        """
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        
        # Vehicle-related classes in COCO dataset
        self.vehicle_classes = {
            2: 'car',
            3: 'motorcycle', 
            5: 'bus',
            7: 'truck',
            9: 'traffic_light',  # Sometimes useful for context
            15: 'cat',  # Could be misidentified vehicles
            16: 'dog',  # Could be misidentified vehicles
        }
        
        # Additional classes we might want to detect
        self.extended_vehicle_classes = {
            'aircraft': ['plane', 'airplane', 'helicopter', 'drone'],
            'boat': ['ship', 'boat', 'yacht', 'ferry'],
            'construction': ['crane', 'excavator', 'bulldozer'],
            'emergency': ['ambulance', 'fire_truck', 'police_car']
        }

    def detect_vehicles(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect vehicles in the given image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of detected vehicles with coordinates and metadata
        """
        try:
            # Run YOLO inference
            results = self.model(image, conf=self.confidence_threshold)
            
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for i, box in enumerate(boxes):
                        # Get box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Check if it's a vehicle class
                        if class_id in self.vehicle_classes:
                            vehicle_type = self.vehicle_classes[class_id]
                            
                            # Calculate center point
                            center_x = int((x1 + x2) / 2)
                            center_y = int((y1 + y2) / 2)
                            
                            # Calculate width and height
                            width = int(x2 - x1)
                            height = int(y2 - y1)
                            
                            detection = {
                                'x': center_x,
                                'y': center_y,
                                'width': width,
                                'height': height,
                                'confidence': float(confidence),
                                'class': vehicle_type,
                                'class_id': class_id,
                                'bbox': [int(x1), int(y1), int(x2), int(y2)]
                            }
                            
                            detections.append(detection)
            
            return detections
            
        except Exception as e:
            print(f"Error in vehicle detection: {e}")
            return []

    def detect_specific_vehicles(self, image: np.ndarray, vehicle_types: List[str]) -> List[Dict[str, Any]]:
        """
        Detect specific types of vehicles
        
        Args:
            image: Input image as numpy array
            vehicle_types: List of vehicle types to detect
            
        Returns:
            List of detected vehicles matching the specified types
        """
        all_detections = self.detect_vehicles(image)
        
        # Filter detections by vehicle type
        filtered_detections = []
        for detection in all_detections:
            if detection['class'] in vehicle_types:
                filtered_detections.append(detection)
        
        return filtered_detections

    def detect_aircraft(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Specifically detect aircraft in satellite imagery
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of detected aircraft
        """
        # For aircraft detection, we might need a specialized model
        # For now, we'll use the general vehicle detector and look for specific patterns
        
        detections = self.detect_vehicles(image)
        aircraft_detections = []
        
        for detection in detections:
            # Look for objects that might be aircraft based on size and shape
            width = detection['width']
            height = detection['height']
            aspect_ratio = width / height if height > 0 else 0
            
            # Aircraft typically have specific aspect ratios and sizes
            if (aspect_ratio > 1.5 or aspect_ratio < 0.6) and (width > 50 or height > 50):
                detection['class'] = 'aircraft'
                detection['confidence'] *= 0.8  # Reduce confidence for aircraft classification
                aircraft_detections.append(detection)
        
        return aircraft_detections

    def get_detection_statistics(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Get statistics about vehicle detections in the image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Dictionary with detection statistics
        """
        detections = self.detect_vehicles(image)
        
        if not detections:
            return {
                'total_vehicles': 0,
                'vehicle_types': {},
                'average_confidence': 0,
                'detection_density': 0
            }
        
        # Count vehicle types
        vehicle_types = {}
        total_confidence = 0
        
        for detection in detections:
            vehicle_type = detection['class']
            vehicle_types[vehicle_type] = vehicle_types.get(vehicle_type, 0) + 1
            total_confidence += detection['confidence']
        
        # Calculate image area
        image_area = image.shape[0] * image.shape[1]
        detection_density = len(detections) / (image_area / 1000000)  # vehicles per megapixel
        
        return {
            'total_vehicles': len(detections),
            'vehicle_types': vehicle_types,
            'average_confidence': total_confidence / len(detections),
            'detection_density': detection_density,
            'image_dimensions': {'width': image.shape[1], 'height': image.shape[0]}
        }

