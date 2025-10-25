"""
DOTA Dataset Korean Region Filter
Filters DOTA v2.0 dataset to only include images from Korea and similar East Asian regions
Reduces dataset size from 30-50GB to 5-10GB
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

# Korea and East Asia geographic bounds
# Korea: 33°N-43°N, 124°E-132°E
# Similar urban environments in China/Japan
REGION_BOUNDS = {
    "korea": {
        "lat_min": 33.0,
        "lat_max": 43.0,
        "lon_min": 124.0,
        "lon_max": 132.0,
        "name": "한국"
    },
    "east_china": {
        "lat_min": 30.0,
        "lat_max": 40.0,
        "lon_min": 115.0,
        "lon_max": 125.0,
        "name": "중국 동부 (유사 환경)"
    },
    "japan": {
        "lat_min": 35.0,
        "lat_max": 41.0,
        "lon_min": 135.0,
        "lon_max": 141.0,
        "name": "일본"
    }
}

def extract_gps_from_metadata(image_path: Path) -> Tuple[float, float]:
    """
    Extract GPS coordinates from image metadata

    For DOTA dataset, coordinates might be in:
    - EXIF data
    - Separate metadata JSON
    - Filename pattern
    - Accompanying XML annotation

    Returns:
        (latitude, longitude) or (None, None) if not found
    """
    # Try to find metadata file
    metadata_files = [
        image_path.with_suffix('.json'),
        image_path.with_suffix('.xml'),
        image_path.parent / 'metadata.json'
    ]

    for meta_file in metadata_files:
        if meta_file.exists():
            try:
                if meta_file.suffix == '.json':
                    with open(meta_file, 'r') as f:
                        data = json.load(f)
                        if 'latitude' in data and 'longitude' in data:
                            return float(data['latitude']), float(data['longitude'])
                        if 'gps' in data:
                            return float(data['gps']['lat']), float(data['gps']['lon'])

                elif meta_file.suffix == '.xml':
                    tree = ET.parse(meta_file)
                    root = tree.getroot()
                    lat = root.find('.//latitude')
                    lon = root.find('.//longitude')
                    if lat is not None and lon is not None:
                        return float(lat.text), float(lon.text)
            except Exception as e:
                continue

    return None, None

def is_in_target_region(lat: float, lon: float) -> Tuple[bool, str]:
    """
    Check if coordinates are within target regions

    Returns:
        (is_in_region, region_name)
    """
    if lat is None or lon is None:
        return False, ""

    for region_key, bounds in REGION_BOUNDS.items():
        if (bounds["lat_min"] <= lat <= bounds["lat_max"] and
            bounds["lon_min"] <= lon <= bounds["lon_max"]):
            return True, bounds["name"]

    return False, ""

def filter_by_vehicle_class(annotation_path: Path) -> bool:
    """
    Check if annotation contains vehicle classes

    DOTA classes we want:
    - small-vehicle
    - large-vehicle
    - (optionally: plane, ship for diverse training)
    """
    target_classes = [
        "small-vehicle",
        "large-vehicle",
        "car",
        "truck",
        "bus"
    ]

    if not annotation_path.exists():
        return False

    try:
        with open(annotation_path, 'r') as f:
            content = f.read().lower()
            for cls in target_classes:
                if cls in content:
                    return True
    except Exception:
        pass

    return False

def parse_dota_structure():
    """
    Parse DOTA dataset structure

    Expected structure:
    data/raw/
    ├── train/
    │   ├── images/
    │   └── labelTxt/
    ├── val/
    │   ├── images/
    │   └── labelTxt/
    └── test/
        └── images/
    """
    dota_dirs = []

    # Look for standard DOTA structure
    for split in ['train', 'val', 'test']:
        split_dir = DATA_RAW / split
        if split_dir.exists():
            dota_dirs.append(split_dir)

    # Alternative: flat structure
    if not dota_dirs:
        images_dir = DATA_RAW / "images"
        if images_dir.exists():
            dota_dirs.append(images_dir)

    return dota_dirs

def filter_dataset():
    """Main filtering logic"""

    print("\n" + "=" * 60)
    print("🔍 한국 지역 데이터 필터링 시작")
    print("=" * 60)

    # Parse DOTA structure
    dota_dirs = parse_dota_structure()

    if not dota_dirs:
        print("\n❌ DOTA 데이터셋을 찾을 수 없습니다!")
        print(f"📂 확인 경로: {DATA_RAW}")
        print("\n💡 다음을 확인하세요:")
        print("   1. download_dota.py 실행했는지")
        print("   2. 데이터가 올바른 경로에 있는지")
        print("   3. 수동 다운로드한 경우 압축 해제했는지")
        return

    print(f"\n✅ DOTA 데이터셋 발견: {len(dota_dirs)}개 디렉토리")

    # Statistics
    stats = {
        "total_images": 0,
        "with_gps": 0,
        "in_region": 0,
        "with_vehicles": 0,
        "copied": 0,
        "regions": {}
    }

    # Filter each directory
    for dota_dir in dota_dirs:
        print(f"\n📁 처리 중: {dota_dir}")

        # Find images
        image_extensions = ['.png', '.jpg', '.jpeg', '.tif', '.tiff']
        images = []
        for ext in image_extensions:
            images.extend(dota_dir.glob(f"**/*{ext}"))

        print(f"   총 이미지: {len(images)}장")
        stats["total_images"] += len(images)

        # Process each image
        for img_path in images:
            # Extract GPS
            lat, lon = extract_gps_from_metadata(img_path)

            if lat and lon:
                stats["with_gps"] += 1

                # Check if in target region
                in_region, region_name = is_in_target_region(lat, lon)

                if in_region:
                    stats["in_region"] += 1
                    stats["regions"][region_name] = stats["regions"].get(region_name, 0) + 1

                    # Check for vehicle annotations
                    label_dir = img_path.parent.parent / "labelTxt"
                    label_file = label_dir / f"{img_path.stem}.txt"

                    has_vehicles = filter_by_vehicle_class(label_file)

                    if has_vehicles:
                        stats["with_vehicles"] += 1

                        # Copy to processed directory
                        target_img_dir = DATA_PROCESSED / "images"
                        target_lbl_dir = DATA_PROCESSED / "labels"
                        target_img_dir.mkdir(parents=True, exist_ok=True)
                        target_lbl_dir.mkdir(parents=True, exist_ok=True)

                        # Copy image
                        target_img = target_img_dir / img_path.name
                        if not target_img.exists():
                            shutil.copy2(img_path, target_img)

                        # Copy label
                        if label_file.exists():
                            target_lbl = target_lbl_dir / label_file.name
                            if not target_lbl.exists():
                                shutil.copy2(label_file, target_lbl)

                        stats["copied"] += 1

                        if stats["copied"] % 10 == 0:
                            print(f"   ✓ 복사됨: {stats['copied']}장", end='\r')

    # Print statistics
    print("\n\n" + "=" * 60)
    print("📊 필터링 결과")
    print("=" * 60)
    print(f"\n총 이미지:        {stats['total_images']:,}장")
    print(f"GPS 정보 있음:    {stats['with_gps']:,}장 ({stats['with_gps']/max(stats['total_images'],1)*100:.1f}%)")
    print(f"목표 지역 내:     {stats['in_region']:,}장 ({stats['in_region']/max(stats['with_gps'],1)*100:.1f}%)")
    print(f"차량 포함:        {stats['with_vehicles']:,}장")
    print(f"\n✅ 최종 복사됨:   {stats['copied']:,}장")

    if stats["regions"]:
        print("\n📍 지역별 분포:")
        for region, count in stats["regions"].items():
            print(f"   - {region}: {count}장")

    # Calculate size
    if stats["copied"] > 0:
        total_size = sum(f.stat().st_size for f in DATA_PROCESSED.glob("**/*") if f.is_file())
        print(f"\n💾 저장 공간: {total_size / (1024**3):.2f} GB")
        print(f"📂 저장 경로: {DATA_PROCESSED}/")

    # Warning if no data found
    if stats["copied"] == 0:
        print("\n" + "=" * 60)
        print("⚠️  경고: 한국 지역 데이터를 찾을 수 없습니다!")
        print("=" * 60)
        print("\n🔍 가능한 원인:")
        print("   1. DOTA 데이터셋에 GPS 메타데이터가 없음")
        print("   2. DOTA v2.0의 대부분이 중국 내륙 지역")
        print("   3. 메타데이터 파싱 방법이 맞지 않음")
        print("\n💡 대안:")
        print("   1. AI Hub 한국 데이터셋 신청 (강력 추천)")
        print("      https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=598")
        print("   2. 전체 DOTA 데이터셋으로 학습 후 한국 데이터로 Fine-tuning")
        print("   3. sample_image1/2.pdf에 라벨링 추가하여 Few-shot learning")
        print("\n" + "=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✅ 다음 단계: 데이터 전처리")
        print("=" * 60)
        print("\n실행:")
        print("   python scripts/preprocess_data.py")
        print("\n" + "=" * 60)

def main():
    """Main execution"""
    filter_dataset()

if __name__ == "__main__":
    main()
