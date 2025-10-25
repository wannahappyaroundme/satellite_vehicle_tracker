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
        
        # Vehicle classes for abandoned vehicle detection (COCO dataset)
        # 프로젝트 목표: 승합차/승용차 우선, 트럭/버스 포함, 기타 제외
        self.vehicle_classes = {
            2: 'car',     # 승합차/승용차 (우선순위)
            5: 'bus',     # 버스
            7: 'truck',   # 트럭
        }

        # 차량 검증 기준
        self.MIN_VEHICLE_AREA = 400        # 20x20 최소 크기 (픽셀²)
        self.MAX_VEHICLE_AREA = 50000      # 너무 크면 건물일 가능성
        self.MIN_ASPECT_RATIO = 0.5        # 너무 세로로 길면 차량 아님
        self.MAX_ASPECT_RATIO = 4.0        # 너무 가로로 길면 차량 아님
        self.MIN_VEHICLE_CONFIDENCE = 0.6  # 차량 최소 신뢰도 (0.5 → 0.6으로 강화)

    def is_valid_vehicle(self, detection: Dict[str, Any]) -> bool:
        """
        차량 검증 로직: 감지된 객체가 실제 차량인지 확인

        검증 기준:
        1. 크기: 400-50000 픽셀² (너무 작거나 큰 것 제외)
        2. 종횡비: 0.5-4.0 (비정상적 형태 제외)
        3. 신뢰도: 0.6 이상 (낮은 확신도 제외)
        4. 타입: car/truck/bus만 허용

        Args:
            detection: 감지된 객체 정보

        Returns:
            bool: 유효한 차량이면 True, 아니면 False
        """
        # 크기 검증
        width = detection.get('width', 0)
        height = detection.get('height', 0)
        area = width * height

        if area < self.MIN_VEHICLE_AREA or area > self.MAX_VEHICLE_AREA:
            return False

        # 종횡비 검증
        aspect_ratio = width / height if height > 0 else 0
        if aspect_ratio < self.MIN_ASPECT_RATIO or aspect_ratio > self.MAX_ASPECT_RATIO:
            return False

        # 신뢰도 검증
        confidence = detection.get('confidence', 0)
        if confidence < self.MIN_VEHICLE_CONFIDENCE:
            return False

        # 타입 검증 (car, truck, bus만 허용)
        vehicle_type = detection.get('class', '')
        if vehicle_type not in ['car', 'truck', 'bus']:
            return False

        return True

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

                            # 차량 검증 로직 적용
                            if self.is_valid_vehicle(detection):
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

