# 한국 차량 탐지 - YOLOv8x

## 📌 프로젝트 개요

DOTA 위성 이미지에서 한국 차량을 탐지하는 YOLOv8x 딥러닝 모델 학습 프로젝트

**데이터셋:** 340개 이미지, 47,445개 annotations
- Train: 237개 이미지 (23,976개 annotations)
- Val: 68개 이미지
- Test: 35개 이미지
- 클래스: small-vehicle, large-vehicle

**모델:** YOLOv8x (68.2M parameters, 258.1 GFLOPs)
**최적화:** Apple Silicon M3 Max (MPS)

---

## 🚀 학습 시작

```bash
python scripts/train_yolov8x.py
```

**예상 시간:** 약 100시간 (100 epochs × 1시간)
- Early stopping(patience=50) 적용으로 더 빨리 종료될 수 있음
- M3 Max MPS 가속 사용

---

## 📊 학습 진행 확인

### 방법 1: 간단 확인
```bash
python check_training.py
```

### 방법 2: TensorBoard (그래프)
```bash
tensorboard --logdir runs/train/yolov8x_korean_vehicles
```
브라우저: http://localhost:6006

### 방법 3: 결과 CSV 파일
```bash
cat runs/train/yolov8x_korean_vehicles/results.csv
```

---

## 📁 결과 파일 위치

**학습 결과:** `runs/train/yolov8x_korean_vehicles/`

**주요 파일:**
- `weights/best.pt` - 최고 성능 모델 ⭐
- `weights/last.pt` - 마지막 epoch 모델
- `results.png` - 학습 그래프
- `confusion_matrix.png` - 혼동 행렬
- `F1_curve.png`, `PR_curve.png` - 성능 곡선

---

## 🎯 학습 완료 후 사용법

### 추론 (이미지 탐지)

```python
from ultralytics import YOLO

# 모델 로드
model = YOLO('runs/train/yolov8x_korean_vehicles/weights/best.pt')

# 테스트 이미지로 추론
results = model.predict(
    source='data/test/images',
    save=True,
    conf=0.25,
    device='mps'
)

# 단일 이미지
result = model.predict('이미지경로.jpg', save=True)
```

### 성능 평가

```python
from ultralytics import YOLO

model = YOLO('runs/train/yolov8x_korean_vehicles/weights/best.pt')
metrics = model.val(data='data.yaml', device='mps')

print(f'mAP50: {metrics.box.map50:.4f}')
print(f'mAP50-95: {metrics.box.map:.4f}')
```

---

## 🔧 학습 설정

**현재 설정 (scripts/train_yolov8x.py):**
- Device: MPS (Apple Silicon GPU)
- Batch size: 8
- Image size: 1024px
- Optimizer: AdamW (lr=0.001)
- Epochs: 100
- Early stopping: patience=50
- Augmentation: mosaic, mixup, rotation, scaling, flipping

**메모리 부족 시 조정:**
```python
# scripts/train_yolov8x.py 파일 수정
batch=4,      # 8 → 4로 줄이기
imgsz=640,    # 1024 → 640으로 줄이기
```

---

## 🛠️ 문제 해결

### 학습 중단 후 재개

```python
from ultralytics import YOLO

model = YOLO('runs/train/yolov8x_korean_vehicles/weights/last.pt')
model.train(resume=True)
```

### CPU로 학습 (느림)

`scripts/train_yolov8x.py`에서:
```python
device='mps'  →  device='cpu'
```

### 더 작은 모델 사용

```python
from ultralytics import YOLO

# YOLOv8l (Large) - 더 빠르지만 정확도 약간 낮음
model = YOLO('yolov8l.pt')
model.train(
    data='data.yaml',
    epochs=100,
    imgsz=1024,
    device='mps'
)
```

---

## 📂 프로젝트 구조

```
korean_vehicle_detection/
├── data/
│   ├── train/images/       # 학습 이미지
│   ├── train/labels/       # YOLO 포맷 레이블
│   ├── val/images/
│   ├── val/labels/
│   └── test/images/
├── scripts/
│   ├── train_yolov8x.py            # 학습 스크립트
│   ├── convert_coco_to_yolo.py     # 포맷 변환
│   └── check_training.py           # 진행 확인
├── data.yaml               # YOLOv8 데이터셋 설정
├── runs/train/             # 학습 결과
└── README.md               # 이 파일
```

---

## 📈 데이터 전처리 (완료됨)

이미 COCO → YOLO 포맷 변환이 완료되어 있습니다.

**재변환이 필요한 경우:**
```bash
python scripts/convert_coco_to_yolo.py
```

---

**Last Updated:** 2025-10-24
**Model:** YOLOv8x
**Framework:** Ultralytics YOLOv8
