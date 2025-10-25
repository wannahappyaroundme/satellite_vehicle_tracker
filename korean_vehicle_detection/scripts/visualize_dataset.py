"""
Visualize Dataset
Check dataset quality and visualize annotations
"""

import json
import cv2
import random
import numpy as np
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Colors for visualization
COLORS = {
    1: (0, 255, 0),    # Green for small-vehicle
    2: (0, 0, 255),    # Red for large-vehicle
}

CLASS_NAMES = {
    1: 'small-vehicle',
    2: 'large-vehicle',
}

def visualize_samples(split='train', num_samples=20, output_dir=None):
    """
    Visualize random samples from dataset

    Args:
        split: 'train', 'val', or 'test'
        num_samples: Number of samples to visualize
        output_dir: Output directory (default: data/{split}/visualizations)
    """

    split_dir = DATA_DIR / split
    ann_file = split_dir / "annotations.json"
    images_dir = split_dir / "images"

    if not ann_file.exists():
        print(f"❌ Annotations not found: {ann_file}")
        return

    print(f"\n📊 Visualizing {split.upper()} dataset...")
    print(f"   Annotations: {ann_file}")
    print(f"   Images: {images_dir}/")

    # Load annotations
    with open(ann_file, 'r') as f:
        data = json.load(f)

    # Build image_id to annotations mapping
    image_to_anns = defaultdict(list)
    for ann in data['annotations']:
        image_to_anns[ann['image_id']].append(ann)

    # Select random images with annotations
    images_with_anns = [img for img in data['images'] if img['id'] in image_to_anns]

    if len(images_with_anns) == 0:
        print("❌ No images with annotations found!")
        return

    samples = random.sample(images_with_anns, min(num_samples, len(images_with_anns)))

    # Create output directory
    if output_dir is None:
        output_dir = split_dir / "visualizations"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🖼️  Visualizing {len(samples)} samples...")

    for i, img_info in enumerate(samples, 1):
        # Find image file
        image_path = images_dir / img_info['file_name']

        if not image_path.exists():
            # Try to find in raw directories
            found = list(PROJECT_ROOT.rglob(img_info['file_name']))
            if found:
                image_path = found[0]
            else:
                print(f"   ⚠️  Image not found: {img_info['file_name']}")
                continue

        # Load image
        img = cv2.imread(str(image_path))
        if img is None:
            print(f"   ⚠️  Failed to load: {image_path}")
            continue

        # Draw annotations
        annotations = image_to_anns[img_info['id']]

        for ann in annotations:
            bbox = ann['bbox']  # [x, y, width, height]
            cat_id = ann['category_id']

            x, y, w, h = map(int, bbox)
            color = COLORS.get(cat_id, (255, 255, 255))
            class_name = CLASS_NAMES.get(cat_id, 'unknown')

            # Draw bounding box
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

            # Draw label
            label = f"{class_name}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(img, (x, y - label_size[1] - 5), (x + label_size[0], y), color, -1)
            cv2.putText(img, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Add info text
        info_text = f"{split.upper()} - {i}/{len(samples)} | {len(annotations)} vehicles"
        cv2.putText(img, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # Save
        output_path = output_dir / f"sample_{i:03d}.jpg"
        cv2.imwrite(str(output_path), img)

        if i % 5 == 0:
            print(f"   Progress: {i}/{len(samples)}")

    print(f"\n✓ Saved {len(samples)} visualizations to: {output_dir}/")

def check_dataset_quality(split='train'):
    """
    Check dataset quality and print statistics

    Args:
        split: 'train', 'val', or 'test'
    """

    split_dir = DATA_DIR / split
    ann_file = split_dir / "annotations.json"

    if not ann_file.exists():
        print(f"❌ Annotations not found: {ann_file}")
        return

    print(f"\n{'='*60}")
    print(f"🔍 Dataset Quality Check - {split.upper()}")
    print(f"{'='*60}")

    # Load annotations
    with open(ann_file, 'r') as f:
        data = json.load(f)

    # Basic stats
    num_images = len(data['images'])
    num_annotations = len(data['annotations'])

    print(f"\n📊 Basic Statistics:")
    print(f"   Images: {num_images}")
    print(f"   Annotations: {num_annotations}")
    print(f"   Avg annotations per image: {num_annotations / num_images:.2f}")

    # Class distribution
    class_counts = defaultdict(int)
    for ann in data['annotations']:
        cat_id = ann['category_id']
        class_counts[cat_id] += 1

    print(f"\n📈 Class Distribution:")
    for cat_id in sorted(class_counts.keys()):
        count = class_counts[cat_id]
        percentage = count / num_annotations * 100
        class_name = CLASS_NAMES.get(cat_id, f'class_{cat_id}')
        print(f"   {class_name}: {count} ({percentage:.1f}%)")

    # Bbox size distribution
    bbox_areas = []
    bbox_widths = []
    bbox_heights = []

    for ann in data['annotations']:
        bbox = ann['bbox']
        w, h = bbox[2], bbox[3]
        area = w * h

        bbox_areas.append(area)
        bbox_widths.append(w)
        bbox_heights.append(h)

    print(f"\n📏 Bounding Box Statistics:")
    print(f"   Area (px²):")
    print(f"      Min: {min(bbox_areas):.0f}")
    print(f"      Max: {max(bbox_areas):.0f}")
    print(f"      Mean: {np.mean(bbox_areas):.0f}")
    print(f"      Median: {np.median(bbox_areas):.0f}")

    print(f"   Width (px):")
    print(f"      Min: {min(bbox_widths):.0f}")
    print(f"      Max: {max(bbox_widths):.0f}")
    print(f"      Mean: {np.mean(bbox_widths):.0f}")

    print(f"   Height (px):")
    print(f"      Min: {min(bbox_heights):.0f}")
    print(f"      Max: {max(bbox_heights):.0f}")
    print(f"      Mean: {np.mean(bbox_heights):.0f}")

    # Image size distribution
    image_widths = [img['width'] for img in data['images']]
    image_heights = [img['height'] for img in data['images']]

    print(f"\n🖼️  Image Dimensions:")
    print(f"   Width range: {min(image_widths)} - {max(image_widths)}")
    print(f"   Height range: {min(image_heights)} - {max(image_heights)}")
    print(f"   Most common width: {max(set(image_widths), key=image_widths.count)}")
    print(f"   Most common height: {max(set(image_heights), key=image_heights.count)}")

    # Check for potential issues
    print(f"\n⚠️  Potential Issues:")

    issues = []

    # Too few images
    if num_images < 100:
        issues.append(f"Low image count ({num_images} < 100 recommended)")

    # Class imbalance
    if len(class_counts) > 1:
        class_ratio = max(class_counts.values()) / min(class_counts.values())
        if class_ratio > 10:
            issues.append(f"High class imbalance (ratio: {class_ratio:.1f}:1)")

    # Tiny bboxes
    tiny_bboxes = sum(1 for area in bbox_areas if area < 100)
    if tiny_bboxes > num_annotations * 0.1:
        issues.append(f"Many tiny bboxes ({tiny_bboxes}/{num_annotations})")

    # Huge bboxes
    huge_bboxes = sum(1 for area in bbox_areas if area > 50000)
    if huge_bboxes > 0:
        issues.append(f"Some huge bboxes ({huge_bboxes} > 50000 px²)")

    if issues:
        for issue in issues:
            print(f"   ⚠️  {issue}")
    else:
        print(f"   ✅ No major issues detected")

def plot_statistics(output_dir=None):
    """
    Plot dataset statistics

    Args:
        output_dir: Output directory for plots
    """

    if output_dir is None:
        output_dir = DATA_DIR / "statistics"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📊 Generating statistical plots...")

    # Collect data from all splits
    all_data = {}

    for split in ['train', 'val', 'test']:
        ann_file = DATA_DIR / split / "annotations.json"
        if ann_file.exists():
            with open(ann_file, 'r') as f:
                all_data[split] = json.load(f)

    if not all_data:
        print("❌ No datasets found!")
        return

    # 1. Dataset sizes
    plt.figure(figsize=(10, 6))

    splits = list(all_data.keys())
    image_counts = [len(all_data[split]['images']) for split in splits]
    ann_counts = [len(all_data[split]['annotations']) for split in splits]

    x = np.arange(len(splits))
    width = 0.35

    plt.bar(x - width/2, image_counts, width, label='Images')
    plt.bar(x + width/2, ann_counts, width, label='Annotations')

    plt.xlabel('Split')
    plt.ylabel('Count')
    plt.title('Dataset Size Distribution')
    plt.xticks(x, splits)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)

    plt.savefig(output_dir / 'dataset_sizes.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Class distribution
    plt.figure(figsize=(12, 6))

    for i, split in enumerate(splits, 1):
        plt.subplot(1, len(splits), i)

        class_counts = defaultdict(int)
        for ann in all_data[split]['annotations']:
            cat_id = ann['category_id']
            class_counts[cat_id] += 1

        class_names = [CLASS_NAMES[cid] for cid in sorted(class_counts.keys())]
        counts = [class_counts[cid] for cid in sorted(class_counts.keys())]

        plt.bar(class_names, counts, color=['green', 'red'])
        plt.title(f'{split.upper()} Class Distribution')
        plt.ylabel('Count')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'class_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()

    print(f"✓ Saved plots to: {output_dir}/")

def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Visualize and check dataset quality')
    parser.add_argument(
        '--split',
        type=str,
        default='train',
        choices=['train', 'val', 'test', 'all'],
        help='Dataset split to visualize'
    )
    parser.add_argument(
        '--num-samples',
        type=int,
        default=20,
        help='Number of samples to visualize'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check quality, do not visualize'
    )
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Generate statistical plots'
    )

    args = parser.parse_args()

    if args.plot:
        plot_statistics()

    splits = ['train', 'val', 'test'] if args.split == 'all' else [args.split]

    for split in splits:
        # Check quality
        check_dataset_quality(split)

        # Visualize samples
        if not args.check_only:
            visualize_samples(split, args.num_samples)

    print(f"\n{'='*60}")
    print("✅ Dataset Visualization Complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
