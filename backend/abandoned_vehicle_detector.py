"""
Abandoned Vehicle Detection System
Uses ResNet feature extraction and cosine similarity to detect vehicles
that haven't moved between two aerial photo captures (year-over-year comparison)
"""

import cv2
import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from typing import List, Dict, Tuple, Any
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache
import hashlib
import rasterio
from rasterio.mask import mask
from shapely.geometry import box, mapping
import json


class AbandonedVehicleDetector:
    """
    Detects abandoned vehicles by comparing aerial photos from different years
    using ResNet feature extraction and cosine similarity
    """

    def __init__(self, similarity_threshold: float = 0.90):
        """
        Initialize the abandoned vehicle detector

        Args:
            similarity_threshold: Minimum cosine similarity (0-1) to consider a vehicle as abandoned
                                 Default 0.90 (90%) as per requirements
        """
        self.similarity_threshold = similarity_threshold

        # Load pre-trained ResNet model (ResNet50 for better feature extraction)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = models.resnet50(pretrained=True)

        # Remove the final classification layer to get feature vectors
        self.model = torch.nn.Sequential(*list(self.model.children())[:-1])
        self.model = self.model.to(self.device)
        self.model.eval()

        # Image preprocessing pipeline
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        # Feature extraction cache (LRU cache for performance optimization)
        self._feature_cache = {}
        self._cache_max_size = 100  # 최대 100개 이미지 캐싱

    def _get_image_hash(self, image: np.ndarray) -> str:
        """
        이미지의 해시값 계산 (캐싱용)

        Args:
            image: 입력 이미지

        Returns:
            이미지 해시값 (MD5)
        """
        return hashlib.md5(image.tobytes()).hexdigest()

    def extract_features(self, image: np.ndarray, use_cache: bool = True) -> np.ndarray:
        """
        Extract feature vector from vehicle image using ResNet

        🚀 성능 최적화: LRU 캐시 적용 (동일 이미지 재분석 시 속도 향상)

        Args:
            image: Input image as numpy array (BGR or RGB)
            use_cache: 캐시 사용 여부 (기본값: True)

        Returns:
            Feature vector as 1D numpy array (2048 dimensions for ResNet50)
        """
        # 캐시 확인 (동일 이미지 재분석 시 캐시 사용)
        if use_cache:
            image_hash = self._get_image_hash(image)
            if image_hash in self._feature_cache:
                return self._feature_cache[image_hash]

        # Convert BGR to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image

        # Convert to PIL Image
        pil_image = Image.fromarray(image_rgb)

        # Apply preprocessing
        input_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)

        # Extract features
        with torch.no_grad():
            features = self.model(input_tensor)

        # Flatten and convert to numpy
        features = features.squeeze().cpu().numpy()

        # 캐시 저장 (LRU 방식: 오래된 항목 자동 삭제)
        if use_cache:
            if len(self._feature_cache) >= self._cache_max_size:
                # 가장 오래된 항목 삭제 (FIFO)
                oldest_key = next(iter(self._feature_cache))
                del self._feature_cache[oldest_key]
            self._feature_cache[image_hash] = features

        return features

    def calculate_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two feature vectors

        Args:
            features1: First feature vector
            features2: Second feature vector

        Returns:
            Cosine similarity score (0-1)
        """
        # Reshape for sklearn cosine_similarity
        feat1 = features1.reshape(1, -1)
        feat2 = features2.reshape(1, -1)

        similarity = cosine_similarity(feat1, feat2)[0][0]

        return float(similarity)

    def crop_parking_space(
        self,
        geotiff_path: str,
        parking_geojson: Dict[str, Any]
    ) -> np.ndarray:
        """
        Crop parking space from GeoTIFF using GeoJSON coordinates

        Args:
            geotiff_path: Path to GeoTIFF aerial photo
            parking_geojson: GeoJSON feature containing parking space polygon

        Returns:
            Cropped image as numpy array
        """
        with rasterio.open(geotiff_path) as src:
            # Extract geometry from GeoJSON
            geometry = parking_geojson['geometry']

            # Crop the image
            out_image, out_transform = mask(src, [geometry], crop=True)

            # Convert to numpy array (channels last)
            out_image = np.transpose(out_image, (1, 2, 0))

            # Convert to uint8 if needed
            if out_image.dtype != np.uint8:
                out_image = (out_image / out_image.max() * 255).astype(np.uint8)

            return out_image

    def detect_abandoned_vehicles(
        self,
        image_year1: np.ndarray,
        image_year2: np.ndarray,
        year1: int,
        year2: int,
        parking_space_id: str = None
    ) -> Dict[str, Any]:
        """
        Compare two vehicle images from different years to detect if abandoned

        Args:
            image_year1: Vehicle/parking space image from first year
            image_year2: Vehicle/parking space image from second year
            year1: First year (e.g., 2015)
            year2: Second year (e.g., 2020)
            parking_space_id: Optional identifier for the parking space

        Returns:
            Detection result with similarity score and abandoned status
        """
        # Extract features from both images
        features1 = self.extract_features(image_year1)
        features2 = self.extract_features(image_year2)

        # Calculate similarity
        similarity = self.calculate_similarity(features1, features2)

        # Determine if vehicle is abandoned (similarity >= threshold)
        is_abandoned = similarity >= self.similarity_threshold

        # Calculate years difference
        years_difference = year2 - year1

        result = {
            'parking_space_id': parking_space_id,
            'year1': year1,
            'year2': year2,
            'years_difference': years_difference,
            'similarity_score': round(similarity, 4),
            'similarity_percentage': round(similarity * 100, 2),
            'threshold': self.similarity_threshold,
            'is_abandoned': is_abandoned,
            'risk_level': self._calculate_risk_level(similarity, years_difference),
            'status': 'ABANDONED_SUSPECTED' if is_abandoned else 'NORMAL'
        }

        return result

    def _calculate_risk_level(self, similarity: float, years_difference: int) -> str:
        """
        Calculate risk level based on similarity and time difference

        Args:
            similarity: Cosine similarity score
            years_difference: Number of years between photos

        Returns:
            Risk level: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
        """
        if similarity >= 0.95 and years_difference >= 3:
            return 'CRITICAL'
        elif similarity >= 0.90 and years_difference >= 2:
            return 'HIGH'
        elif similarity >= 0.85:
            return 'MEDIUM'
        else:
            return 'LOW'

    def batch_detect_abandoned_vehicles(
        self,
        parking_spaces: List[Dict[str, Any]],
        geotiff_year1: str,
        geotiff_year2: str,
        year1: int,
        year2: int
    ) -> List[Dict[str, Any]]:
        """
        Batch process multiple parking spaces from GeoTIFF files

        Args:
            parking_spaces: List of GeoJSON parking space features
            geotiff_year1: Path to first year GeoTIFF
            geotiff_year2: Path to second year GeoTIFF
            year1: First year
            year2: Second year

        Returns:
            List of detection results for all parking spaces
        """
        results = []

        for i, parking_space in enumerate(parking_spaces):
            try:
                # Crop images for this parking space
                image1 = self.crop_parking_space(geotiff_year1, parking_space)
                image2 = self.crop_parking_space(geotiff_year2, parking_space)

                # Get parking space ID from properties or use index
                space_id = parking_space.get('properties', {}).get('id', f'space_{i}')

                # Detect abandoned vehicle
                result = self.detect_abandoned_vehicles(
                    image1, image2, year1, year2, space_id
                )

                # Add geometry information
                result['geometry'] = parking_space['geometry']
                result['properties'] = parking_space.get('properties', {})

                results.append(result)

            except Exception as e:
                print(f"Error processing parking space {i}: {str(e)}")
                continue

        return results

    def compare_pdf_images(
        self,
        pdf_image1: np.ndarray,
        pdf_image2: np.ndarray,
        year1: int,
        year2: int,
        bounding_boxes: List[Tuple[int, int, int, int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Compare vehicles in two PDF-extracted images
        If bounding boxes provided, compare specific regions
        Otherwise, compare whole images

        Args:
            pdf_image1: Image from first PDF (numpy array)
            pdf_image2: Image from second PDF (numpy array)
            year1: First year
            year2: Second year
            bounding_boxes: Optional list of (x, y, w, h) bounding boxes for vehicle locations

        Returns:
            List of detection results
        """
        results = []

        if bounding_boxes is None:
            # Compare whole images
            result = self.detect_abandoned_vehicles(
                pdf_image1, pdf_image2, year1, year2, 'full_image'
            )
            results.append(result)
        else:
            # Compare specific regions
            for i, (x, y, w, h) in enumerate(bounding_boxes):
                try:
                    # Crop regions from both images
                    crop1 = pdf_image1[y:y+h, x:x+w]
                    crop2 = pdf_image2[y:y+h, x:x+w]

                    result = self.detect_abandoned_vehicles(
                        crop1, crop2, year1, year2, f'vehicle_{i}'
                    )

                    # Add bounding box info
                    result['bbox'] = {'x': x, 'y': y, 'w': w, 'h': h}

                    results.append(result)
                except Exception as e:
                    print(f"Error processing bounding box {i}: {str(e)}")
                    continue

        return results

    def filter_abandoned_vehicles(
        self,
        results: List[Dict[str, Any]],
        min_years: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Filter results to only show abandoned vehicles

        Args:
            results: List of detection results
            min_years: Minimum years difference to consider

        Returns:
            Filtered list of abandoned vehicles only
        """
        abandoned = [
            r for r in results
            if r['is_abandoned'] and r['years_difference'] >= min_years
        ]

        # Sort by similarity score (highest first - most suspicious)
        abandoned.sort(key=lambda x: x['similarity_score'], reverse=True)

        return abandoned
