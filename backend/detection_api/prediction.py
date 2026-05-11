from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


INCIDENT_TYPES = ("fire", "flood", "crowd")

KEYWORD_WEIGHTS: dict[str, dict[str, float]] = {
    "fire": {
        "fire": 0.24,
        "flame": 0.22,
        "smoke": 0.16,
        "burn": 0.14,
        "wildfire": 0.18,
        "city_fire": 0.2,
    },
    "flood": {
        "flood": 0.24,
        "water": 0.16,
        "rain": 0.12,
        "river": 0.12,
        "inundation": 0.18,
        "overflow": 0.14,
    },
    "crowd": {
        "crowd": 0.2,
        "people": 0.14,
        "social": 0.14,
        "distance": 0.14,
        "queue": 0.1,
        "gathering": 0.14,
    },
}

TYPE_PRIORS = {
    "fire": 0.46,
    "flood": 0.44,
    "crowd": 0.38,
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".mpeg", ".mpg"}


@dataclass(frozen=True)
class PredictionResult:
    incident_type: str
    confidence: float
    severity: str
    affected_area: float
    affected_population: int
    meta: dict[str, Any]


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def detect_media_kind(filename: str, content_type: str | None = None) -> str:
    content_type = (content_type or "").lower()
    suffix = Path(filename).suffix.lower()

    if content_type.startswith("image/") or suffix in IMAGE_EXTENSIONS:
        return "image"
    if content_type.startswith("video/") or suffix in VIDEO_EXTENSIONS:
        return "video"
    return "unknown"


def _keyword_score(filename: str, incident_type: str) -> float:
    normalized = filename.lower().replace("-", "_").replace(" ", "_")
    return sum(
        weight
        for keyword, weight in KEYWORD_WEIGHTS[incident_type].items()
        if keyword in normalized
    )


def _size_score(size_bytes: int | None, media_kind: str) -> float:
    if not size_bytes or size_bytes <= 0:
        return 0.0

    size_mb = size_bytes / (1024 * 1024)
    expected_mb = 80 if media_kind == "video" else 8
    return clamp(size_mb / expected_mb, 0.0, 1.0) * 0.22


def _media_fit_score(media_kind: str, incident_type: str) -> float:
    if media_kind == "image":
        return {"fire": 0.13, "flood": 0.1, "crowd": 0.06}[incident_type]
    if media_kind == "video":
        return {"fire": 0.08, "flood": 0.12, "crowd": 0.16}[incident_type]
    return 0.03


def choose_incident_type(
    filename: str,
    media_kind: str,
    requested_type: str | None = None,
) -> tuple[str, dict[str, float]]:
    scores = {
        incident_type: TYPE_PRIORS[incident_type]
        + _keyword_score(filename, incident_type)
        + _media_fit_score(media_kind, incident_type)
        for incident_type in INCIDENT_TYPES
    }

    if requested_type in INCIDENT_TYPES:
        scores[requested_type] += 0.28

    incident_type = max(scores, key=scores.get)
    return incident_type, {key: round(value, 3) for key, value in scores.items()}


def estimate_severity(confidence: float, incident_type: str, media_kind: str) -> str:
    threshold_shift = 0.03 if incident_type == "crowd" and media_kind == "video" else 0

    if confidence >= 0.88 - threshold_shift:
        return "critical"
    if confidence >= 0.72 - threshold_shift:
        return "high"
    if confidence >= 0.52:
        return "medium"
    return "low"


def estimate_affected_area(
    incident_type: str,
    confidence: float,
    media_kind: str,
    size_bytes: int | None,
) -> float:
    base_area = {
        "fire": 0.35,
        "flood": 1.5,
        "crowd": 0.08,
    }[incident_type]

    media_multiplier = 1.18 if media_kind == "video" else 1.0
    size_multiplier = 1.0 + _size_score(size_bytes, media_kind)
    confidence_multiplier = 0.65 + confidence

    return round(max(0.05, base_area * media_multiplier * size_multiplier * confidence_multiplier), 3)


def estimate_population(incident_type: str, affected_area: float, confidence: float) -> int:
    density = {
        "fire": 620,
        "flood": 360,
        "crowd": 1350,
    }[incident_type]
    confidence_multiplier = 0.75 + (confidence * 0.5)
    return max(1, round(affected_area * density * confidence_multiplier))


def predict_from_media(
    *,
    filename: str,
    size_bytes: int | None,
    content_type: str | None = None,
    requested_type: str | None = None,
) -> PredictionResult:
    media_kind = detect_media_kind(filename, content_type)
    incident_type, class_scores = choose_incident_type(
        filename,
        media_kind,
        requested_type=requested_type,
    )

    confidence = TYPE_PRIORS[incident_type]
    confidence += _keyword_score(filename, incident_type)
    confidence += _media_fit_score(media_kind, incident_type)
    confidence += _size_score(size_bytes, media_kind)

    if requested_type == incident_type:
        confidence += 0.1

    confidence = round(clamp(confidence, 0.35, 0.97), 3)
    severity = estimate_severity(confidence, incident_type, media_kind)
    affected_area = estimate_affected_area(
        incident_type,
        confidence,
        media_kind,
        size_bytes,
    )
    affected_population = estimate_population(incident_type, affected_area, confidence)

    return PredictionResult(
        incident_type=incident_type,
        confidence=confidence,
        severity=severity,
        affected_area=affected_area,
        affected_population=affected_population,
        meta={
            "prediction_engine": "calibrated_media_heuristic_v2",
            "media_kind": media_kind,
            "class_scores": class_scores,
        },
    )


def predict_from_video_path(
    video_path: str,
    requested_type: str,
) -> PredictionResult:
    path = Path(video_path)
    size_bytes = path.stat().st_size if path.exists() and path.is_file() else None

    return predict_from_media(
        filename=path.name or video_path,
        size_bytes=size_bytes,
        content_type="video/*",
        requested_type=requested_type,
    )
