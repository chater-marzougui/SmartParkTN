"""RTSP / webcam frame capture handler."""
from __future__ import annotations
import time
import threading
from typing import Optional
import cv2
import numpy as np


class StreamHandler:
    """Thread-safe RTSP/webcam capture with double-buffering."""

    def __init__(self, source: str | int, fps_limit: int = 10):
        self.source = source
        self.fps_limit = fps_limit
        self._cap: Optional[cv2.VideoCapture] = None
        self._frame: Optional[np.ndarray] = None
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self._cap = cv2.VideoCapture(self.source)
        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {self.source}")
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        if self._cap:
            self._cap.release()

    def _capture_loop(self):
        interval = 1.0 / self.fps_limit
        while self._running:
            t0 = time.time()
            ret, frame = self._cap.read()
            if ret:
                with self._lock:
                    self._frame = frame
            elapsed = time.time() - t0
            time.sleep(max(0.0, interval - elapsed))

    def read(self) -> Optional[np.ndarray]:
        """Return the latest frame (or None if not yet available)."""
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    @property
    def is_open(self) -> bool:
        return self._running and self._cap is not None and self._cap.isOpened()
