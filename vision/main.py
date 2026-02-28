"""Vision pipeline entry point — wires detector, OCR, tracker, and poster."""
from __future__ import annotations
import os
import logging
import time
import numpy as np

from vision.camera.stream_handler import StreamHandler
from vision.detector.yolo_detector import PlateDetector, VehicleClassifier
from vision.ocr.ocr_engine import read_plate
from vision.ocr.postprocessor import post_process
from vision.tracker.deepsort_tracker import PlateTracker
from vision.event_poster import EventPoster

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("vision.main")

GATE_ID = os.getenv("GATE_ID", "gate_01")
STREAM_SOURCE = os.getenv("STREAM_SOURCE", "0")  # "0" = default webcam, or RTSP URL
OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.6"))


def run_pipeline():
    logger.info("Starting TunisPark Vision Pipeline — Gate: %s", GATE_ID)

    # Parse stream source (int for webcam index, str for RTSP URL)
    source = int(STREAM_SOURCE) if STREAM_SOURCE.isdigit() else STREAM_SOURCE

    stream = StreamHandler(source, fps_limit=10)
    detector = PlateDetector()
    classifier = VehicleClassifier()
    tracker = PlateTracker()
    poster = EventPoster()

    stream.start()
    logger.info("Stream opened: %s", STREAM_SOURCE)

    try:
        while True:
            frame = stream.read()
            if frame is None:
                time.sleep(0.05)
                continue

            # 1. Detect plates
            plate_boxes = detector.detect(frame)
            if not plate_boxes:
                continue

            # 2. Format for tracker
            tracker_inputs = [
                tracker.format_detection(x1, y1, x2, y2, conf)
                for (x1, y1, x2, y2, conf) in plate_boxes
            ]
            tracks = tracker.update(tracker_inputs, frame)

            for track in tracks:
                if not track.is_confirmed():
                    continue
                track_id = track.track_id
                ltrb = track.to_ltrb()
                x1, y1, x2, y2 = map(int, ltrb)
                # Clamp to frame
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                crop = frame[y1:y2, x1:x2]
                if crop.size == 0:
                    continue

                # 3. Run OCR on crop
                raw_text, ocr_conf = read_plate(crop)
                result = post_process(raw_text, ocr_conf)

                if not result["valid"] or result["confidence"] < OCR_CONFIDENCE_THRESHOLD:
                    continue

                # 4. Update plate cache with best reading
                tracker.cache_plate(track_id, result["normalized"], result["confidence"])
                cached = tracker.get_plate(track_id)
                if cached is None:
                    continue

                plate_normalized, best_conf = cached

                # 5. Classify vehicle type from whole frame
                vehicle_type, _ = classifier.classify(frame)

                # 6. Post event (debounced)
                poster.post_event(
                    plate=result["plate"],
                    plate_normalized=plate_normalized,
                    gate_id=GATE_ID,
                    ocr_confidence=best_conf,
                    vehicle_type=vehicle_type,
                    snapshot=frame,
                )

    except KeyboardInterrupt:
        logger.info("Shutting down vision pipeline...")
    finally:
        stream.stop()


if __name__ == "__main__":
    run_pipeline()
