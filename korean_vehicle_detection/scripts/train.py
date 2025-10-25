"""
Training Script for Cascade R-CNN + Swin Transformer
Optimized for Apple Silicon M3 Max with MPS backend
"""

import os
import sys
import argparse
import torch
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import MMDet modules FIRST to register all custom classes
try:
    import mmdet.models  # Register all models
    import mmdet.datasets  # Register all datasets
    import mmdet.visualization  # Register visualizers
except ImportError as e:
    print(f"Warning: MMDetection imports failed: {e}")
    print("Some features may not work properly.")

def check_environment():
    """Check if environment is properly set up"""
    print("\n" + "=" * 60)
    print("🔍 환경 검사")
    print("=" * 60)

    # Check PyTorch
    print(f"\n✓ PyTorch 버전: {torch.__version__}")

    # Check MPS availability
    if torch.backends.mps.is_available():
        print("✓ MPS (Apple Silicon GPU) 사용 가능")
        device = "mps"
    else:
        print("⚠️  MPS 사용 불가 - CPU로 학습")
        device = "cpu"

    # Check MMCV/MMDet
    try:
        import mmcv
        import mmdet
        print(f"✓ MMCV 버전: {mmcv.__version__}")
        print(f"✓ MMDet 버전: {mmdet.__version__}")
    except ImportError as e:
        print(f"❌ MMDetection 설치 필요: {e}")
        print("\n설치 명령:")
        print("   pip install openmim")
        print("   mim install mmcv==2.1.0")
        print("   mim install mmdet==3.3.0")
        return False

    # Check data
    data_train = PROJECT_ROOT / "data" / "train" / "annotations.json"
    data_val = PROJECT_ROOT / "data" / "val" / "annotations.json"

    if not data_train.exists():
        print(f"\n❌ 학습 데이터 없음: {data_train}")
        print("\n💡 먼저 데이터 전처리를 실행하세요:")
        print("   python scripts/preprocess_data.py")
        return False

    if not data_val.exists():
        print(f"\n❌ 검증 데이터 없음: {data_val}")
        return False

    print(f"\n✓ 학습 데이터: {data_train}")
    print(f"✓ 검증 데이터: {data_val}")

    # Check disk space
    import shutil
    total, used, free = shutil.disk_usage(PROJECT_ROOT)
    free_gb = free / (1024**3)
    print(f"\n💾 사용 가능한 디스크 공간: {free_gb:.1f} GB")

    if free_gb < 10:
        print("⚠️  디스크 공간 부족 (10GB 이상 권장)")

    # Memory info
    import psutil
    mem = psutil.virtual_memory()
    print(f"💻 사용 가능한 RAM: {mem.available / (1024**3):.1f} GB / {mem.total / (1024**3):.1f} GB")

    print("\n" + "=" * 60)
    return True, device

def train(config_file: str, work_dir: str = None, resume: bool = False, skip_confirm: bool = False):
    """
    Train Cascade R-CNN model

    Args:
        config_file: Path to config file
        work_dir: Working directory for checkpoints and logs
        resume: Resume from last checkpoint
        skip_confirm: Skip confirmation prompt for background training
    """
    from mmengine.config import Config
    from mmengine.runner import Runner

    print("\n" + "=" * 60)
    print("🚀 학습 시작")
    print("=" * 60)

    # Load config
    cfg = Config.fromfile(config_file)

    # Override work_dir if specified
    if work_dir:
        cfg.work_dir = work_dir

    # Create work directory
    os.makedirs(cfg.work_dir, exist_ok=True)

    print(f"\n📁 작업 디렉토리: {cfg.work_dir}")
    print(f"📝 설정 파일: {config_file}")

    # Print training info
    print(f"\n⚙️  학습 설정:")
    print(f"   Epochs: {cfg.train_cfg.max_epochs}")
    print(f"   Batch Size: {cfg.train_dataloader.batch_size}")
    print(f"   Learning Rate: {cfg.optim_wrapper.optimizer.lr}")
    print(f"   Device: {cfg.device}")

    # Estimate training time
    # Assuming ~2-3 hours per epoch on M3 Max
    epochs = cfg.train_cfg.max_epochs
    hours_per_epoch = 2.5
    estimated_hours = epochs * hours_per_epoch
    estimated_days = estimated_hours / 24

    print(f"\n⏱️  예상 학습 시간:")
    print(f"   시간당 Epoch: ~{1/hours_per_epoch:.2f}")
    print(f"   총 예상 시간: {estimated_hours:.1f}시간 ({estimated_days:.1f}일)")

    print("\n" + "=" * 60)
    print("💡 학습 진행 모니터링:")
    print("=" * 60)
    print(f"\n1. TensorBoard:")
    print(f"   tensorboard --logdir {cfg.work_dir}")
    print(f"\n2. 로그 파일:")
    print(f"   tail -f {cfg.work_dir}/*.log")
    print(f"\n3. 체크포인트:")
    print(f"   ls -lh {cfg.work_dir}/*.pth")

    # Confirm before training
    if not resume and not skip_confirm:
        print("\n" + "=" * 60)
        response = input("학습을 시작하시겠습니까? (y/n): ")
        if response.lower() != 'y':
            print("학습 취소됨")
            return

    print("\n" + "=" * 60)
    print("🔥 학습 시작...")
    print("=" * 60)

    # Build runner
    runner = Runner.from_cfg(cfg)

    # Resume or train from scratch
    if resume:
        print("\n이전 체크포인트에서 재개...")
        runner.resume = True

    # Start training
    try:
        runner.train()

        print("\n" + "=" * 60)
        print("✅ 학습 완료!")
        print("=" * 60)

        # Find best checkpoint
        best_ckpt = Path(cfg.work_dir) / "best_coco_bbox_mAP_epoch_*.pth"
        best_ckpts = list(Path(cfg.work_dir).glob("best_*.pth"))

        if best_ckpts:
            best_ckpt = best_ckpts[0]
            print(f"\n🏆 최고 성능 체크포인트: {best_ckpt}")
            print(f"   파일 크기: {best_ckpt.stat().st_size / (1024**2):.1f} MB")

        print(f"\n📁 모든 체크포인트: {cfg.work_dir}/")
        print(f"\n다음 단계: 모델 평가")
        print(f"   python scripts/test.py --config {config_file} --checkpoint {best_ckpt}")

    except KeyboardInterrupt:
        print("\n\n⚠️  학습 중단됨 (Ctrl+C)")
        print(f"\n재개하려면:")
        print(f"   python scripts/train.py --config {config_file} --resume")

    except Exception as e:
        print(f"\n\n❌ 학습 오류 발생:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Train Cascade R-CNN for Korean Vehicle Detection')

    parser.add_argument(
        '--config',
        default='configs/cascade_rcnn_swin_korean.py',
        help='Config file path'
    )
    parser.add_argument(
        '--work-dir',
        help='Working directory for checkpoints and logs'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from last checkpoint'
    )
    parser.add_argument(
        '--skip-check',
        action='store_true',
        help='Skip environment check'
    )
    parser.add_argument(
        '--skip-confirm',
        action='store_true',
        help='Skip confirmation prompt (for background training)'
    )

    args = parser.parse_args()

    # Check environment
    if not args.skip_check:
        result = check_environment()
        if isinstance(result, tuple):
            success, device = result
            if not success:
                return
        else:
            return

    # Convert relative path to absolute
    config_file = Path(args.config)
    if not config_file.is_absolute():
        config_file = PROJECT_ROOT / config_file

    if not config_file.exists():
        print(f"\n❌ 설정 파일을 찾을 수 없습니다: {config_file}")
        print("\n사용 가능한 설정 파일:")
        for cfg in (PROJECT_ROOT / "configs").glob("*.py"):
            print(f"   {cfg.relative_to(PROJECT_ROOT)}")
        return

    # Train
    train(
        config_file=str(config_file),
        work_dir=args.work_dir,
        resume=args.resume,
        skip_confirm=args.skip_confirm
    )

if __name__ == "__main__":
    main()
