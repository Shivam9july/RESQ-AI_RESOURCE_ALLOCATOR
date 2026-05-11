from pathlib import Path
from typing import Any, Dict

import subprocess
import sys
import uuid

BASE_DIR = Path(__file__).resolve().parents[2]
DETECTION_TIMEOUT_SECONDS = 120

PREDICT_FLOOD_SCRIPT = Path(
    r"C:\Users\Shivam\AI_Based_Disaster_Relief_And_Management_System\predict_flood.py"
)


def load_model() -> Any:
    """Verify that the original flood prediction script exists."""
    if not PREDICT_FLOOD_SCRIPT.exists():
        raise FileNotFoundError(
            f"predict_flood.py not found at {PREDICT_FLOOD_SCRIPT}. "
            "Make sure the original project is available at that location."
        )
    return None


def run_flood_detection(video_path: str) -> Dict[str, Any]:
    """
    Run flood detection via the original predict_flood.py script.
    """
    load_model()

    video_path = str(video_path)
    output_dir = BASE_DIR / "detectors" / "flood" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_video = output_dir / f"flood_result_{uuid.uuid4().hex}.avi"

    cmd = [
        sys.executable,
        str(PREDICT_FLOOD_SCRIPT),
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
            "stderr": f"Flood detection timed out after {DETECTION_TIMEOUT_SECONDS} seconds.",
        }

    success = completed.returncode == 0

    return {
        "video_path": video_path,
        "output_video": str(output_video) if success else None,
        "success": success,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }

