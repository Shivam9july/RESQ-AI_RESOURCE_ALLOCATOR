from pathlib import Path
from typing import Any, Dict

import subprocess
import sys
import uuid

BASE_DIR = Path(__file__).resolve().parents[2]
DETECTION_TIMEOUT_SECONDS = 120

# Absolute path to your original CLI script.
PREDICT_FIRE_SCRIPT = Path(
    r"C:\Users\Shivam\AI_Based_Disaster_Relief_And_Management_System\predict_fire.py"
)


def load_model() -> Any:
    """
    Compatibility stub for API symmetry.

    The actual model is loaded inside the original `predict_fire.py` script
    when it runs, so this function simply verifies the script exists.
    """
    if not PREDICT_FIRE_SCRIPT.exists():
        raise FileNotFoundError(
            f"predict_fire.py not found at {PREDICT_FIRE_SCRIPT}. "
            "Make sure the original project is available at that location."
        )
    return None


def run_fire_detection(video_path: str) -> Dict[str, Any]:
    """
    Run fire detection by delegating to the original predict_fire.py script.

    This function spawns a subprocess:
        python predict_fire.py --input <video> --output <tmp_output> --display 0

    and returns a summary including the path to the generated output video.
    """
    load_model()

    video_path = str(video_path)
    output_dir = BASE_DIR / "detectors" / "city_fire" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_video = output_dir / f"fire_result_{uuid.uuid4().hex}.avi"

    cmd = [
        sys.executable,
        str(PREDICT_FIRE_SCRIPT),
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
            "stderr": f"Fire detection timed out after {DETECTION_TIMEOUT_SECONDS} seconds.",
        }

    success = completed.returncode == 0

    return {
        "video_path": video_path,
        "output_video": str(output_video) if success else None,
        "success": success,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }

