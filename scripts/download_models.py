"""Download the MediaPipe hand landmarker model (~7 MB) into models/."""
import urllib.request
from pathlib import Path

URL = ("https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
       "hand_landmarker/float16/latest/hand_landmarker.task")
DEST = Path(__file__).resolve().parents[1] / "models" / "hand_landmarker.task"

if DEST.exists():
    print("Already present:", DEST)
else:
    DEST.parent.mkdir(exist_ok=True)
    print("Downloading", URL)
    urllib.request.urlretrieve(URL, DEST)
    print("Saved to", DEST, f"({DEST.stat().st_size/1e6:.1f} MB)")
