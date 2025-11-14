"""Response models for YOLO detections."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class Detection(BaseModel):
    label: str = Field(description="Detected object label")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    box: List[float] = Field(
        min_length=4,
        max_length=4,
        description="Bounding box coordinates [x1, y1, x2, y2]",
    )


class DetectionResponse(BaseModel):
    model: str
    confidence: float
    detections: List[Detection]
