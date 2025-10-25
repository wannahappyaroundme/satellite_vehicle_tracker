"""
Download Roboflow Aerial Vehicle Detection Dataset
Public aerial vehicle detection datasets from Roboflow Universe
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "roboflow"
DATA_RAW.mkdir(parents=True, exist_ok=True)

def download_roboflow_dataset(api_key: str = None):
    """
    Download aerial vehicle detection dataset from Roboflow

    Available public datasets:
    1. DOTA Aerial Images
    2. Aerial Vehicle Detection
    3. xView Object Detection
    """

    print("\n" + "=" * 60)
    print("🌐 Roboflow 항공 차량 탐지 데이터셋 다운로드")
    print("=" * 60)

    if not api_key:
        print("\n⚠️  Roboflow API 키가 필요합니다!")
        print("\n📋 API 키 발급 방법:")
        print("1. Roboflow 계정 생성: https://roboflow.com/")
        print("2. Workspace 생성")
        print("3. Settings → API Key 복사")
        print("\n사용법:")
        print("   python scripts/download_roboflow_aerial.py --api-key YOUR_API_KEY")
        return False

    try:
        from roboflow import Roboflow

        # Initialize Roboflow
        rf = Roboflow(api_key=api_key)

        print("\n✓ Roboflow API 연결 성공")

        # Option 1: DOTA Aerial Images (recommended)
        print("\n📦 Option 1: DOTA Aerial Images 다운로드 중...")
        print("   Dataset: felipe-coradesque-6gmum/dota-aerial-images")

        try:
            project = rf.workspace("felipe-coradesque-6gmum").project("dota-aerial-images")
            dataset = project.version(1).download("coco", location=str(DATA_RAW / "dota"))
            print(f"   ✓ 다운로드 완료: {DATA_RAW / 'dota'}")
        except Exception as e:
            print(f"   ✗ 실패: {e}")

        # Option 2: Aerial Vehicle Detection
        print("\n📦 Option 2: Aerial Vehicle Detection 다운로드 중...")
        print("   Dataset: 공개 항공 차량 탐지 데이터셋")

        try:
            # Search for public aerial vehicle datasets
            # Note: Actual dataset name may vary
            project = rf.workspace().project("aerial-vehicle-detection")
            dataset = project.version(1).download("coco", location=str(DATA_RAW / "aerial"))
            print(f"   ✓ 다운로드 완료: {DATA_RAW / 'aerial'}")
        except Exception as e:
            print(f"   ✗ 실패: {e}")
            print("   💡 대안: Roboflow Universe에서 'aerial vehicle' 검색")
            print("   https://universe.roboflow.com/search?q=aerial+vehicle")

        # Print summary
        print("\n" + "=" * 60)
        print("📊 다운로드 결과")
        print("=" * 60)

        if DATA_RAW.exists():
            datasets = list(DATA_RAW.iterdir())
            print(f"\n다운로드된 데이터셋: {len(datasets)}개")

            for ds in datasets:
                if ds.is_dir():
                    size = sum(f.stat().st_size for f in ds.rglob("*") if f.is_file())
                    print(f"   - {ds.name}: {size / (1024**2):.1f} MB")

        print(f"\n📁 저장 경로: {DATA_RAW}/")
        print("\n다음 단계:")
        print("   python scripts/preprocess_data.py")

        return True

    except ImportError:
        print("\n❌ Roboflow 패키지가 설치되지 않았습니다!")
        print("설치:")
        print("   pip install roboflow")
        return False

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return False

def list_public_datasets():
    """List available public aerial vehicle datasets"""
    print("\n" + "=" * 60)
    print("📋 Roboflow Universe 공개 항공 데이터셋")
    print("=" * 60)

    datasets = [
        {
            "name": "DOTA Aerial Images",
            "workspace": "felipe-coradesque-6gmum",
            "project": "dota-aerial-images",
            "url": "https://universe.roboflow.com/felipe-coradesque-6gmum/dota-aerial-images",
            "images": "2,806+",
            "classes": "15 (vehicle, plane, etc.)"
        },
        {
            "name": "xView Object Detection",
            "workspace": "university-college-london-uzluz",
            "project": "xview-4aivt",
            "url": "https://universe.roboflow.com/university-college-london-uzluz/xview-4aivt",
            "images": "1,000+",
            "classes": "60 (vehicles, buildings, etc.)"
        },
        {
            "name": "Aerial Vehicle Dataset",
            "workspace": "various",
            "project": "search on universe",
            "url": "https://universe.roboflow.com/search?q=aerial+vehicle",
            "images": "Multiple datasets",
            "classes": "Vehicle-specific"
        }
    ]

    for i, ds in enumerate(datasets, 1):
        print(f"\n{i}. {ds['name']}")
        print(f"   Workspace: {ds['workspace']}")
        print(f"   Project: {ds['project']}")
        print(f"   Images: {ds['images']}")
        print(f"   Classes: {ds['classes']}")
        print(f"   URL: {ds['url']}")

    print("\n" + "=" * 60)

def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Download Roboflow Aerial Vehicle Dataset')
    parser.add_argument('--api-key', help='Roboflow API key')
    parser.add_argument('--list', action='store_true', help='List available datasets')

    args = parser.parse_args()

    if args.list:
        list_public_datasets()
        return

    # Try to use provided API key or environment variable
    api_key = args.api_key or os.getenv('ROBOFLOW_API_KEY')

    if not api_key:
        print("\n⚠️  API 키를 제공하세요:")
        print("   python scripts/download_roboflow_aerial.py --api-key YOUR_KEY")
        print("\n또는 환경 변수 설정:")
        print("   export ROBOFLOW_API_KEY=your_key")
        print("\n사용 가능한 데이터셋 보기:")
        print("   python scripts/download_roboflow_aerial.py --list")
        return

    download_roboflow_dataset(api_key)

if __name__ == "__main__":
    main()
