"""
Merge All Datasets into Single COCO Dataset
Combines Roboflow, Kaggle, auto-labeled, and manual datasets
"""

import json
import shutil
import hashlib
import random
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from tqdm import tqdm
import cv2
import numpy as np

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_FINAL = PROJECT_ROOT / "data"
DATA_TRAIN = DATA_FINAL / "train"
DATA_VAL = DATA_FINAL / "val"
DATA_TEST = DATA_FINAL / "test"

# Class mapping - map all variants to our 2 classes
CLASS_MAPPING = {
    # Small vehicles
    'car': 'small-vehicle',
    'vehicle': 'small-vehicle',
    'small-vehicle': 'small-vehicle',
    'sedan': 'small-vehicle',
    'suv': 'small-vehicle',
    'motorcycle': 'small-vehicle',
    'motorbike': 'small-vehicle',
    'bike': 'small-vehicle',

    # Large vehicles
    'truck': 'large-vehicle',
    'large-vehicle': 'large-vehicle',
    'bus': 'large-vehicle',
    'van': 'large-vehicle',
    'lorry': 'large-vehicle',
    'trailer': 'large-vehicle',

    # Aircraft (skip - not vehicle)
    'plane': None,
    'helicopter': None,
    'aircraft': None,

    # Other (skip)
    'ship': None,
    'boat': None,
    'person': None,
    'human': None,
}

# Our target classes
TARGET_CLASSES = {
    'small-vehicle': 1,
    'large-vehicle': 2,
}

class DatasetMerger:
    """Merge multiple COCO datasets into one"""

    def __init__(self):
        self.merged_data = {
            "info": {
                "description": "Korean Aerial Vehicle Detection - Merged Dataset",
                "url": "",
                "version": "2.0",
                "year": datetime.now().year,
                "contributor": "Multiple sources (Roboflow, Kaggle, Auto-labeled, Manual)",
                "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "licenses": [],
            "images": [],
            "annotations": [],
            "categories": [
                {"id": 1, "name": "small-vehicle", "supercategory": "vehicle"},
                {"id": 2, "name": "large-vehicle", "supercategory": "vehicle"}
            ]
        }

        self.image_id_counter = 1
        self.annotation_id_counter = 1
        self.image_hashes = {}  # For duplicate detection
        self.stats = defaultdict(int)

    def compute_image_hash(self, image_path):
        """Compute hash of image for duplicate detection"""
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return None

            # Resize to small size for faster hashing
            img_small = cv2.resize(img, (64, 64))
            img_bytes = img_small.tobytes()

            return hashlib.md5(img_bytes).hexdigest()
        except Exception as e:
            print(f"⚠️  Error hashing {image_path}: {e}")
            return None

    def load_coco_dataset(self, coco_json_path, images_dir):
        """
        Load a COCO format dataset

        Returns:
            List of (image_info, annotations) tuples
        """
        if not coco_json_path.exists():
            return []

        with open(coco_json_path, 'r') as f:
            data = json.load(f)

        # Build category ID mapping
        cat_id_to_name = {}
        if 'categories' in data:
            for cat in data['categories']:
                cat_id_to_name[cat['id']] = cat['name'].lower()

        # Build image ID to annotations mapping
        image_to_anns = defaultdict(list)
        if 'annotations' in data:
            for ann in data['annotations']:
                image_to_anns[ann['image_id']].append(ann)

        # Process images
        result = []
        for img_info in data.get('images', []):
            image_id = img_info['id']
            file_name = img_info['file_name']

            # Find image file
            image_path = images_dir / file_name
            if not image_path.exists():
                # Try subdirectories
                found = list(images_dir.rglob(file_name))
                if found:
                    image_path = found[0]
                else:
                    continue

            # Get annotations
            anns = image_to_anns.get(image_id, [])

            # Map annotations to our classes
            mapped_anns = []
            for ann in anns:
                cat_id = ann['category_id']
                cat_name = cat_id_to_name.get(cat_id, '').lower()

                # Map to our classes
                mapped_class = CLASS_MAPPING.get(cat_name, None)
                if mapped_class is None:
                    continue  # Skip non-vehicle classes

                new_ann = ann.copy()
                new_ann['category_name'] = mapped_class
                new_ann['category_id'] = TARGET_CLASSES[mapped_class]
                mapped_anns.append(new_ann)

            if mapped_anns:  # Only include images with valid annotations
                result.append((img_info, mapped_anns, image_path))

        return result

    def add_dataset(self, dataset_name, coco_json_path, images_dir):
        """Add a dataset to the merged dataset"""

        print(f"\n{'='*60}")
        print(f"📦 Adding Dataset: {dataset_name}")
        print(f"{'='*60}")
        print(f"   JSON: {coco_json_path}")
        print(f"   Images: {images_dir}")

        # Load dataset
        dataset = self.load_coco_dataset(coco_json_path, images_dir)

        if not dataset:
            print(f"   ⚠️  No valid images found")
            return 0

        print(f"   Found {len(dataset)} images with annotations")

        # Add to merged dataset
        added_images = 0
        added_annotations = 0
        skipped_duplicates = 0

        for img_info, annotations, image_path in tqdm(dataset, desc=f"  Merging"):
            # Check for duplicates
            img_hash = self.compute_image_hash(image_path)
            if img_hash and img_hash in self.image_hashes:
                skipped_duplicates += 1
                continue

            # Add image
            new_image_info = {
                "id": self.image_id_counter,
                "file_name": image_path.name,
                "width": img_info['width'],
                "height": img_info['height'],
                "source": dataset_name
            }

            self.merged_data['images'].append(new_image_info)

            if img_hash:
                self.image_hashes[img_hash] = self.image_id_counter

            # Add annotations
            for ann in annotations:
                new_ann = {
                    "id": self.annotation_id_counter,
                    "image_id": self.image_id_counter,
                    "category_id": ann['category_id'],
                    "bbox": ann['bbox'],
                    "area": ann.get('area', ann['bbox'][2] * ann['bbox'][3]),
                    "iscrowd": ann.get('iscrowd', 0)
                }

                self.merged_data['annotations'].append(new_ann)

                # Update stats
                cat_name = ann['category_name']
                self.stats[f"{dataset_name}_{cat_name}"] += 1
                self.annotation_id_counter += 1
                added_annotations += 1

            added_images += 1
            self.image_id_counter += 1

        print(f"\n   ✓ Added: {added_images} images, {added_annotations} annotations")
        if skipped_duplicates > 0:
            print(f"   ⏭️  Skipped: {skipped_duplicates} duplicates")

        return added_images

    def split_dataset(self, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1, seed=42):
        """Split merged dataset into train/val/test"""

        print(f"\n{'='*60}")
        print("📊 Splitting Dataset")
        print(f"{'='*60}")

        random.seed(seed)

        # Group annotations by image_id
        image_to_anns = defaultdict(list)
        for ann in self.merged_data['annotations']:
            image_to_anns[ann['image_id']].append(ann)

        # Shuffle images
        images = self.merged_data['images'].copy()
        random.shuffle(images)

        # Split
        total = len(images)
        train_end = int(total * train_ratio)
        val_end = int(total * (train_ratio + val_ratio))

        splits = {
            'train': images[:train_end],
            'val': images[train_end:val_end],
            'test': images[val_end:]
        }

        print(f"\n   Total images: {total}")
        print(f"   Train: {len(splits['train'])} ({len(splits['train'])/total*100:.1f}%)")
        print(f"   Val: {len(splits['val'])} ({len(splits['val'])/total*100:.1f}%)")
        print(f"   Test: {len(splits['test'])} ({len(splits['test'])/total*100:.1f}%)")

        return splits, image_to_anns

    def save_split(self, split_name, split_images, image_to_anns, output_dir):
        """Save a dataset split"""

        output_dir.mkdir(parents=True, exist_ok=True)
        images_dir = output_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        # Create split dataset
        split_data = {
            "info": self.merged_data['info'].copy(),
            "images": [],
            "annotations": [],
            "categories": self.merged_data['categories']
        }
        split_data['info']['description'] += f" - {split_name.upper()}"

        # Copy images and annotations
        for img_info in tqdm(split_images, desc=f"  Saving {split_name}"):
            # Add image info
            split_data['images'].append(img_info)

            # Add annotations
            anns = image_to_anns.get(img_info['id'], [])
            split_data['annotations'].extend(anns)

            # Note: Images are not copied here to save disk space
            # They should already be in data/raw directories
            # If you want to copy them, uncomment below:
            # source_path = ... (find original image)
            # dest_path = images_dir / img_info['file_name']
            # shutil.copy2(source_path, dest_path)

        # Save annotations
        ann_path = output_dir / "annotations.json"
        with open(ann_path, 'w') as f:
            json.dump(split_data, f, indent=2)

        print(f"   ✓ Saved {split_name}: {len(split_data['images'])} images, {len(split_data['annotations'])} annotations")
        print(f"      Location: {output_dir}/")

        return split_data

    def print_statistics(self):
        """Print dataset statistics"""

        print(f"\n{'='*60}")
        print("📈 Dataset Statistics")
        print(f"{'='*60}")

        # Overall stats
        print(f"\n🖼️  Total Images: {len(self.merged_data['images'])}")
        print(f"🏷️  Total Annotations: {len(self.merged_data['annotations'])}")

        # Class distribution
        class_counts = defaultdict(int)
        for ann in self.merged_data['annotations']:
            cat_id = ann['category_id']
            cat_name = next(c['name'] for c in self.merged_data['categories'] if c['id'] == cat_id)
            class_counts[cat_name] += 1

        print(f"\n📊 Class Distribution:")
        for class_name in sorted(class_counts.keys()):
            count = class_counts[class_name]
            percentage = count / len(self.merged_data['annotations']) * 100
            print(f"   {class_name}: {count} ({percentage:.1f}%)")

        # Source distribution
        print(f"\n📁 Sources:")
        source_counts = defaultdict(int)
        for img in self.merged_data['images']:
            source = img.get('source', 'unknown')
            source_counts[source] += 1

        for source in sorted(source_counts.keys()):
            count = source_counts[source]
            percentage = count / len(self.merged_data['images']) * 100
            print(f"   {source}: {count} images ({percentage:.1f}%)")

def main():
    """Main execution"""

    print("\n" + "=" * 60)
    print("🔗 Merging All Datasets")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    merger = DatasetMerger()

    # 1. Add Roboflow datasets
    roboflow_dir = DATA_RAW / "roboflow"
    if roboflow_dir.exists():
        for dataset_dir in roboflow_dir.iterdir():
            if dataset_dir.is_dir():
                # Find annotations.json
                ann_files = list(dataset_dir.rglob("*annotations*.json"))
                if ann_files:
                    ann_file = ann_files[0]
                    images_dir = ann_file.parent / "images"
                    if not images_dir.exists():
                        images_dir = ann_file.parent

                    merger.add_dataset(f"roboflow_{dataset_dir.name}", ann_file, images_dir)

    # 2. Add Kaggle datasets
    kaggle_dir = DATA_RAW / "kaggle"
    if kaggle_dir.exists():
        for dataset_dir in kaggle_dir.iterdir():
            if dataset_dir.is_dir():
                ann_files = list(dataset_dir.rglob("*annotations*.json"))
                if ann_files:
                    ann_file = ann_files[0]
                    images_dir = ann_file.parent / "images"
                    if not images_dir.exists():
                        images_dir = ann_file.parent

                    merger.add_dataset(f"kaggle_{dataset_dir.name}", ann_file, images_dir)

    # 3. Add auto-labeled datasets
    auto_labeled_dir = DATA_RAW / "auto_labeled"
    if auto_labeled_dir.exists():
        for dataset_dir in auto_labeled_dir.iterdir():
            if dataset_dir.is_dir():
                ann_file = dataset_dir / "annotations.json"
                images_dir = dataset_dir / "images"

                if ann_file.exists():
                    merger.add_dataset(f"auto_{dataset_dir.name}", ann_file, images_dir)

    # 4. Add manual labeled dataset
    manual_dir = DATA_RAW.parent / "manual_labeled"
    if manual_dir.exists():
        ann_file = manual_dir / "annotations.json"
        images_dir = manual_dir / "images"

        if ann_file.exists():
            merger.add_dataset("manual", ann_file, images_dir)

    # Print statistics
    merger.print_statistics()

    # Check if we have enough data
    if len(merger.merged_data['images']) < 100:
        print(f"\n⚠️  Warning: Only {len(merger.merged_data['images'])} images found!")
        print("   Minimum 100 images recommended for training")
        response = input("\n   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Merge cancelled")
            return

    # Split dataset
    splits, image_to_anns = merger.split_dataset()

    # Save splits
    print(f"\n{'='*60}")
    print("💾 Saving Dataset Splits")
    print(f"{'='*60}")

    for split_name in ['train', 'val', 'test']:
        output_dir = DATA_FINAL / split_name
        merger.save_split(split_name, splits[split_name], image_to_anns, output_dir)

    # Final summary
    print(f"\n{'='*60}")
    print("✅ Dataset Merge Complete!")
    print(f"{'='*60}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\n📂 Output Structure:")
    print(f"   {DATA_TRAIN}/")
    print(f"   ├── images/")
    print(f"   └── annotations.json")
    print(f"   {DATA_VAL}/")
    print(f"   ├── images/")
    print(f"   └── annotations.json")
    print(f"   {DATA_TEST}/")
    print(f"   ├── images/")
    print(f"   └── annotations.json")

    print(f"\n🚀 Next Steps:")
    print(f"   1. Verify dataset:")
    print(f"      python scripts/visualize_dataset.py")
    print(f"   2. Update config:")
    print(f"      vim configs/cascade_rcnn_swin_korean.py")
    print(f"   3. Start training:")
    print(f"      python scripts/train.py --config configs/cascade_rcnn_swin_korean.py")

if __name__ == "__main__":
    main()
