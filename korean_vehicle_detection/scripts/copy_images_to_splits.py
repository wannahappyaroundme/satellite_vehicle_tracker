"""
Copy images from raw directories to train/val/test directories
"""

import json
import shutil
from pathlib import Path
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW = DATA_DIR / "raw"

# Source directories where images are located
SOURCE_DIRS = [
    DATA_RAW / "roboflow" / "dota" / "train",
    DATA_RAW / "roboflow" / "dota" / "valid",
    DATA_RAW / "roboflow" / "dota" / "test",
    DATA_RAW / "auto_labeled" / "dota_train" / "images",
    DATA_RAW / "auto_labeled" / "dota_val" / "images",
    DATA_RAW / "auto_labeled" / "dota_test" / "images",
    DATA_RAW / "dota" / "DOTA" / "train" / "images",
    DATA_RAW / "dota" / "DOTA" / "val" / "images",
    DATA_RAW / "dota" / "DOTA" / "test" / "images",
    DATA_DIR / "manual_labeled" / "images",
]

def find_image_file(file_name, source_dirs):
    """Find image file in source directories"""
    for source_dir in source_dirs:
        if not source_dir.exists():
            continue

        # Try direct path
        image_path = source_dir / file_name
        if image_path.exists():
            return image_path

        # Try recursive search
        found = list(source_dir.rglob(file_name))
        if found:
            return found[0]

    return None

def copy_images_for_split(split_name):
    """Copy images for a specific split (train/val/test)"""

    split_dir = DATA_DIR / split_name
    ann_file = split_dir / "annotations.json"
    images_dir = split_dir / "images"

    if not ann_file.exists():
        print(f"❌ Annotations not found: {ann_file}")
        return False

    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"📂 Copying images for {split_name.upper()} split")
    print(f"{'='*60}")

    # Load annotations
    with open(ann_file, 'r') as f:
        data = json.load(f)

    print(f"   Images to copy: {len(data['images'])}")
    print(f"   Target directory: {images_dir}/")

    # Copy each image
    copied = 0
    skipped_exists = 0
    not_found = 0

    for img_info in tqdm(data['images'], desc=f"  Copying {split_name}"):
        file_name = img_info['file_name']
        dest_path = images_dir / file_name

        # Skip if already copied
        if dest_path.exists():
            skipped_exists += 1
            continue

        # Find source image
        source_path = find_image_file(file_name, SOURCE_DIRS)

        if source_path is None:
            print(f"   ⚠️  Not found: {file_name}")
            not_found += 1
            continue

        # Copy image
        try:
            shutil.copy2(source_path, dest_path)
            copied += 1
        except Exception as e:
            print(f"   ⚠️  Error copying {file_name}: {e}")
            not_found += 1

    print(f"\n   ✓ Copied: {copied} images")
    if skipped_exists > 0:
        print(f"   ⏭️  Skipped (already exists): {skipped_exists}")
    if not_found > 0:
        print(f"   ❌ Not found: {not_found} images")

    return not_found == 0

def main():
    """Main execution"""

    print("\n" + "=" * 60)
    print("📦 Copying Images to Train/Val/Test Splits")
    print("=" * 60)

    # Copy for each split
    success = True
    for split in ['train', 'val', 'test']:
        if not copy_images_for_split(split):
            success = False

    print("\n" + "=" * 60)
    if success:
        print("✅ All images copied successfully!")
    else:
        print("⚠️  Some images could not be found")
    print("=" * 60)

    # Summary
    for split in ['train', 'val', 'test']:
        images_dir = DATA_DIR / split / "images"
        if images_dir.exists():
            count = len(list(images_dir.glob("*")))
            print(f"   {split}: {count} images")

if __name__ == "__main__":
    main()
