#!/usr/bin/env python3
"""
간단히 학습 진행 상황을 확인하는 스크립트
"""
import os
from pathlib import Path

def check_training_progress():
    """학습 진행 상황 확인"""

    results_dir = Path('runs/train/yolov8x_korean_vehicles')

    print("\n" + "="*70)
    print("🔍 YOLOv8x 학습 진행 상황 확인")
    print("="*70)

    if not results_dir.exists():
        print("\n❌ 학습 결과 폴더를 찾을 수 없습니다.")
        print(f"   찾는 위치: {results_dir.absolute()}")
        return

    # 1. 생성된 파일들 확인
    print("\n📁 생성된 파일:")
    for file in sorted(results_dir.glob("*.jpg")):
        size = file.stat().st_size / 1024  # KB
        print(f"   - {file.name} ({size:.1f} KB)")

    # 2. 체크포인트 확인
    weights_dir = results_dir / 'weights'
    if weights_dir.exists():
        print("\n💾 저장된 모델:")
        for weight_file in sorted(weights_dir.glob("*.pt")):
            size = weight_file.stat().st_size / (1024*1024)  # MB
            print(f"   - {weight_file.name} ({size:.1f} MB)")

    # 3. 로그 파일에서 최근 epoch 정보 가져오기
    log_file = Path('yolov8x_training.log')
    if log_file.exists():
        print("\n📊 최근 학습 로그 (마지막 10줄):")
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-10:]:
                if 'Epoch' in line or 'mAP' in line or '%|' in line:
                    print(f"   {line.strip()}")

    # 4. TensorBoard 실행 방법 안내
    print("\n" + "="*70)
    print("📈 더 자세한 정보를 보려면:")
    print("="*70)
    print("\n1️⃣  TensorBoard로 시각적으로 확인:")
    print(f"   tensorboard --logdir {results_dir}")
    print("   그 다음 브라우저에서: http://localhost:6006")

    print("\n2️⃣  실시간 로그 보기:")
    print(f"   tail -f {log_file}")

    print("\n3️⃣  학습 이미지 확인:")
    print(f"   open {results_dir}/train_batch0.jpg")
    print(f"   open {results_dir}/labels.jpg")

    print("\n")

if __name__ == "__main__":
    check_training_progress()
