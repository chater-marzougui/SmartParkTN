"""YOLOv8 license plate detector training script.

Usage:
    python train_detector.py [--base yolov8n.pt] [--epochs 100] [--batch 16] [--imgsz 640]
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path

from ultralytics import YOLO


def train(
    data_yaml: str = "plates.yaml",
    base_model: str = "yolov8n.pt",
    epochs: int = 100,
    batch: int = 16,
    imgsz: int = 640,
    project: str = "runs/detect",
    name: str = "plate_detector",
):
    print(f"Training YOLOv8 plate detector")
    print(f"  base: {base_model}  epochs: {epochs}  batch: {batch}  imgsz: {imgsz}")

    model = YOLO(base_model)
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch,
        imgsz=imgsz,
        project=project,
        name=name,
        patience=15,
        save=True,
        device=0 if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu",
        workers=4,
        cache=True,
        augment=True,
        cos_lr=True,
        label_smoothing=0.05,
    )

    # Export best weights to models/
    best = Path(project) / name / "weights" / "best.pt"
    out_dir = Path("models")
    out_dir.mkdir(exist_ok=True)
    if best.exists():
        import shutil
        dst = out_dir / "plate_detector.pt"
        shutil.copy(best, dst)
        print(f"\nBest weights copied to: {dst}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="plates.yaml")
    parser.add_argument("--base", default="yolov8n.pt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--name", default="plate_detector")
    args = parser.parse_args()
    train(args.data, args.base, args.epochs, args.batch, args.imgsz, name=args.name)
