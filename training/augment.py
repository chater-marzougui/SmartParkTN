"""Albumentations-based augmentation pipeline for plate images.

Usage:
    python augment.py --input data/raw --output data/augmented --count 5
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path

import cv2
import numpy as np
import albumentations as A
from tqdm import tqdm


AUGMENT_PIPELINE = A.Compose(
    [
        A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.6),
        A.GaussNoise(var_limit=(10, 50), p=0.4),
        A.MotionBlur(blur_limit=5, p=0.3),
        A.Rotate(limit=8, border_mode=cv2.BORDER_REPLICATE, p=0.5),
        A.Perspective(scale=(0.02, 0.06), p=0.3),
        A.RandomShadow(p=0.2),
        A.HueSaturationValue(hue_shift_limit=5, sat_shift_limit=20, val_shift_limit=20, p=0.3),
        A.CLAHE(clip_limit=3.0, p=0.3),
        A.Sharpen(alpha=(0.2, 0.5), lightness=(0.8, 1.0), p=0.3),
    ],
    bbox_params=A.BboxParams(format="yolo", label_fields=["class_labels"], min_visibility=0.6),
)


def load_yolo_labels(label_path: Path) -> list:
    if not label_path.exists():
        return []
    lines = label_path.read_text().strip().splitlines()
    return [list(map(float, l.split())) for l in lines if l]


def save_yolo_labels(label_path: Path, labels: list):
    lines = [" ".join(f"{v:.6f}" for v in row) for row in labels]
    label_path.write_text("\n".join(lines))


def augment_dataset(input_dir: str, output_dir: str, count: int = 5):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    (output_dir / "images").mkdir(parents=True, exist_ok=True)
    (output_dir / "labels").mkdir(parents=True, exist_ok=True)

    image_files = list((input_dir / "images").glob("*.jpg")) + list((input_dir / "images").glob("*.png"))
    print(f"Found {len(image_files)} source images. Generating {count}x augments each...")

    for img_path in tqdm(image_files, unit="img"):
        image = cv2.imread(str(img_path))
        if image is None:
            continue
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        label_path = input_dir / "labels" / (img_path.stem + ".txt")
        yolo_labels = load_yolo_labels(label_path)

        bboxes = [row[1:5] for row in yolo_labels]
        class_labels = [int(row[0]) for row in yolo_labels]

        for i in range(count):
            try:
                augmented = AUGMENT_PIPELINE(
                    image=image_rgb, bboxes=bboxes, class_labels=class_labels
                )
            except Exception:
                continue

            aug_name = f"{img_path.stem}_aug{i:03d}"
            out_img = cv2.cvtColor(augmented["image"], cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(output_dir / "images" / f"{aug_name}.jpg"), out_img)

            new_labels = [
                [cls] + list(box)
                for cls, box in zip(augmented["class_labels"], augmented["bboxes"])
            ]
            save_yolo_labels(output_dir / "labels" / f"{aug_name}.txt", new_labels)

    print(f"Done. Augmented data saved to: {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/labeled", help="Input YOLO dataset dir")
    parser.add_argument("--output", default="data/augmented", help="Output directory")
    parser.add_argument("--count", type=int, default=5, help="Augmentations per image")
    args = parser.parse_args()
    augment_dataset(args.input, args.output, args.count)
