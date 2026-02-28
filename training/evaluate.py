"""Evaluation script — computes mAP for detector and character/plate accuracy for OCR.

Usage:
    # Evaluate detector
    python evaluate.py --mode detector --model models/plate_detector.pt --data plates.yaml

    # Evaluate OCR on a test image directory
    python evaluate.py --mode ocr --images data/ocr/test/images --labels data/ocr/test/labels
"""
from __future__ import annotations
import argparse
from pathlib import Path

import numpy as np


# ─── Detector Evaluation ────────────────────────────────────────────────────


def evaluate_detector(model_path: str, data_yaml: str):
    from ultralytics import YOLO

    print(f"\nEvaluating detector: {model_path}")
    model = YOLO(model_path)
    metrics = model.val(data=data_yaml, verbose=True)

    print("\n── Detector Metrics ──────────────────────────────")
    print(f"  mAP@0.50       : {metrics.box.map50:.4f}")
    print(f"  mAP@[.50:.95]  : {metrics.box.map:.4f}")
    print(f"  Precision      : {metrics.box.mp:.4f}")
    print(f"  Recall         : {metrics.box.mr:.4f}")
    print("──────────────────────────────────────────────────")
    return metrics


# ─── OCR Evaluation ─────────────────────────────────────────────────────────


def cer(pred: str, truth: str) -> float:
    """Character Error Rate (Levenshtein distance / len(truth))."""
    if not truth:
        return 0.0 if not pred else 1.0
    m, n = len(pred), len(truth)
    dp = np.arange(n + 1)
    for i in range(1, m + 1):
        prev = dp.copy()
        dp[0] = i
        for j in range(1, n + 1):
            dp[j] = prev[j - 1] if pred[i - 1] == truth[j - 1] else 1 + min(prev[j - 1], prev[j], dp[j - 1])
    return dp[n] / n


def evaluate_ocr(images_dir: str, labels_dir: str):
    import cv2
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from vision.ocr.ocr_engine import read_plate
    from vision.ocr.postprocessor import normalize_raw_ocr

    images_path = Path(images_dir)
    labels_path = Path(labels_dir)
    image_files = sorted(images_path.glob("*.jpg")) + sorted(images_path.glob("*.png"))

    cer_scores, exact_matches = [], 0
    print(f"\nEvaluating OCR on {len(image_files)} images...")

    for img_path in image_files:
        gt_file = labels_path / (img_path.stem + ".txt")
        if not gt_file.exists():
            continue
        gt = gt_file.read_text().strip().upper()
        frame = cv2.imread(str(img_path))
        if frame is None:
            continue
        raw, _ = read_plate(frame)
        pred = normalize_raw_ocr(raw)
        c = cer(pred, gt)
        cer_scores.append(c)
        if pred == gt:
            exact_matches += 1

    if not cer_scores:
        print("No samples evaluated.")
        return

    print("\n── OCR Metrics ───────────────────────────────────")
    print(f"  Samples evaluated : {len(cer_scores)}")
    print(f"  Exact plate match : {exact_matches / len(cer_scores) * 100:.1f}%")
    print(f"  Mean CER          : {np.mean(cer_scores) * 100:.2f}%")
    print(f"  Median CER        : {np.median(cer_scores) * 100:.2f}%")
    print("──────────────────────────────────────────────────")


# ─── Main ────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["detector", "ocr"], required=True)
    # Detector args
    parser.add_argument("--model", default="models/plate_detector.pt")
    parser.add_argument("--data", default="plates.yaml")
    # OCR args
    parser.add_argument("--images", default="data/ocr/test/images")
    parser.add_argument("--labels", default="data/ocr/test/labels")
    args = parser.parse_args()

    if args.mode == "detector":
        evaluate_detector(args.model, args.data)
    else:
        evaluate_ocr(args.images, args.labels)
