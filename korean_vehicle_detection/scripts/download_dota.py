"""
DOTA v2.0 Dataset Download Script
Downloads DOTA dataset from Kaggle and prepares for Korean region filtering
"""

import os
import sys
import subprocess
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_RAW.mkdir(parents=True, exist_ok=True)

def check_kaggle_api():
    """Check if Kaggle API is configured"""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"

    if not kaggle_json.exists():
        print("=" * 60)
        print("⚠️  Kaggle API 설정이 필요합니다!")
        print("=" * 60)
        print("\n📋 설정 방법:")
        print("1. Kaggle 계정 로그인: https://www.kaggle.com/")
        print("2. Account → API → Create New API Token")
        print("3. 다운로드된 kaggle.json을 다음 위치로 이동:")
        print(f"   {kaggle_json.parent}/")
        print("\n💻 명령어:")
        print(f"   mkdir -p {kaggle_json.parent}")
        print(f"   mv ~/Downloads/kaggle.json {kaggle_json.parent}/")
        print(f"   chmod 600 {kaggle_json}")
        print("\n" + "=" * 60)
        return False

    return True

def download_dota_kaggle():
    """Download DOTA dataset from Kaggle"""

    if not check_kaggle_api():
        return False

    print("\n🔽 DOTA Dataset 다운로드 시작...")
    print(f"📂 저장 경로: {DATA_RAW}")
    print("\n⏳ 예상 시간: 30-60분 (네트워크 속도에 따라 다름)")
    print("📦 예상 크기: ~30-50GB\n")

    # Kaggle dataset download command
    # Note: Actual dataset name might differ - user needs to find correct Kaggle dataset
    try:
        # Option 1: DOTA from Kaggle
        cmd = [
            "kaggle", "datasets", "download",
            "-d", "chandlertimm/dota-data",  # Example dataset
            "-p", str(DATA_RAW),
            "--unzip"
        ]

        print(f"💡 실행 명령: {' '.join(cmd)}\n")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        print("✅ 다운로드 완료!")
        print(f"📁 데이터 위치: {DATA_RAW}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 다운로드 실패!")
        print(f"에러: {e.stderr}")
        print("\n🔍 대안 다운로드 방법:")
        print("\n1. IEEE DataPort (공식):")
        print("   https://ieee-dataport.org/documents/dota")
        print("   - 회원가입 후 수동 다운로드")
        print("\n2. Roboflow Universe:")
        print("   https://universe.roboflow.com/felipe-coradesque-6gmum/dota-aerial-images")
        print("   - API를 통한 데이터셋 접근")
        print("\n3. 공식 웹사이트:")
        print("   https://captain-whu.github.io/DOTA/dataset.html")
        print("   - DOTA-v1.0 + DOTA-v2.0 extras 다운로드")
        return False

    except FileNotFoundError:
        print("\n❌ Kaggle CLI가 설치되지 않았습니다!")
        print("💡 설치 명령:")
        print("   pip install kaggle")
        return False

def check_downloaded_data():
    """Check if DOTA data exists"""
    dota_files = list(DATA_RAW.glob("*.zip")) + list(DATA_RAW.glob("images/"))

    if dota_files:
        print("\n✅ 다운로드된 DOTA 데이터 발견:")
        for f in dota_files[:5]:  # Show first 5 files
            size = f.stat().st_size / (1024**3) if f.is_file() else 0
            print(f"   - {f.name} ({size:.2f} GB)")
        return True
    else:
        print("\n⚠️  DOTA 데이터가 없습니다.")
        return False

def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print("📦 DOTA v2.0 Dataset Download")
    print("=" * 60)

    # Check if data already exists
    if check_downloaded_data():
        print("\n💡 이미 데이터가 존재합니다. 다시 다운로드하려면 data/raw 폴더를 삭제하세요.")
        return

    # Download from Kaggle
    success = download_dota_kaggle()

    if success:
        print("\n" + "=" * 60)
        print("✅ 다음 단계: 한국 지역 필터링")
        print("=" * 60)
        print("\n실행:")
        print("   python scripts/filter_korea_region.py")
        print("\n" + "=" * 60)
    else:
        print("\n" + "=" * 60)
        print("📌 수동 다운로드 후 다음 경로에 압축 해제:")
        print(f"   {DATA_RAW}/")
        print("\n압축 해제 후 실행:")
        print("   python scripts/filter_korea_region.py")
        print("=" * 60)

if __name__ == "__main__":
    main()
