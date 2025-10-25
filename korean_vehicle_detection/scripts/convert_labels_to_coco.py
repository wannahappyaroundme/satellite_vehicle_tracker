"""
Convert LabelImg XML labels to COCO format
Processes manual labels from sample_image1 and sample_image2
"""

import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
LABELING_DIR = PROJECT_ROOT / "data" / "labeling"
IMAGES_DIR = LABELING_DIR / "images"
LABELS_DIR = LABELING_DIR / "labels"
OUTPUT_DIR = PROJECT_ROOT / "data" / "manual_labeled"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Class mapping
CLASS_MAPPING = {
    "small-vehicle": 1,
    "large-vehicle": 2,
    "bus": 2,  # Maps to large-vehicle
    "truck": 2  # Maps to large-vehicle
}

CLASSES = {
    1: "small-vehicle",
    2: "large-vehicle"
}

def parse_xml_annotation(xml_file: Path):
    """
    Parse LabelImg XML format

    XML structure:
    <annotation>
        <filename>image.png</filename>
        <size>
            <width>2480</width>
            <height>3509</height>
        </size>
        <object>
            <name>small-vehicle</name>
            <bndbox>
                <xmin>100</xmin>
                <ymin>200</ymin>
                <xmax>150</xmax>
                <ymax>250</ymax>
            </bndbox>
        </object>
    </annotation>
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Image info
    filename = root.find('filename').text
    size = root.find('size')
    width = int(size.find('width').text)
    height = int(size.find('height').text)

    # Objects
    objects = []
    for obj in root.findall('object'):
        name = obj.find('name').text.lower()

        # Map class
        if name not in CLASS_MAPPING:
            print(f"  ⚠️  Unknown class: {name}, skipping")
            continue

        class_id = CLASS_MAPPING[name]

        # Bounding box
        bndbox = obj.find('bndbox')
        xmin = float(bndbox.find('xmin').text)
        ymin = float(bndbox.find('ymin').text)
        xmax = float(bndbox.find('xmax').text)
        ymax = float(bndbox.find('ymax').text)

        # Convert to COCO format [x, y, width, height]
        bbox_width = xmax - xmin
        bbox_height = ymax - ymin

        if bbox_width <= 0 or bbox_height <= 0:
            print(f"  ⚠️  Invalid bbox: {xmin},{ymin},{xmax},{ymax}, skipping")
            continue

        objects.append({
            "class_id": class_id,
            "class_name": CLASSES[class_id],
            "bbox": [xmin, ymin, bbox_width, bbox_height],
            "area": bbox_width * bbox_height
        })

    return {
        "filename": filename,
        "width": width,
        "height": height,
        "objects": objects
    }

def create_coco_dataset():
    """Create COCO format JSON from LabelImg annotations"""

    print("\n" + "=" * 60)
    print("🔄 Converting Labels to COCO Format")
    print("=" * 60)

    # Find all XML files
    xml_files = list(LABELS_DIR.glob("*.xml"))

    if not xml_files:
        print("\n❌ No XML labels found!")
        print(f"   Location: {LABELS_DIR}")
        print("\n💡 Make sure you saved labels in LabelImg (Ctrl+S)")
        return False

    print(f"\n✓ Found {len(xml_files)} label files:")
    for xml in xml_files:
        print(f"   - {xml.name}")

    # Initialize COCO structure
    coco_data = {
        "info": {
            "description": "Korean Aerial Vehicle Detection - Manual Labels",
            "version": "1.0",
            "year": 2025,
            "date_created": datetime.now().isoformat(),
            "contributor": "Manual Labeling"
        },
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

    annotation_id = 1

    # Process each XML file
    print("\n📝 Processing labels...")
    for image_id, xml_file in enumerate(xml_files, start=1):
        print(f"\n{image_id}. {xml_file.name}")

        # Parse XML
        parsed = parse_xml_annotation(xml_file)

        # Add image info
        image_path = IMAGES_DIR / parsed["filename"]
        if not image_path.exists():
            print(f"   ⚠️  Image not found: {image_path}")
            continue

        image_info = {
            "id": image_id,
            "file_name": parsed["filename"],
            "width": parsed["width"],
            "height": parsed["height"]
        }
        coco_data["images"].append(image_info)

        print(f"   Image: {parsed['width']}x{parsed['height']} pixels")
        print(f"   Objects: {len(parsed['objects'])} vehicles")

        # Add annotations
        for obj in parsed["objects"]:
            annotation = {
                "id": annotation_id,
                "image_id": image_id,
                "category_id": obj["class_id"],
                "bbox": obj["bbox"],
                "area": obj["area"],
                "iscrowd": 0
            }
            coco_data["annotations"].append(annotation)
            annotation_id += 1

            print(f"     - {obj['class_name']}: bbox {obj['bbox']}")

    # Save COCO JSON
    output_json = OUTPUT_DIR / "annotations.json"
    with open(output_json, 'w') as f:
        json.dump(coco_data, f, indent=2)

    # Copy images
    images_output = OUTPUT_DIR / "images"
    images_output.mkdir(exist_ok=True)

    for img_info in coco_data["images"]:
        src = IMAGES_DIR / img_info["file_name"]
        dst = images_output / img_info["file_name"]
        if src.exists() and not dst.exists():
            import shutil
            shutil.copy2(src, dst)

    # Statistics
    print("\n" + "=" * 60)
    print("📊 Conversion Complete!")
    print("=" * 60)

    print(f"\n✅ COCO Dataset Created:")
    print(f"   Images: {len(coco_data['images'])} files")
    print(f"   Annotations: {len(coco_data['annotations'])} vehicles")
    print(f"   Categories: {len(coco_data['categories'])} classes")

    # Class distribution
    class_counts = {}
    for ann in coco_data["annotations"]:
        cid = ann["category_id"]
        class_counts[cid] = class_counts.get(cid, 0) + 1

    print(f"\n📈 Class Distribution:")
    for cid, count in class_counts.items():
        class_name = CLASSES[cid]
        percentage = count / len(coco_data["annotations"]) * 100
        print(f"   {class_name}: {count} ({percentage:.1f}%)")

    print(f"\n💾 Output:")
    print(f"   JSON: {output_json}")
    print(f"   Images: {images_output}/")

    # File size
    json_size = output_json.stat().st_size / 1024
    total_images_size = sum(f.stat().st_size for f in images_output.glob("*")) / (1024**2)
    print(f"   Size: {json_size:.1f} KB (JSON) + {total_images_size:.1f} MB (images)")

    print("\n" + "=" * 60)
    print("✅ Next Step: Integrate with DOTA dataset")
    print("=" * 60)
    print("\nRun:")
    print("   python scripts/filter_korea_region.py")
    print("\nThen:")
    print("   python scripts/preprocess_data.py")

    return True

if __name__ == "__main__":
    create_coco_dataset()
