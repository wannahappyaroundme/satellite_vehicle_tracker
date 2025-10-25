"""
Train YOLOv8x model on Korean vehicle detection dataset
Using MPS (Metal Performance Shaders) for Apple Silicon acceleration
"""

from ultralytics import YOLO
from pathlib import Path
import torch

def main():
    """Train YOLOv8x on prepared dataset"""

    print("\n" + "=" * 70)
    print("🚀 YOLOv8x Training - Korean Vehicle Detection")
    print("=" * 70)

    # Check device
    if torch.backends.mps.is_available():
        device = 'mps'
        print(f"\n✓ MPS device available - using Apple Silicon GPU acceleration")
    else:
        device = 'cpu'
        print(f"\n⚠️  MPS not available - using CPU")

    print(f"   Device: {device}")

    # Project paths
    project_root = Path(__file__).parent.parent
    data_yaml = project_root / 'data.yaml'

    print(f"\n📋 Configuration:")
    print(f"   Dataset config: {data_yaml}")
    print(f"   Model: YOLOv8x (extra-large)")
    print(f"   Epochs: 100")
    print(f"   Batch size: 8")
    print(f"   Image size: 1024")

    # Initialize YOLOv8x model
    print(f"\n📦 Loading YOLOv8x pretrained model...")
    model = YOLO('yolov8x.pt')  # Will download automatically if not present

    # Training parameters optimized for accuracy (not speed)
    print(f"\n🔧 Training parameters (optimized for accuracy):")
    print(f"   - Optimizer: AdamW")
    print(f"   - Learning rate: 0.001")
    print(f"   - Weight decay: 0.0005")
    print(f"   - Augmentation: Heavy (mosaic, mixup, rotation, scale)")
    print(f"   - Early stopping patience: 50 epochs")

    # Start training
    print(f"\n{'='*70}")
    print("🚀 Starting training...")
    print(f"{'='*70}\n")

    results = model.train(
        data=str(data_yaml),
        epochs=100,
        imgsz=1024,                # Large image size for better accuracy
        batch=8,                   # Batch size (adjust based on memory)
        device=device,             # Use MPS for M3 Max

        # Optimizer settings (for maximum accuracy)
        optimizer='AdamW',
        lr0=0.001,                 # Initial learning rate
        lrf=0.01,                  # Final learning rate (lr0 * lrf)
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,

        # Augmentation (heavy for better generalization)
        hsv_h=0.015,               # HSV-Hue augmentation
        hsv_s=0.7,                 # HSV-Saturation augmentation
        hsv_v=0.4,                 # HSV-Value augmentation
        degrees=10.0,              # Rotation augmentation
        translate=0.1,             # Translation augmentation
        scale=0.9,                 # Scale augmentation
        shear=5.0,                 # Shear augmentation
        perspective=0.0,           # Perspective augmentation
        flipud=0.5,                # Vertical flip probability
        fliplr=0.5,                # Horizontal flip probability
        mosaic=1.0,                # Mosaic augmentation probability
        mixup=0.15,                # Mixup augmentation probability
        copy_paste=0.1,            # Copy-paste augmentation probability

        # Training settings
        patience=50,               # Early stopping patience
        save=True,
        save_period=10,            # Save checkpoint every N epochs
        cache=False,               # Don't cache (to save memory)
        workers=8,                 # Data loading workers
        project='runs/train',
        name='yolov8x_korean_vehicles',
        exist_ok=True,
        pretrained=True,
        verbose=True,

        # Validation settings
        val=True,
        plots=True,

        # Additional accuracy-focused settings
        close_mosaic=10,           # Disable mosaic in last N epochs for stability
        amp=True,                  # Automatic Mixed Precision (faster without losing accuracy)
    )

    print(f"\n{'='*70}")
    print("✅ Training completed!")
    print(f"{'='*70}")

    # Print best metrics
    print(f"\n📊 Best results:")
    print(f"   mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
    print(f"   mAP50-95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")
    print(f"\n   Best model saved to: runs/train/yolov8x_korean_vehicles/weights/best.pt")
    print(f"   Last model saved to: runs/train/yolov8x_korean_vehicles/weights/last.pt")

    print(f"\n📈 View results:")
    print(f"   Training plots: runs/train/yolov8x_korean_vehicles/")
    print(f"   TensorBoard: tensorboard --logdir runs/train")

    print()

if __name__ == "__main__":
    main()
