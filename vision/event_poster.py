"""Event poster — Redis-debounced HTTP POST to the backend /api/vision/plate-event."""
from __future__ import annotations
import os
import time
import base64
import logging

import redis
import requests
import numpy as np
import cv2

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEBOUNCE_SECONDS = int(os.getenv("DEBOUNCE_SECONDS", "10"))
BACKEND_API_KEY = os.getenv("VISION_API_KEY", "vision-internal-key")

logger = logging.getLogger(__name__)


class EventPoster:
    """Post plate events to backend with Redis-based per-plate debounce."""

    def __init__(self):
        self._redis = redis.from_url(REDIS_URL, decode_responses=True)
        self._session = requests.Session()
        self._session.headers["X-Vision-Key"] = BACKEND_API_KEY

    def should_post(self, plate_normalized: str) -> bool:
        """Return True if enough time has passed since last post for this plate."""
        key = f"debounce:{plate_normalized}"
        if self._redis.get(key):
            return False
        return True

    def mark_posted(self, plate_normalized: str):
        key = f"debounce:{plate_normalized}"
        self._redis.setex(key, DEBOUNCE_SECONDS, "1")

    def post_event(
        self,
        plate: str,
        plate_normalized: str,
        gate_id: str,
        ocr_confidence: float,
        vehicle_type: str,
        snapshot: np.ndarray | None = None,
    ) -> dict | None:
        if not self.should_post(plate_normalized):
            logger.debug("Debounced plate: %s", plate_normalized)
            return None

        payload = {
            "plate": plate,
            "plate_normalized": plate_normalized,
            "gate_id": gate_id,
            "ocr_confidence": ocr_confidence,
            "vehicle_type": vehicle_type,
        }

        if snapshot is not None:
            _, buf = cv2.imencode(".jpg", snapshot, [cv2.IMWRITE_JPEG_QUALITY, 85])
            payload["image_b64"] = base64.b64encode(buf).decode()

        try:
            resp = self._session.post(
                f"{BACKEND_URL}/api/vision/plate-event",
                json=payload,
                timeout=5,
            )
            resp.raise_for_status()
            self.mark_posted(plate_normalized)
            logger.info("Posted event for %s → %s", plate_normalized, resp.json().get("decision"))
            return resp.json()
        except Exception as e:
            logger.error("Failed to post event for %s: %s", plate_normalized, e)
            return None
