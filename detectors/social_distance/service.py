from pathlib import Path
from typing import Any, Dict, List, Tuple

import subprocess
import sys
import uuid

BASE_DIR = Path(__file__).resolve().parents[2]
DETECTION_TIMEOUT_SECONDS = 120
YOLO_DIR = BASE_DIR / "detectors" / "social_distance" / "yolo-coco"
WEIGHTS_PATH = YOLO_DIR / "yolov3.weights"
CONFIG_PATH = YOLO_DIR / "yolov3.cfg"
NAMES_PATH = YOLO_DIR / "coco.names"

SOCIAL_DISTANCE_SCRIPT = Path(
    r"C:\Users\Shivam\AI_Based_Disaster_Relief_And_Management_System\Social-Distance-Detector\social_distance_detector.py"
)


def verify_yolo_files() -> None:
    """Ensure YOLOv3 files exist in the expected directory."""
    missing: List[Tuple[str, Path]] = []
    for label, path in [
        ("weights", WEIGHTS_PATH),
        ("config", CONFIG_PATH),
        ("class names", NAMES_PATH),
    ]:
        if not path.exists():
            missing.append((label, path))

    if missing:
        missing_str = ", ".join(f"{label}: {path}" for label, path in missing)
        raise FileNotFoundError(
            "Missing YOLOv3 files. Expected the following to exist – "
            f"{missing_str}. Copy them from your model Drive folder."
        )


def load_model() -> Any:
    """Verify that YOLO files and the original script are available."""
    verify_yolo_files()
    if not SOCIAL_DISTANCE_SCRIPT.exists():
        raise FileNotFoundError(
            f"social_distance_detector.py not found at {SOCIAL_DISTANCE_SCRIPT}. "
            "Make sure the original project is available at that location."
        )
    return None


def run_social_distance_detection(video_path: str) -> Dict[str, Any]:
    """
    Run social distance / crowd detection on a video by delegating to the
    original social_distance_detector.py script.
    """
    load_model()

    video_path = str(video_path)
    output_dir = BASE_DIR / "detectors" / "social_distance" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_video = output_dir / f"social_distance_{uuid.uuid4().hex}.avi"

    cmd = [
        sys.executable,
        str(SOCIAL_DISTANCE_SCRIPT),
        "--input",
        video_path,
        "--output",
        str(output_video),
        "--display",
        "0",
    ]

    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=DETECTION_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "video_path": video_path,
            "output_video": None,
            "success": False,
            "stdout": exc.stdout or "",
            "stderr": (
                "Social-distance detection timed out after "
                f"{DETECTION_TIMEOUT_SECONDS} seconds."
            ),
        }

    success = completed.returncode == 0

    return {
        "video_path": video_path,
        "output_video": str(output_video) if success else None,
        "success": success,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }

