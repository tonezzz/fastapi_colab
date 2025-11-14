"""Utilities for running Ultralytics YOLO predictions."""

from __future__ import annotations

from typing import List, Optional

import cv2
import numpy as np
from ultralytics import YOLO


class YoloRunner:
    """Lazy-loading wrapper around the Ultralytics YOLO model."""

    def __init__(self, model_name: str, *, confidence: float = 0.35) -> None:
        self.model_name = model_name
        self.confidence = confidence
        self._model: Optional[YOLO] = None

    def load(self) -> YOLO:
        if self._model is None:
            self._model = YOLO(self.model_name)
        return self._model

    def close(self) -> None:
        self._model = None

    def detect(self, image_bytes: bytes, confidence: Optional[float] = None) -> List[dict]:
        model = self.load()
        conf = confidence if confidence is not None else self.confidence
        image = self._decode_image(image_bytes)
        results = model.predict(source=image, conf=conf, verbose=False)

        detections: List[dict] = []
        for result in results:
            boxes = result.boxes
            names = result.names or {}
            if boxes is None:
                continue
            for box in boxes:
                cls_id = int(box.cls[0]) if box.cls is not None else -1
                label = names.get(cls_id, str(cls_id))
                score = float(box.conf[0]) if box.conf is not None else 0.0
                x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
                detections.append(
                    {
                        "label": label,
                        "confidence": score,
                        "box": [x1, y1, x2, y2],
                    }
                )
        return detections

    @staticmethod
    def _decode_image(image_bytes: bytes) -> np.ndarray:
        array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Unable to decode image bytes. Ensure a valid image file is provided.")
        return image
