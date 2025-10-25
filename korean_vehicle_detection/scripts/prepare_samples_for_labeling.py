"""
Prepare sample_image1.pdf and sample_image2.pdf for manual labeling
Converts PDFs to high-quality PNG images and sets up LabelImg environment
"""

import os
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SAMPLES_DIR = PROJECT_ROOT
LABELING_DIR = PROJECT_ROOT / "korean_vehicle_detection" / "data" / "labeling"
IMAGES_DIR = LABELING_DIR / "images"
LABELS_DIR = LABELING_DIR / "labels"

# Create directories
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
LABELS_DIR.mkdir(parents=True, exist_ok=True)

def convert_pdf_to_png(pdf_path: Path, output_dir: Path, dpi: int = 300):
    """
    Convert PDF to high-resolution PNG

    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory for PNG
        dpi: Resolution (300 = high quality)
    """
    print(f"\n📄 Converting {pdf_path.name}...")

    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=dpi)

        print(f"   Pages found: {len(images)}")

        # Save each page
        for i, image in enumerate(images):
            # Generate output filename
            output_name = f"{pdf_path.stem}_page{i+1}.png"
            output_path = output_dir / output_name

            # Save as PNG
            image.save(output_path, "PNG")

            # Get image info
            width, height = image.size
            file_size = output_path.stat().st_size / (1024**2)  # MB

            print(f"   ✓ {output_name}")
            print(f"     Resolution: {width}x{height} pixels")
            print(f"     Size: {file_size:.1f} MB")

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def create_class_file():
    """Create classes.txt for LabelImg"""
    classes = [
        "small-vehicle",
        "large-vehicle",
        "bus",
        "truck"
    ]

    class_file = LABELING_DIR / "classes.txt"

    with open(class_file, 'w') as f:
        f.write('\n'.join(classes))

    print(f"\n📝 Created {class_file}")
    print("   Classes:")
    for cls in classes:
        print(f"     - {cls}")

def create_labeling_guide():
    """Create labeling guide document"""
    guide = """# 제주도 항공사진 라벨링 가이드

## 🎯 목적
sample_image1.pdf (2015)와 sample_image2.pdf (2020) 항공사진에서 차량을 탐지하여
장기 방치 차량을 식별하기 위한 학습 데이터 생성

---

## 📋 클래스 정의

### 1. small-vehicle (소형 차량)
- **포함**: 승용차, 소형 SUV, 경차, 택시
- **크기**: 작은 사각형 (약 15-30 픽셀)
- **색상**: 흰색, 검은색, 은색, 빨간색 등
- **특징**: 주차장에 가장 많이 보이는 일반 차량

### 2. large-vehicle (대형 차량)
- **포함**: 윙 트럭, 대형 트럭, 트레일러
- **크기**: 큰 직사각형 (약 40-80 픽셀)
- **특징**: 승용차보다 2-3배 큰 차량

### 3. bus (버스)
- **포함**: 관광버스, 시내버스
- **크기**: 긴 직사각형 (약 30-50 픽셀)
- **특징**: 길이가 길고 폭이 좁음

### 4. truck (트럭)
- **포함**: 중형 트럭, 화물차
- **크기**: 중간 크기 (약 25-40 픽셀)
- **특징**: 승용차보다 크지만 대형 차량보다 작음

---

## 🔧 LabelImg 사용법

### 실행
```bash
cd ~/Desktop/satellite_project
source .venv/bin/activate
labelImg korean_vehicle_detection/data/labeling/images korean_vehicle_detection/data/labeling/classes.txt korean_vehicle_detection/data/labeling/labels
```

### 단축키
- **W**: 새 바운딩 박스 그리기
- **D**: 다음 이미지
- **A**: 이전 이미지
- **Del**: 선택한 박스 삭제
- **Ctrl+S**: 저장
- **Ctrl+D**: 박스 복사

### 라벨링 팁
1. **확대/축소**: 마우스 휠로 확대하여 정확하게 표시
2. **박스 크기**: 차량 전체를 포함하되 여백 최소화
3. **겹친 차량**: 각각 별도로 표시
4. **부분만 보이는 차량**: 보이는 부분만 표시
5. **그림자 제외**: 차량 본체만 포함, 그림자 제외

---

## 📊 라벨링 목표

### 최소 목표
- **sample_image1 (2015)**: 100-150개 차량
- **sample_image2 (2020)**: 100-150개 차량
- **총계**: 200-300개 바운딩 박스

### 권장 목표
- **sample_image1 (2015)**: 200-250개 차량
- **sample_image2 (2020)**: 200-250개 차량
- **총계**: 400-500개 바운딩 박스

더 많은 라벨링 = 더 높은 정확도!

---

## ✅ 품질 체크리스트

라벨링 완료 후 확인:
- [ ] 모든 보이는 차량을 표시했는가?
- [ ] 박스가 차량 전체를 포함하는가?
- [ ] 클래스를 정확히 선택했는가?
- [ ] 횡단보도, 도로 선을 차량으로 표시하지 않았는가?
- [ ] .xml 파일이 자동 저장되었는가?

---

## 🔄 라벨링 완료 후

1. **저장 확인**
   ```bash
   ls -l korean_vehicle_detection/data/labeling/labels/
   # sample_image1_page1.xml
   # sample_image2_page1.xml
   ```

2. **전처리 실행**
   ```bash
   python korean_vehicle_detection/scripts/convert_labels_to_coco.py
   ```

3. **학습 데이터에 추가**
   - 전처리된 데이터가 train/val/test에 자동 추가됨

---

## 💡 주의사항

### 표시하지 말아야 할 것들
- ❌ 횡단보도
- ❌ 주차 구획선
- ❌ 도로 표시
- ❌ 건물 그림자
- ❌ 나무 그림자
- ❌ 사람

### 애매한 경우
- **차량 절반만 보임**: 보이는 부분만 표시
- **색이 도로와 비슷함**: 차량 윤곽이 있으면 표시
- **작은 점처럼 보임**: 10픽셀 이상이면 표시
- **종류 불명확**: small-vehicle로 표시

---

## 📞 문의

라벨링 중 궁금한 점이 있으면 질문하세요!

**예상 소요 시간**: 2-4시간 (경험에 따라 다름)
**휴식 권장**: 1시간마다 10분 휴식

화이팅! 🚀
"""

    guide_file = LABELING_DIR / "LABELING_GUIDE.md"
    with open(guide_file, 'w') as f:
        f.write(guide)

    print(f"\n📖 Created {guide_file}")
    print("   라벨링 가이드를 확인하세요:")
    print(f"   cat {guide_file}")

def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print("🏷️  Sample Image Preparation for Labeling")
    print("=" * 60)

    # Find sample PDF files
    sample1 = SAMPLES_DIR / "sample_image1.pdf"
    sample2 = SAMPLES_DIR / "sample_image2.pdf"

    if not sample1.exists():
        print(f"\n❌ sample_image1.pdf not found at {sample1}")
        return

    if not sample2.exists():
        print(f"\n❌ sample_image2.pdf not found at {sample2}")
        return

    print(f"\n✓ Found sample_image1.pdf")
    print(f"✓ Found sample_image2.pdf")

    # Convert PDFs to PNG
    print("\n" + "=" * 60)
    print("📸 Converting PDFs to PNG (300 DPI)")
    print("=" * 60)

    success1 = convert_pdf_to_png(sample1, IMAGES_DIR, dpi=300)
    success2 = convert_pdf_to_png(sample2, IMAGES_DIR, dpi=300)

    if not (success1 and success2):
        print("\n⚠️  Some conversions failed!")
        return

    # Create class file
    print("\n" + "=" * 60)
    print("📝 Creating Class Definitions")
    print("=" * 60)
    create_class_file()

    # Create labeling guide
    print("\n" + "=" * 60)
    print("📖 Creating Labeling Guide")
    print("=" * 60)
    create_labeling_guide()

    # Print summary
    print("\n" + "=" * 60)
    print("✅ Preparation Complete!")
    print("=" * 60)

    images = list(IMAGES_DIR.glob("*.png"))
    total_size = sum(img.stat().st_size for img in images) / (1024**2)

    print(f"\n📁 Labeling Directory: {LABELING_DIR}/")
    print(f"   Images: {len(images)}개 ({total_size:.1f} MB)")
    print(f"   Classes: {LABELING_DIR / 'classes.txt'}")
    print(f"   Guide: {LABELING_DIR / 'LABELING_GUIDE.md'}")

    print("\n" + "=" * 60)
    print("🚀 Start Labeling")
    print("=" * 60)
    print("\n실행 명령:")
    print(f"   cd {PROJECT_ROOT}")
    print("   source .venv/bin/activate")
    print(f"   labelImg {IMAGES_DIR} {LABELING_DIR / 'classes.txt'} {LABELS_DIR}")

    print("\n💡 팁:")
    print("   1. 라벨링 가이드 먼저 읽기:")
    print(f"      cat {LABELING_DIR / 'LABELING_GUIDE.md'}")
    print("   2. 확대/축소: 마우스 휠")
    print("   3. 박스 그리기: W 키")
    print("   4. 저장: Ctrl+S")
    print("   5. 다음 이미지: D 키")

    print("\n⏱️  예상 소요 시간: 2-4시간")
    print("🎯 목표: 200-300개 차량 라벨링")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
