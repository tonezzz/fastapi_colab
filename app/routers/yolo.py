"""FastAPI routes for YOLO detections."""

from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.config import Settings, get_settings
from app.schemas.yolo import DetectionResponse
from app.services.yolo_runner import YoloRunner

router = APIRouter(prefix="/yolo", tags=["yolo"])


async def get_yolo_runner(request) -> YoloRunner:
    runner: YoloRunner | None = getattr(request.app.state, "yolo_runner", None)
    if runner is None:
        raise HTTPException(status_code=503, detail="YOLO runner not initialized.")
    return runner


SettingsDep = Annotated[Settings, Depends(get_settings)]
RunnerDep = Annotated[YoloRunner, Depends(get_yolo_runner)]


@router.post("/detect", response_model=DetectionResponse)
async def detect(
    file: UploadFile = File(...),
    confidence: Optional[float] = None,
    runner: RunnerDep = Depends(),
    settings: SettingsDep = Depends(),
) -> DetectionResponse:
    image_bytes = await file.read()
    try:
        detections = runner.detect(image_bytes, confidence=confidence)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return DetectionResponse(
        model=runner.model_name,
        confidence=confidence if confidence is not None else settings.yolo_confidence,
        detections=detections,
    )
