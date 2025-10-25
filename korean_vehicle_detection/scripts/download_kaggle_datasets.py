"""
Download Kaggle Aerial Vehicle Detection Datasets
Automatically downloads and processes multiple Kaggle datasets for vehicle detection
"""

import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "kaggle"
DATA_RAW.mkdir(parents=True, exist_ok=True)

# Top Kaggle datasets for aerial vehicle detection
DATASETS = [
    {
        "name": "Traffic Aerial Images",
        "kaggle_id": "javiersanchezsoriano/traffic-images-captured-from-uavs",
        "size": "34GB",
        "expected_images": "3000-5000",
        "format": "COCO",
        "priority": 1,
        "description": "High-quality traffic images from UAVs with vehicle annotations"
    },
    {
        "name": "Aerial Vehicles YOLO",
        "kaggle_id": "redzapdos123/aerial-view-of-vehicles-and-humans-dataset-yolo",
        "size": "30GB",
        "expected_images": "2000-3000",
        "format": "YOLO",
        "priority": 2,
        "description": "Aerial view dataset in YOLO format"
    },
    {
        "name": "Roundabout Aerial Images",
        "kaggle_id": "javiersanchezsoriano/roundabout-aerial-images-for-vehicle-detection",
        "size": "13GB",
        "expected_images": "1000-2000",
        "format": "COCO",
        "priority": 3,
        "description": "Roundabout traffic images with vehicle annotations"
    },
    {
        "name": "iSAID Dataset",
        "kaggle_id": "usharengaraju/isaid-dataset",
        "size": "6.8GB",
        "expected_images": "500-1000",
        "format": "COCO",
        "priority": 4,
        "description": "High-quality aerial imagery segmentation dataset"
    }
]

def check_kaggle_credentials():
    """Check if Kaggle credentials are properly configured"""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"

    if not kaggle_json.exists():
        print("\n❌ Kaggle credentials not found!")
        print("\n📋 Setup instructions:")
        print("1. Create Kaggle account: https://www.kaggle.com/")
        print("2. Go to Account settings → API → Create New API Token")
        print("3. Move kaggle.json to ~/.kaggle/")
        print("   mkdir -p ~/.kaggle")
        print("   mv ~/Downloads/kaggle.json ~/.kaggle/")
        print("   chmod 600 ~/.kaggle/kaggle.json")
        return False

    # Check permissions
    if oct(kaggle_json.stat().st_mode)[-3:] != '600':
        print(f"\n⚠️  Fixing kaggle.json permissions...")
        kaggle_json.chmod(0o600)

    print(f"✓ Kaggle credentials found: {kaggle_json}")
    return True

def download_dataset(dataset_info, skip_existing=True):
    """Download a single Kaggle dataset"""

    name = dataset_info["name"]
    kaggle_id = dataset_info["kaggle_id"]

    # Create dataset directory
    dataset_slug = kaggle_id.split('/')[-1]
    dataset_dir = DATA_RAW / dataset_slug

    # Skip if already exists
    if skip_existing and dataset_dir.exists() and list(dataset_dir.iterdir()):
        print(f"\n⏭️  Skipping {name} (already exists)")
        return True

    dataset_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n" + "=" * 60)
    print(f"📦 Downloading: {name}")
    print("=" * 60)
    print(f"   Kaggle ID: {kaggle_id}")
    print(f"   Size: {dataset_info['size']}")
    print(f"   Expected images: {dataset_info['expected_images']}")
    print(f"   Format: {dataset_info['format']}")
    print(f"   Destination: {dataset_dir}/")
    print()

    try:
        # Download using Kaggle CLI
        cmd = [
            "kaggle", "datasets", "download",
            "-d", kaggle_id,
            "-p", str(dataset_dir),
            "--unzip"
        ]

        print(f"🚀 Running: {' '.join(cmd)}")
        print()

        # Run with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        # Print output in real-time
        for line in process.stdout:
            print(line, end='')

        process.wait()

        if process.returncode == 0:
            print(f"\n✓ Successfully downloaded: {name}")

            # Check what was downloaded
            files = list(dataset_dir.rglob("*"))
            total_size = sum(f.stat().st_size for f in files if f.is_file())

            print(f"   Files: {len([f for f in files if f.is_file()])} files")
            print(f"   Total size: {total_size / (1024**3):.2f} GB")

            return True
        else:
            print(f"\n✗ Failed to download: {name}")
            print(f"   Error code: {process.returncode}")
            return False

    except FileNotFoundError:
        print(f"\n❌ Kaggle CLI not found!")
        print("Install with: pip install kaggle")
        return False
    except Exception as e:
        print(f"\n❌ Error downloading {name}: {e}")
        return False

def list_datasets():
    """List all available datasets"""
    print("\n" + "=" * 60)
    print("📋 Available Kaggle Aerial Vehicle Datasets")
    print("=" * 60)

    for i, ds in enumerate(DATASETS, 1):
        print(f"\n{i}. {ds['name']}")
        print(f"   Kaggle ID: {ds['kaggle_id']}")
        print(f"   Size: {ds['size']}")
        print(f"   Expected images: {ds['expected_images']}")
        print(f"   Format: {ds['format']}")
        print(f"   Priority: {ds['priority']}")
        print(f"   Description: {ds['description']}")

    print("\n" + "=" * 60)

def check_disk_space(required_gb=100):
    """Check if sufficient disk space is available"""
    import shutil

    total, used, free = shutil.disk_usage(DATA_RAW)
    free_gb = free / (1024**3)

    print(f"\n💾 Disk Space Check:")
    print(f"   Available: {free_gb:.1f} GB")
    print(f"   Required: {required_gb} GB")

    if free_gb < required_gb:
        print(f"\n⚠️  Warning: Low disk space!")
        print(f"   You may not have enough space for all datasets")
        response = input("\n   Continue anyway? (y/n): ")
        return response.lower() == 'y'

    print(f"   ✓ Sufficient disk space available")
    return True

def download_all(skip_existing=True, priorities=None):
    """Download all datasets or selected priorities"""

    print("\n" + "=" * 60)
    print("🌐 Kaggle Aerial Vehicle Datasets Download")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check credentials
    if not check_kaggle_credentials():
        return False

    # Check disk space
    if not check_disk_space():
        return False

    # Filter datasets by priority
    datasets_to_download = DATASETS
    if priorities:
        datasets_to_download = [ds for ds in DATASETS if ds['priority'] in priorities]

    # Sort by priority
    datasets_to_download = sorted(datasets_to_download, key=lambda x: x['priority'])

    print(f"\n📦 Datasets to download: {len(datasets_to_download)}")
    for ds in datasets_to_download:
        print(f"   {ds['priority']}. {ds['name']} ({ds['size']})")

    # Confirm
    print()
    response = input("Continue with download? (y/n): ")
    if response.lower() != 'y':
        print("Download cancelled")
        return False

    # Download each dataset
    successful = []
    failed = []

    for dataset_info in datasets_to_download:
        if download_dataset(dataset_info, skip_existing):
            successful.append(dataset_info['name'])
        else:
            failed.append(dataset_info['name'])

    # Summary
    print("\n" + "=" * 60)
    print("📊 Download Summary")
    print("=" * 60)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n✓ Successful: {len(successful)}")
    for name in successful:
        print(f"   - {name}")

    if failed:
        print(f"\n✗ Failed: {len(failed)}")
        for name in failed:
            print(f"   - {name}")

    # Calculate total size
    if DATA_RAW.exists():
        total_size = 0
        total_files = 0

        for dataset_dir in DATA_RAW.iterdir():
            if dataset_dir.is_dir():
                files = list(dataset_dir.rglob("*"))
                dataset_files = [f for f in files if f.is_file()]
                dataset_size = sum(f.stat().st_size for f in dataset_files)

                total_files += len(dataset_files)
                total_size += dataset_size

                print(f"\n{dataset_dir.name}:")
                print(f"   Files: {len(dataset_files)}")
                print(f"   Size: {dataset_size / (1024**3):.2f} GB")

        print(f"\n📁 Total:")
        print(f"   Files: {total_files}")
        print(f"   Size: {total_size / (1024**3):.2f} GB")
        print(f"   Location: {DATA_RAW}/")

    print(f"\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("=" * 60)
    print("1. Convert YOLO datasets to COCO format (if needed)")
    print("   python scripts/convert_yolo_to_coco.py")
    print()
    print("2. Merge all datasets")
    print("   python scripts/merge_all_datasets.py")
    print()
    print("3. Start training")
    print("   python scripts/train.py --config configs/cascade_rcnn_swin_korean.py")

    return len(successful) > 0

def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Download Kaggle Aerial Vehicle Detection Datasets'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available datasets'
    )
    parser.add_argument(
        '--priorities',
        type=int,
        nargs='+',
        help='Download only specific priorities (e.g., --priorities 1 2)'
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        default=True,
        help='Skip already downloaded datasets (default: True)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-download even if dataset exists'
    )

    args = parser.parse_args()

    if args.list:
        list_datasets()
        return

    skip_existing = args.skip_existing and not args.force

    download_all(skip_existing=skip_existing, priorities=args.priorities)

if __name__ == "__main__":
    main()
