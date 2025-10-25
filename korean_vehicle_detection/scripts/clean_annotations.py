"""
Clean invalid annotations from COCO format dataset
"""

import json
from pathlib import Path

def clean_annotations(ann_file):
    """Remove invalid annotations (negative coords, zero area, etc.)"""

    with open(ann_file, 'r') as f:
        data = json.load(f)

    original_count = len(data['annotations'])

    valid_annotations = []
    removed = []

    for ann in data['annotations']:
        bbox = ann['bbox']
        x, y, w, h = bbox

        # Check validity
        if x < 0 or y < 0:
            removed.append(f"ID {ann['id']}: negative coords (x={x:.2f}, y={y:.2f})")
            continue

        if w <= 0 or h <= 0:
            removed.append(f"ID {ann['id']}: zero/negative size (w={w:.2f}, h={h:.2f})")
            continue

        if ann['area'] <= 0:
            removed.append(f"ID {ann['id']}: zero/negative area ({ann['area']:.2f})")
            continue

        valid_annotations.append(ann)

    data['annotations'] = valid_annotations

    # Save cleaned file
    backup_file = ann_file.parent / (ann_file.stem + '_backup.json')
    ann_file.rename(backup_file)

    with open(ann_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Cleaned: {ann_file}")
    print(f"{'='*60}")
    print(f"Original annotations: {original_count}")
    print(f"Valid annotations: {len(valid_annotations)}")
    print(f"Removed: {len(removed)}")

    if removed:
        print(f"\nRemoved annotations:")
        for r in removed[:20]:
            print(f"  - {r}")
        if len(removed) > 20:
            print(f"  ... and {len(removed) - 20} more")

    print(f"\n✅ Backup saved to: {backup_file}")

    return len(removed)

def main():
    """Clean all dataset splits"""

    data_dir = Path(__file__).parent.parent / 'data'

    total_removed = 0
    for split in ['train', 'val', 'test']:
        ann_file = data_dir / split / 'annotations.json'
        if ann_file.exists():
            removed = clean_annotations(ann_file)
            total_removed += removed

    print(f"\n{'='*60}")
    print(f"✅ Total annotations removed: {total_removed}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
