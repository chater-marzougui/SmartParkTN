"""EasyOCR fine-tuning script for Tunisian plate characters.

EasyOCR uses a CRNN backend. This script converts a plate text dataset
(image + ground truth text pairs) into the EasyOCR training format
and launches training.

Usage:
    python train_ocr.py --data data/ocr --output models/ocr_model --epochs 50
"""
from __future__ import annotations
import argparse
import json
import os
import shutil
from pathlib import Path

import cv2
import numpy as np


def build_gt_file(data_dir: Path, split: str = "train") -> int:
    """Build EasyOCR ground truth JSON from a directory of (image, .txt) pairs."""
    image_dir = data_dir / split / "images"
    label_dir = data_dir / split / "labels"
    gt_file = data_dir / split / "gt.json"

    if not image_dir.exists():
        print(f"[WARN] {image_dir} not found, skipping {split} split.")
        return 0

    records = []
    for img_path in sorted(image_dir.glob("*")):
        if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        txt_path = label_dir / (img_path.stem + ".txt")
        if not txt_path.exists():
            continue
        text = txt_path.read_text().strip()
        records.append({"filename": str(img_path.relative_to(data_dir / split)), "words": text})

    with open(gt_file, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"[{split}] {len(records)} samples written to {gt_file}")
    return len(records)


def train_ocr(data_dir: str, output_dir: str, epochs: int = 50):
    """Invoke EasyOCR's training pipeline."""
    data_path = Path(data_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    n_train = build_gt_file(data_path, "train")
    n_val = build_gt_file(data_path, "val")

    if n_train == 0:
        print("No training data found. Populate data/ocr/train/images and data/ocr/train/labels first.")
        return

    # EasyOCR training via its CLI (must be installed in venv)
    train_cmd = (
        f"python -m easyocr.scripts.train "
        f"--train_data_dir {data_path / 'train'} "
        f"--val_data_dir {data_path / 'val'} "
        f"--saved_model {output_path / 'model'} "
        f"--num_iter {epochs * n_train} "
        f"--lang ar "
    )
    print(f"\nRunning: {train_cmd}\n")
    os.system(train_cmd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/ocr")
    parser.add_argument("--output", default="models/ocr_model")
    parser.add_argument("--epochs", type=int, default=50)
    args = parser.parse_args()
    train_ocr(args.data, args.output, args.epochs)
