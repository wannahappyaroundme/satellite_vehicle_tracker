"""
Auto-label images using YOLOv8 Pretrained Model
Automatically generates COCO annotations for unlabeled aerial images
"""

import os
import json
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
from ultralytics import YOLO

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_DOTA = PROJECT_ROOT / "data" / "raw" / "dota" / "DOTA"
DATA_AUTO_LABELED = PROJECT_ROOT / "data" / "raw" / "auto_labeled"
DATA_AUTO_LABELED.mkdir(parents=True, exist_ok=True)

# YOLO vehicle class IDs (COCO dataset)
VEHICLE_CLASSES = {
    2: 'car',
    3: 'motorcycle',
    5: 'bus',
    7: 'truck',
}

# Map to our custom classes
CLASS_MAPPING = {
    'car': 'small-vehicle',
    'motorcycle': 'small-vehicle',
    'bus': 'large-vehicle',
    'truck': 'large-vehicle',
}

# Our custom class IDs
CUSTOM_CLASSES = {
    'small-vehicle': 1,
    'large-vehicle': 2,
}

class AutoLabeler:
    """Auto-labeling using YOLOv8"""

    def __init__(
        self,
        model_name='yolov8x.pt',  # Use largest model for best accuracy
        conf_threshold=0.5,
        iou_threshold=0.45,
        min_box_area=100,  # Minimum bbox area (pixels^2)
        max_box_area=50000,  # Maximum bbox area
        device='mps'  # 'mps' for M3 Max, 'cuda' for NVIDIA, 'cpu' for CPU
    ):
        """
        Initialize auto-labeler

        Args:
            model_name: YOLOv8 model ('yolov8n.pt', 'yolov8x.pt', etc.)
            conf_threshold: Confidence threshold (0-1)
            iou_threshold: NMS IOU threshold
            min_box_area: Minimum bbox area to filter tiny detections
            max_box_area: Maximum bbox area to filter huge detections
            device: Device to run on
        """
        print("\n" + "=" * 60)
        print("🤖 Initializing YOLOv8 Auto-Labeler")
        print("=" * 60)

        print(f"\n📦 Loading model: {model_name}")
        self.model = YOLO(model_name)

        # Configure model
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.min_box_area = min_box_area
        self.max_box_area = max_box_area
        self.device = device

        print(f"   Device: {device}")
        print(f"   Confidence threshold: {conf_threshold}")
        print(f"   IOU threshold: {iou_threshold}")
        print(f"   Bbox area range: {min_box_area} - {max_box_area} px²")
        print(f"\n✓ Model loaded successfully")

    def detect_vehicles(self, image_path):
        """
        Detect vehicles in a single image

        Returns:
            List of detections: [{'bbox': [x, y, w, h], 'class': 'small-vehicle', 'conf': 0.95}, ...]
        """
        # Read image
        img = cv2.imread(str(image_path))
        if img is None:
            return []

        # Run YOLOv8
        results = self.model.predict(
            img,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            classes=list(VEHICLE_CLASSES.keys()),  # Only detect vehicles
            device=self.device,
            verbose=False
        )

        # Parse results
        detections = []

        if len(results) > 0:
            result = results[0]

            if result.boxes is not None and len(result.boxes) > 0:
                boxes = result.boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
                confs = result.boxes.conf.cpu().numpy()
                classes = result.boxes.cls.cpu().numpy().astype(int)

                for box, conf, cls in zip(boxes, confs, classes):
                    # Convert to COCO format [x, y, width, height]
                    x1, y1, x2, y2 = box
                    x, y = x1, y1
                    w, h = x2 - x1, y2 - y1

                    # Filter by area
                    area = w * h
                    if area < self.min_box_area or area > self.max_box_area:
                        continue

                    # Map to our custom classes
                    yolo_class = VEHICLE_CLASSES.get(cls, None)
                    if yolo_class is None:
                        continue

                    custom_class = CLASS_MAPPING.get(yolo_class, None)
                    if custom_class is None:
                        continue

                    detections.append({
                        'bbox': [float(x), float(y), float(w), float(h)],
                        'class': custom_class,
                        'confidence': float(conf),
                        'yolo_class': yolo_class
                    })

        return detections

    def label_directory(self, input_dir, output_dir=None, dataset_name="auto_labeled"):
        """
        Auto-label all images in a directory

        Args:
            input_dir: Directory containing images
            output_dir: Output directory (default: data/raw/auto_labeled)
            dataset_name: Dataset name for COCO info
        """
        input_dir = Path(input_dir)
        if output_dir is None:
            output_dir = DATA_AUTO_LABELED
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        print("\n" + "=" * 60)
        print(f"🏷️  Auto-labeling: {input_dir.name}")
        print("=" * 60)

        # Find all images
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        image_files = []

        for ext in image_extensions:
            image_files.extend(input_dir.rglob(f"*{ext}"))
            image_files.extend(input_dir.rglob(f"*{ext.upper()}"))

        print(f"\n📸 Found {len(image_files)} images")

        if len(image_files) == 0:
            print("⚠️  No images found!")
            return False

        # Initialize COCO format
        coco_data = {
            "info": {
                "description": f"Auto-labeled Dataset - {dataset_name}",
                "url": "",
                "version": "1.0",
                "year": datetime.now().year,
                "contributor": "YOLOv8 Auto-Labeler",
                "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "licenses": [],
            "images": [],
            "annotations": [],
            "categories": [
                {
                    "id": 1,
                    "name": "small-vehicle",
                    "supercategory": "vehicle"
                },
                {
                    "id": 2,
                    "name": "large-vehicle",
                    "supercategory": "vehicle"
                }
            ]
        }

        # Process each image
        annotation_id = 1
        image_id = 1
        total_vehicles = 0

        # Create images output directory
        images_output_dir = output_dir / "images"
        images_output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n🔍 Processing images...")
        print(f"   Saving to: {output_dir}/")

        for image_path in tqdm(image_files, desc="Auto-labeling"):
            # Detect vehicles
            detections = self.detect_vehicles(image_path)

            if len(detections) == 0:
                continue  # Skip images with no detections

            # Read image to get dimensions
            img = cv2.imread(str(image_path))
            if img is None:
                continue

            height, width = img.shape[:2]

            # Copy image to output directory
            output_image_path = images_output_dir / image_path.name
            if not output_image_path.exists():
                import shutil
                shutil.copy2(image_path, output_image_path)

            # Add image to COCO
            coco_data["images"].append({
                "id": image_id,
                "file_name": image_path.name,
                "width": width,
                "height": height
            })

            # Add annotations
            for detection in detections:
                bbox = detection['bbox']
                category_name = detection['class']
                category_id = CUSTOM_CLASSES[category_name]

                coco_data["annotations"].append({
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": category_id,
                    "bbox": bbox,
                    "area": bbox[2] * bbox[3],
                    "iscrowd": 0,
                    "confidence": detection['confidence']
                })

                annotation_id += 1
                total_vehicles += 1

            image_id += 1

        # Save COCO JSON
        annotations_path = output_dir / "annotations.json"
        with open(annotations_path, 'w') as f:
            json.dump(coco_data, f, indent=2)

        # Summary
        print("\n" + "=" * 60)
        print("📊 Auto-labeling Results")
        print("=" * 60)
        print(f"\n✓ Images with detections: {len(coco_data['images'])}")
        print(f"✓ Total vehicles detected: {total_vehicles}")
        print(f"✓ Average vehicles per image: {total_vehicles / len(coco_data['images']):.1f}")

        # Class distribution
        class_counts = {}
        for ann in coco_data['annotations']:
            cat_id = ann['category_id']
            cat_name = next(c['name'] for c in coco_data['categories'] if c['id'] == cat_id)
            class_counts[cat_name] = class_counts.get(cat_name, 0) + 1

        print(f"\n📈 Class Distribution:")
        for class_name, count in sorted(class_counts.items()):
            percentage = count / total_vehicles * 100
            print(f"   {class_name}: {count} ({percentage:.1f}%)")

        # Confidence distribution
        confidences = [ann['confidence'] for ann in coco_data['annotations']]
        avg_conf = np.mean(confidences)
        min_conf = np.min(confidences)
        max_conf = np.max(confidences)

        print(f"\n🎯 Confidence Statistics:")
        print(f"   Average: {avg_conf:.3f}")
        print(f"   Min: {min_conf:.3f}")
        print(f"   Max: {max_conf:.3f}")

        print(f"\n💾 Saved to:")
        print(f"   Images: {images_output_dir}/")
        print(f"   Annotations: {annotations_path}")

        return True

def label_dota_dataset(split='train'):
    """Auto-label DOTA dataset (train/val/test splits)"""

    split_dir = DATA_RAW_DOTA / split / "images"

    if not split_dir.exists():
        print(f"\n❌ DOTA {split} split not found: {split_dir}")
        return False

    # Initialize auto-labeler
    labeler = AutoLabeler(
        model_name='yolov8x.pt',  # Largest model for best accuracy
        conf_threshold=0.5,  # Moderate threshold
        device='mps'  # M3 Max GPU
    )

    # Label the split
    output_dir = DATA_AUTO_LABELED / f"dota_{split}"
    labeler.label_directory(
        input_dir=split_dir,
        output_dir=output_dir,
        dataset_name=f"DOTA-{split.upper()}"
    )

    return True

def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Auto-label aerial images with YOLOv8')
    parser.add_argument(
        '--input',
        type=str,
        help='Input directory containing images'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output directory for labeled dataset'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='yolov8x.pt',
        choices=['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt'],
        help='YOLOv8 model size'
    )
    parser.add_argument(
        '--conf',
        type=float,
        default=0.5,
        help='Confidence threshold (0-1)'
    )
    parser.add_argument(
        '--dota',
        action='store_true',
        help='Auto-label DOTA dataset (train/val/test splits)'
    )
    parser.add_argument(
        '--device',
        type=str,
        default='mps',
        choices=['mps', 'cuda', 'cpu'],
        help='Device to run on'
    )

    args = parser.parse_args()

    if args.dota:
        # Label all DOTA splits
        print("\n🚀 Auto-labeling DOTA dataset...")

        for split in ['train', 'val', 'test']:
            print(f"\n{'='*60}")
            print(f"Processing DOTA {split.upper()} split")
            print(f"{'='*60}")

            if label_dota_dataset(split):
                print(f"✓ Successfully labeled DOTA {split} split")
            else:
                print(f"⚠️  Skipped DOTA {split} split (not found)")

        print("\n" + "=" * 60)
        print("✅ DOTA Auto-labeling Complete!")
        print("=" * 60)

    elif args.input:
        # Label custom directory
        labeler = AutoLabeler(
            model_name=args.model,
            conf_threshold=args.conf,
            device=args.device
        )

        labeler.label_directory(
            input_dir=args.input,
            output_dir=args.output,
            dataset_name=Path(args.input).name
        )

    else:
        print("\n⚠️  Please specify --input or --dota")
        print("\nExamples:")
        print("  # Label custom directory")
        print("  python scripts/auto_label_with_yolo.py --input /path/to/images --output /path/to/output")
        print()
        print("  # Label DOTA dataset")
        print("  python scripts/auto_label_with_yolo.py --dota")

if __name__ == "__main__":
    main()
