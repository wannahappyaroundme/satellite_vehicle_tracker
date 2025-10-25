"""
Direct DOTA Dataset Download using Kaggle API
Downloads chandlertimm/dota-data dataset
"""

import os
import sys
from pathlib import Path
import subprocess

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "dota"
DATA_RAW.mkdir(parents=True, exist_ok=True)

def download_dota():
    """Download DOTA dataset from Kaggle"""

    print("\n" + "=" * 60)
    print("📥 DOTA Dataset Download")
    print("=" * 60)

    # Check Kaggle API
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists():
        print("\n❌ Kaggle API not configured!")
        print(f"   Missing: {kaggle_json}")
        return False

    print(f"\n✓ Kaggle API configured")
    print(f"   Config: {kaggle_json}")

    # Dataset info
    dataset = "chandlertimm/dota-data"
    print(f"\n📦 Dataset: {dataset}")
    print(f"   Size: ~20GB (compressed)")
    print(f"   Target: {DATA_RAW}/")

    try:
        # Install kaggle if needed
        print("\n📌 Checking kaggle package...")
        try:
            import kaggle
            print("   ✓ kaggle package found")
        except ImportError:
            print("   ⚠️  Installing kaggle...")
            subprocess.run([sys.executable, "-m", "pip", "install", "kaggle", "-q"], check=True)
            print("   ✓ kaggle installed")
            import kaggle

        # Download using kaggle API
        print("\n⏬ Downloading DOTA dataset...")
        print("   This will take 10-30 minutes depending on your network speed...")
        print("   Progress will be shown below:\n")

        # Use kaggle CLI through subprocess
        cmd = [
            "kaggle", "datasets", "download",
            "-d", dataset,
            "-p", str(DATA_RAW),
            "--unzip"
        ]

        # Run download
        result = subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=False  # Show live output
        )

        print("\n✓ Download complete!")

        # Check downloaded files
        files = list(DATA_RAW.rglob("*"))
        total_size = sum(f.stat().st_size for f in files if f.is_file())

        print(f"\n📊 Downloaded:")
        print(f"   Files: {len([f for f in files if f.is_file()])} files")
        print(f"   Folders: {len([f for f in files if f.is_dir()])} folders")
        print(f"   Size: {total_size / (1024**3):.2f} GB")
        print(f"   Location: {DATA_RAW}/")

        print("\n" + "=" * 60)
        print("✅ Next step: Filter Korea region")
        print("=" * 60)
        print("\nRun:")
        print("   python scripts/filter_korea_region.py")

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Download failed: {e}")
        print("\n💡 Alternative:")
        print("   1. Download manually from: https://www.kaggle.com/datasets/chandlertimm/dota-data")
        print(f"   2. Extract to: {DATA_RAW}/")
        return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    download_dota()
