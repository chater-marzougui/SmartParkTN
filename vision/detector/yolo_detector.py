"""YOLOv8-based license plate and vehicle detector."""
from __future__ import annotations
import os
from typing import List, Tuple

import numpy as np
from ultralytics import YOLO


# Default model weights — override via env var PLATE_MODEL_PATH / VEHICLE_MODEL_PATH
PLATE_MODEL_PATH = os.getenv("PLATE_MODEL_PATH", "models/plate_detector.pt")
VEHICLE_MODEL_PATH = os.getenv("VEHICLE_MODEL_PATH", "models/vehicle_classifier.pt")

VEHICLE_CLASSES = ["car", "truck", "bus", "motorcycle", "van"]


class PlateDetector:
    """Detect license plates in a frame using YOLOv8."""

    def __init__(self, model_path: str = PLATE_MODEL_PATH, conf: float = 0.4):
        self.model = YOLO(model_path)
        self.conf = conf

    def detect(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """Run detection and return list of (x1, y1, x2, y2, confidence)."""
        results = self.model.predict(frame, conf=self.conf, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                detections.append((x1, y1, x2, y2, conf))
        return detections


class VehicleClassifier:
    """Classify vehicle type (car, truck, bus, motorcycle, van) using YOLOv8."""

    def __init__(self, model_path: str = VEHICLE_MODEL_PATH, conf: float = 0.3):
        if os.path.exists(model_path):
            self.model = YOLO(model_path)
        else:
            # Fall back to COCO-pretrained model for prototype
            self.model = YOLO("yolov8n.pt")
        self.conf = conf

    def classify(self, frame: np.ndarray) -> Tuple[str, float]:
        """Return (vehicle_type, confidence) for the whole frame."""
        results = self.model.predict(frame, conf=self.conf, verbose=False)
        best_class, best_conf = "car", 0.0
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = r.names.get(cls_id, "car").lower()
                conf = float(box.conf[0])
                # Map COCO names to our categories
                if any(v in cls_name for v in ["truck", "bus", "motorcycle", "van"]):
                    mapped = next(v for v in VEHICLE_CLASSES if v in cls_name)
                else:
                    mapped = "car"
                if conf > best_conf:
                    best_class, best_conf = mapped, conf
        return best_class, best_conf
