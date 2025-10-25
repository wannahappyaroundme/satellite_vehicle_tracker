"""
Convert COCO format annotations to YOLO format for YOLOv8 training
"""

import json
from pathlib import Path
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

def convert_bbox_coco_to_yolo(coco_bbox, img_width, img_height):
    """
    Convert COCO bbox [x, y, width, height] to YOLO format [x_center, y_center, width, height]
    All values normalized to [0, 1]
    """
    x, y, w, h = coco_bbox

    # Calculate center coordinates
    x_center = (x + w / 2) / img_width
    y_center = (y + h / 2) / img_height

    # Normalize width and height
    width = w / img_width
    height = h / img_height

    return x_center, y_center, width, height

def convert_split_to_yolo(split_name):
    """Convert a single split (train/val/test) from COCO to YOLO format"""

    split_dir = DATA_DIR / split_name
    ann_file = split_dir / "annotations.json"
    images_dir = split_dir / "images"
    labels_dir = split_dir / "labels"

    # Create labels directory
    labels_dir.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Converting {split_name.upper()} split to YOLO format")
    print(f"{'='*60}")

    # Load COCO annotations
    with open(ann_file, 'r') as f:
        coco_data = json.load(f)

    # Create category ID to index mapping (0-indexed for YOLO)
    category_map = {cat['id']: idx for idx, cat in enumerate(coco_data['categories'])}

    # Create image ID to image info mapping
    image_map = {img['id']: img for img in coco_data['images']}

    # Group annotations by image ID
    annotations_by_image = {}
    for ann in coco_data['annotations']:
        img_id = ann['image_id']
        if img_id not in annotations_by_image:
            annotations_by_image[img_id] = []
        annotations_by_image[img_id].append(ann)

    # Convert each image's annotations
    converted_count = 0
    skipped_count = 0

    for img_info in tqdm(coco_data['images'], desc=f"  Converting {split_name}"):
        img_id = img_info['id']
        file_name = img_info['file_name']
        img_width = img_info['width']
        img_height = img_info['height']

        # Get label file path (same name as image but .txt extension)
        label_file = labels_dir / (Path(file_name).stem + '.txt')

        # Get annotations for this image
        anns = annotations_by_image.get(img_id, [])

        if not anns:
            # Create empty label file
            label_file.write_text('')
            skipped_count += 1
            continue

        # Convert annotations to YOLO format
        yolo_lines = []
        for ann in anns:
            # Get category index (0-indexed)
            cat_idx = category_map[ann['category_id']]

            # Convert bbox
            x_center, y_center, width, height = convert_bbox_coco_to_yolo(
                ann['bbox'], img_width, img_height
            )

            # Ensure values are within [0, 1]
            x_center = max(0.0, min(1.0, x_center))
            y_center = max(0.0, min(1.0, y_center))
            width = max(0.0, min(1.0, width))
            height = max(0.0, min(1.0, height))

            # YOLO format: <class_id> <x_center> <y_center> <width> <height>
            yolo_line = f"{cat_idx} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
            yolo_lines.append(yolo_line)

        # Write label file
        label_file.write_text('\n'.join(yolo_lines) + '\n')
        converted_count += 1

    print(f"\n   ✓ Converted: {converted_count} images")
    print(f"   ⏭️  Empty labels: {skipped_count}")
    print(f"   📁 Labels saved to: {labels_dir}/")

    return converted_count

def main():
    """Convert all splits to YOLO format"""

    print("\n" + "=" * 60)
    print("📦 Converting COCO to YOLO Format")
    print("=" * 60)

    total_converted = 0
    for split in ['train', 'val', 'test']:
        count = convert_split_to_yolo(split)
        total_converted += count

    print("\n" + "=" * 60)
    print(f"✅ Total images converted: {total_converted}")
    print("=" * 60)

    # Print category information
    ann_file = DATA_DIR / "train" / "annotations.json"
    with open(ann_file, 'r') as f:
        coco_data = json.load(f)

    print("\n📋 Class mapping for YOLO:")
    for idx, cat in enumerate(coco_data['categories']):
        print(f"   {idx}: {cat['name']}")
    print()

if __name__ == "__main__":
    main()
