"""
Data Preprocessing Pipeline
Converts DOTA/AI Hub data to COCO format and splits into train/val/test sets
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List
import random
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_TRAIN = PROJECT_ROOT / "data" / "train"
DATA_VAL = PROJECT_ROOT / "data" / "val"
DATA_TEST = PROJECT_ROOT / "data" / "test"

# Vehicle classes mapping
# DOTA classes → Our unified classes
CLASS_MAPPING = {
    "small-vehicle": 1,
    "large-vehicle": 2,
    "car": 1,  # Maps to small-vehicle
    "truck": 2,  # Maps to large-vehicle
    "bus": 2,  # Maps to large-vehicle
    "vehicle": 1,  # Generic vehicle → small
}

CLASSES = {
    0: "background",
    1: "small-vehicle",
    2: "large-vehicle"
}

def parse_dota_annotation(label_file: Path) -> List[Dict]:
    """
    Parse DOTA annotation format

    DOTA format (labelTxt):
    x1 y1 x2 y2 x3 y3 x4 y4 class difficulty

    Returns:
        List of bounding boxes with class and difficulty
    """
    annotations = []

    if not label_file.exists():
        return annotations

    with open(label_file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith('imagesource') or line.startswith('gsd'):
            continue

        parts = line.split()
        if len(parts) < 9:
            continue

        try:
            # Parse coordinates (8 points for oriented bbox)
            x1, y1, x2, y2, x3, y3, x4, y4 = map(float, parts[:8])
            class_name = parts[8].lower()
            difficulty = int(parts[9]) if len(parts) > 9 else 0

            # Map class name
            if class_name not in CLASS_MAPPING:
                continue

            class_id = CLASS_MAPPING[class_name]

            # Convert oriented bbox to axis-aligned bbox (COCO format)
            x_coords = [x1, x2, x3, x4]
            y_coords = [y1, y2, y3, y4]

            x_min = min(x_coords)
            y_min = min(y_coords)
            x_max = max(x_coords)
            y_max = max(y_coords)

            width = x_max - x_min
            height = y_max - y_min

            # Filter out invalid boxes
            if width <= 0 or height <= 0:
                continue

            annotations.append({
                "bbox": [x_min, y_min, width, height],  # COCO format: [x, y, w, h]
                "category_id": class_id,
                "difficulty": difficulty,
                "area": width * height,
                "iscrowd": 0
            })

        except Exception as e:
            print(f"Error parsing line: {line[:50]}... - {e}")
            continue

    return annotations

def create_coco_dataset(image_files: List[Path], output_path: Path, split_name: str):
    """
    Create COCO format JSON from DOTA annotations

    COCO format:
    {
        "images": [...],
        "annotations": [...],
        "categories": [...]
    }
    """
    coco_data = {
        "info": {
            "description": f"Korean Aerial Vehicle Detection - {split_name}",
            "version": "1.0",
            "year": 2025,
            "date_created": datetime.now().isoformat()
        },
        "images": [],
        "annotations": [],
        "categories": [
            {"id": 1, "name": "small-vehicle", "supercategory": "vehicle"},
            {"id": 2, "name": "large-vehicle", "supercategory": "vehicle"}
        ]
    }

    annotation_id = 1

    for image_id, image_file in enumerate(image_files, start=1):
        # Image info
        try:
            from PIL import Image
            with Image.open(image_file) as img:
                width, height = img.size
        except Exception:
            # Default size if image can't be opened
            width, height = 1024, 1024

        image_info = {
            "id": image_id,
            "file_name": image_file.name,
            "width": width,
            "height": height
        }
        coco_data["images"].append(image_info)

        # Annotations
        label_dir = image_file.parent.parent / "labels"
        label_file = label_dir / f"{image_file.stem}.txt"

        annotations = parse_dota_annotation(label_file)

        for ann in annotations:
            ann["id"] = annotation_id
            ann["image_id"] = image_id
            coco_data["annotations"].append(ann)
            annotation_id += 1

    # Save COCO JSON
    with open(output_path, 'w') as f:
        json.dump(coco_data, f, indent=2)

    return coco_data

def split_dataset(images_dir: Path, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1, seed=42):
    """
    Split dataset into train/val/test sets

    Args:
        images_dir: Directory containing all images
        train_ratio: Training set ratio (default: 0.7)
        val_ratio: Validation set ratio (default: 0.2)
        test_ratio: Test set ratio (default: 0.1)
        seed: Random seed for reproducibility
    """
    # Get all image files
    image_extensions = ['.png', '.jpg', '.jpeg', '.tif', '.tiff']
    all_images = []
    for ext in image_extensions:
        all_images.extend(images_dir.glob(f"*{ext}"))

    if not all_images:
        print(f"❌ No images found in {images_dir}")
        return None, None, None

    # Shuffle
    random.seed(seed)
    random.shuffle(all_images)

    # Split
    total = len(all_images)
    train_end = int(total * train_ratio)
    val_end = int(total * (train_ratio + val_ratio))

    train_images = all_images[:train_end]
    val_images = all_images[train_end:val_end]
    test_images = all_images[val_end:]

    print(f"\n📊 데이터셋 분할:")
    print(f"   Train: {len(train_images):,}장 ({len(train_images)/total*100:.1f}%)")
    print(f"   Val:   {len(val_images):,}장 ({len(val_images)/total*100:.1f}%)")
    print(f"   Test:  {len(test_images):,}장 ({len(test_images)/total*100:.1f}%)")

    return train_images, val_images, test_images

def copy_images_and_labels(image_files: List[Path], target_dir: Path):
    """Copy images and labels to target directory"""
    target_images_dir = target_dir / "images"
    target_labels_dir = target_dir / "labels"

    target_images_dir.mkdir(parents=True, exist_ok=True)
    target_labels_dir.mkdir(parents=True, exist_ok=True)

    for img_file in image_files:
        # Copy image
        target_img = target_images_dir / img_file.name
        if not target_img.exists():
            shutil.copy2(img_file, target_img)

        # Copy label
        label_dir = img_file.parent.parent / "labels"
        label_file = label_dir / f"{img_file.stem}.txt"

        if label_file.exists():
            target_label = target_labels_dir / label_file.name
            if not target_label.exists():
                shutil.copy2(label_file, target_label)

def main():
    """Main preprocessing pipeline"""
    print("\n" + "=" * 60)
    print("🔧 데이터 전처리 시작")
    print("=" * 60)

    # Check if processed data exists
    images_dir = DATA_PROCESSED / "images"
    if not images_dir.exists() or not list(images_dir.glob("*.*")):
        print("\n❌ 처리된 데이터가 없습니다!")
        print("📂 확인 경로:", images_dir)
        print("\n💡 먼저 다음 스크립트를 실행하세요:")
        print("   python scripts/filter_korea_region.py")
        return

    # Split dataset
    print("\n📁 데이터셋 분할 중...")
    train_images, val_images, test_images = split_dataset(images_dir)

    if not train_images:
        return

    # Copy images and labels to split directories
    print("\n📋 파일 복사 중...")
    copy_images_and_labels(train_images, DATA_TRAIN)
    copy_images_and_labels(val_images, DATA_VAL)
    copy_images_and_labels(test_images, DATA_TEST)

    # Create COCO format annotations
    print("\n🔄 COCO format 변환 중...")

    train_coco = create_coco_dataset(
        list((DATA_TRAIN / "images").glob("*.*")),
        DATA_TRAIN / "annotations.json",
        "train"
    )

    val_coco = create_coco_dataset(
        list((DATA_VAL / "images").glob("*.*")),
        DATA_VAL / "annotations.json",
        "val"
    )

    test_coco = create_coco_dataset(
        list((DATA_TEST / "images").glob("*.*")),
        DATA_TEST / "annotations.json",
        "test"
    )

    # Statistics
    print("\n" + "=" * 60)
    print("📊 전처리 완료")
    print("=" * 60)
    print(f"\nTrain Set:")
    print(f"   Images: {len(train_coco['images']):,}장")
    print(f"   Annotations: {len(train_coco['annotations']):,}개")
    print(f"\nVal Set:")
    print(f"   Images: {len(val_coco['images']):,}장")
    print(f"   Annotations: {len(val_coco['annotations']):,}개")
    print(f"\nTest Set:")
    print(f"   Images: {len(test_coco['images']):,}장")
    print(f"   Annotations: {len(test_coco['annotations']):,}개")

    # Class distribution
    train_classes = {}
    for ann in train_coco['annotations']:
        cid = ann['category_id']
        train_classes[cid] = train_classes.get(cid, 0) + 1

    print(f"\n클래스 분포 (Train):")
    for cid, count in train_classes.items():
        class_name = CLASSES[cid]
        print(f"   {class_name}: {count:,}개 ({count/len(train_coco['annotations'])*100:.1f}%)")

    # Calculate total size
    total_size = 0
    for data_dir in [DATA_TRAIN, DATA_VAL, DATA_TEST]:
        for f in data_dir.glob("**/*"):
            if f.is_file():
                total_size += f.stat().st_size

    print(f"\n💾 총 데이터 크기: {total_size / (1024**3):.2f} GB")

    print("\n" + "=" * 60)
    print("✅ 다음 단계: 모델 학습")
    print("=" * 60)
    print("\n실행:")
    print("   python scripts/train.py --config configs/cascade_rcnn_swin.py")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
