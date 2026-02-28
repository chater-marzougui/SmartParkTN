"""DeepSORT tracker with per-track plate cache to reduce OCR load."""
from __future__ import annotations
from typing import Dict, Optional, Tuple
import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort


class PlateTracker:
    """Wrap DeepSORT and maintain a plate cache keyed by track ID."""

    def __init__(self, max_age: int = 30, n_init: int = 3):
        self._tracker = DeepSort(max_age=max_age, n_init=n_init)
        # track_id → (plate_normalized, confidence)
        self._plate_cache: Dict[int, Tuple[str, float]] = {}

    def update(
        self,
        detections: list,  # list of ([x1,y1,w,h], confidence, "plate")
        frame: np.ndarray,
    ) -> list:
        """Update tracker and return active tracks as list of Track objects."""
        if not detections:
            return []
        return self._tracker.update_tracks(detections, frame=frame)

    def cache_plate(self, track_id: int, plate: str, confidence: float):
        existing = self._plate_cache.get(track_id)
        if existing is None or confidence > existing[1]:
            self._plate_cache[track_id] = (plate, confidence)

    def get_plate(self, track_id: int) -> Optional[Tuple[str, float]]:
        return self._plate_cache.get(track_id)

    def remove_track(self, track_id: int):
        self._plate_cache.pop(track_id, None)

    def format_detection(self, x1, y1, x2, y2, conf) -> list:
        """Convert xyxy bbox to DeepSORT's expected [x1, y1, w, h] format."""
        return [[x1, y1, x2 - x1, y2 - y1], conf, "plate"]
