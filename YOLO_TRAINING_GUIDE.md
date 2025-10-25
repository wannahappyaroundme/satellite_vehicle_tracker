# 🎓 YOLOv8 차량 탐지 모델 학습 가이드

> **장기 방치 차량 탐지 시스템의 차량 탐지 정확도를 높이기 위한 YOLOv8 학습 가이드**

---

## 📋 목차

1. [YOLOv8이란?](#yolov8이란)
2. [왜 학습이 필요한가?](#왜-학습이-필요한가)
3. [학습 데이터 준비](#학습-데이터-준비)
4. [학습 환경 설정](#학습-환경-설정)
5. [모델 학습 실행](#모델-학습-실행)
6. [학습된 모델 적용](#학습된-모델-적용)
7. [FAQ](#faq)

---

## YOLOv8이란?

**YOLO (You Only Look Once)**는 실시간 객체 탐지를 위한 최신 딥러닝 모델입니다.

### YOLOv8의 특징

- ⚡ **빠른 속도**: 실시간 객체 탐지 가능
- 🎯 **높은 정확도**: 최신 아키텍처로 정확도 향상
- 🔧 **쉬운 사용**: Python API로 간단하게 사용
- 📦 **사전학습 모델**: 80개 클래스 객체 탐지 가능 (차량 포함)

### 우리 시스템에서의 역할

```
항공사진 → YOLOv8 (차량 탐지) → ResNet50 (특징 추출) → 유사도 비교
```

YOLOv8은 항공사진에서 **차량 객체를 찾는** 역할을 합니다.

---

## 왜 학습이 필요한가?

### 사전학습 모델의 한계

기본 YOLOv8 모델은 일반 사진(도로, 거리)에서 차량을 잘 탐지합니다. 하지만:

❌ **항공사진의 특수성**:
- 위에서 내려다본 각도 (Top-down view)
- 작은 차량 크기
- 주차장 환경
- 한국 차량의 특성

✅ **학습으로 해결**:
- 항공사진 특화 학습
- 한국 차량 데이터셋 활용
- 주차장 환경 최적화
- **정확도 15-30% 향상 가능!**

---

## 학습 데이터 준비

### 1. 데이터셋 구조

YOLOv8는 다음 구조의 데이터셋이 필요합니다:

```
dataset/
├── images/
│   ├── train/       # 학습 이미지 (70-80%)
│   ├── val/         # 검증 이미지 (10-20%)
│   └── test/        # 테스트 이미지 (10%)
└── labels/
    ├── train/       # 학습 라벨
    ├── val/         # 검증 라벨
    └── test/        # 테스트 라벨
```

### 2. 라벨 형식 (YOLO Format)

각 이미지마다 `.txt` 파일이 필요합니다:

```
# 파일명: image001.txt
# 형식: <class> <x_center> <y_center> <width> <height>
# 모든 값은 0-1 사이로 정규화

0 0.512 0.345 0.082 0.124
0 0.687 0.512 0.091 0.135
1 0.234 0.789 0.156 0.203
```

**클래스 정의**:
- `0`: car (승용차/승합차)
- `1`: truck (트럭)
- `2`: bus (버스)

### 3. 데이터 라벨링 도구

추천 라벨링 도구:

#### **LabelImg** (무료)
```bash
pip install labelImg
labelImg
```
- 사용 간편
- YOLO 형식 직접 지원
- 단축키로 빠른 작업

#### **Roboflow** (웹 기반)
- https://roboflow.com
- 온라인 협업 가능
- 자동 증강 기능
- **추천!**

### 4. 한국 차량 데이터셋 (공개 데이터)

#### AI Hub (한국어 데이터셋)
- https://aihub.or.kr
- **"자율주행 차량 데이터"** 검색
- 무료 다운로드 (회원가입 필요)

#### Roboflow Universe
- https://universe.roboflow.com
- **"vehicle aerial view"** 검색
- 항공사진 차량 데이터셋

---

## 학습 환경 설정

### 시스템 요구사항

**최소 사양**:
- CPU: Intel i5 이상
- RAM: 16GB 이상
- GPU: NVIDIA GTX 1060 (6GB VRAM) 이상
- 저장공간: 50GB 이상

**권장 사양**:
- GPU: NVIDIA RTX 3060 (12GB VRAM) 이상
- RAM: 32GB

### 1. Python 패키지 설치

```bash
# YOLOv8 설치
pip install ultralytics

# 추가 패키지
pip install opencv-python pillow matplotlib
```

### 2. GPU 설정 (선택)

NVIDIA GPU가 있다면:

```bash
# CUDA 설치 확인
nvidia-smi

# PyTorch GPU 버전 설치
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 모델 학습 실행

### 1. 데이터 설정 파일 작성

`data.yaml` 파일 생성:

```yaml
# data.yaml

# 경로 설정 (절대 경로 권장)
path: /Users/yourname/Desktop/vehicle_dataset
train: images/train
val: images/val
test: images/test

# 클래스 정의
names:
  0: car
  1: truck
  2: bus

# 클래스 개수
nc: 3
```

### 2. 학습 스크립트 작성

`train_yolo.py` 파일 생성:

```python
from ultralytics import YOLO

# 1. 모델 선택
# yolov8n.pt - 가장 빠름 (6.5MB)
# yolov8s.pt - 작고 빠름 (22MB)
# yolov8m.pt - 중간 (52MB) ⭐ 권장
# yolov8l.pt - 큼 (88MB)
# yolov8x.pt - 가장 큼, 정확 (138MB)

model = YOLO('yolov8m.pt')  # 사전학습 모델 로드

# 2. 학습 시작
results = model.train(
    data='data.yaml',           # 데이터 설정 파일
    epochs=100,                 # 학습 에포크 (100-300 권장)
    imgsz=640,                  # 이미지 크기 (640 권장)
    batch=16,                   # 배치 크기 (GPU 메모리에 따라 조정)
    name='vehicle_detector',    # 프로젝트 이름
    device=0,                   # GPU 번호 (CPU는 'cpu')
    patience=50,                # Early stopping
    save=True,                  # 모델 저장
    plots=True,                 # 학습 그래프 생성

    # 증강 설정
    hsv_h=0.015,               # 색조 증강
    hsv_s=0.7,                 # 채도 증강
    hsv_v=0.4,                 # 명도 증강
    degrees=10.0,              # 회전 증강
    translate=0.1,             # 이동 증강
    scale=0.5,                 # 크기 증강
    fliplr=0.5,                # 좌우 반전
    mosaic=1.0,                # 모자이크 증강
)

print("✅ 학습 완료!")
print(f"모델 저장 위치: {results.save_dir}/weights/best.pt")
```

### 3. 학습 실행

```bash
python train_yolo.py
```

**예상 학습 시간**:
- CPU: 수 일 (비추천)
- GTX 1060: ~24시간
- RTX 3060: ~12시간
- RTX 4090: ~6시간

### 4. 학습 모니터링

학습 중 다음 정보를 확인할 수 있습니다:

```bash
# TensorBoard로 실시간 모니터링
tensorboard --logdir runs/train/vehicle_detector
# http://localhost:6006 에서 확인
```

**확인 가능한 지표**:
- `mAP50`: 정확도 (높을수록 좋음, 0.7 이상 목표)
- `Precision`: 정밀도
- `Recall`: 재현율
- `Loss`: 손실 (낮을수록 좋음)

---

## 학습된 모델 적용

### 1. 모델 파일 위치

학습이 완료되면 다음 위치에 모델이 저장됩니다:

```
runs/train/vehicle_detector/weights/
├── best.pt      # 최고 성능 모델 ⭐
└── last.pt      # 마지막 에포크 모델
```

### 2. 우리 시스템에 적용

#### 방법 1: 모델 파일 교체

```bash
# 기존 모델 백업
mv backend/yolov8n.pt backend/yolov8n_backup.pt

# 새 모델 복사
cp runs/train/vehicle_detector/weights/best.pt backend/yolov8_custom.pt
```

#### 방법 2: vehicle_detector.py 수정

```python
# backend/vehicle_detector.py 수정

class VehicleDetector:
    def __init__(self):
        # 기존
        # self.model = YOLO('yolov8n.pt')

        # 학습된 모델 사용 ⭐
        self.model = YOLO('yolov8_custom.pt')
```

### 3. 성능 테스트

```python
from ultralytics import YOLO

# 학습된 모델 로드
model = YOLO('runs/train/vehicle_detector/weights/best.pt')

# 테스트 이미지로 검증
results = model.predict(
    source='test_images/',
    save=True,
    conf=0.25,  # 신뢰도 임계값
)

# 성능 평가
metrics = model.val(data='data.yaml')
print(f'mAP50: {metrics.box.map50:.4f}')
print(f'mAP50-95: {metrics.box.map:.4f}')
```

---

## FAQ

### Q1. 데이터가 얼마나 필요한가요?

**최소**: 500장 (클래스당 ~170장)
**권장**: 2,000장 이상 (클래스당 ~670장)
**이상적**: 10,000장 이상

적은 데이터로 시작하고 점진적으로 늘려가는 것을 권장합니다.

### Q2. GPU가 없으면 학습할 수 없나요?

CPU로도 가능하지만 **매우 느립니다** (수 일 소요).

**대안**:
- **Google Colab** (무료 GPU): https://colab.research.google.com
- **Kaggle Kernels** (무료 GPU): https://www.kaggle.com/code
- **AWS/GCP** (유료 클라우드 GPU)

### Q3. 학습 중 메모리 부족 오류가 나요!

배치 크기를 줄여보세요:

```python
model.train(
    batch=8,   # 16 → 8로 줄임
    imgsz=416  # 640 → 416으로 줄임 (선택)
)
```

### Q4. 학습이 너무 오래 걸려요!

**해결 방법**:
1. 작은 모델 사용 (`yolov8n.pt` 또는 `yolov8s.pt`)
2. 에포크 줄이기 (100 → 50)
3. 이미지 크기 줄이기 (640 → 416)
4. GPU 사용

### Q5. 정확도가 낮아요!

**개선 방법**:
1. **데이터 품질 확인**: 라벨링이 정확한가?
2. **데이터 양 증가**: 더 많은 학습 데이터 추가
3. **증강 활성화**: 데이터 증강 파라미터 조정
4. **에포크 증가**: 100 → 200
5. **큰 모델 사용**: yolov8m → yolov8l

### Q6. 기존 모델을 계속 학습시킬 수 있나요?

네! **Transfer Learning**이 가능합니다:

```python
# 기존 학습된 모델에서 계속 학습
model = YOLO('runs/train/vehicle_detector/weights/best.pt')

model.train(
    data='data.yaml',
    epochs=50,  # 추가 50 에포크
    resume=True  # 이어서 학습
)
```

---

## 📚 추가 자료

### 공식 문서
- **YOLOv8 공식 문서**: https://docs.ultralytics.com
- **학습 가이드**: https://docs.ultralytics.com/modes/train/
- **데이터 형식**: https://docs.ultralytics.com/datasets/

### 튜토리얼
- **YouTube**: "YOLOv8 Custom Training Tutorial"
- **Medium**: "Training YOLOv8 on Custom Dataset"

### 데이터셋
- **AI Hub**: https://aihub.or.kr
- **Roboflow Universe**: https://universe.roboflow.com
- **COCO Dataset**: https://cocodataset.org

---

## 🎯 요약

1. **데이터 준비**: 항공사진 차량 이미지 + YOLO 형식 라벨
2. **환경 설정**: YOLOv8 설치 + GPU 설정
3. **학습 실행**: `train_yolo.py` 실행
4. **모델 적용**: `best.pt`를 우리 시스템에 적용
5. **성능 확인**: 정확도 측정 및 개선

**학습을 통해 15-30% 정확도 향상이 가능합니다!** 🚀

---

**Questions?**
📧 bu5119@hanyang.ac.kr

[⬆ 맨 위로](#-yolov8-차량-탐지-모델-학습-가이드)
