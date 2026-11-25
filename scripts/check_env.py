"""Environment check. Run: python scripts/check_env.py"""
import platform
import sys
from importlib import metadata
from pathlib import Path

print("Python  :", sys.version.split()[0], "|", platform.platform())
if sys.version_info < (3, 12):
    print("  WARNING: Python 3.12+ recommended (numpy 2.5 needs it)")

pkgs = ["mediapipe", "opencv-contrib-python", "numpy", "pandas", "scikit-learn",
        "matplotlib", "torch", "torchvision", "torchinfo", "pyttsx3",
        "customtkinter", "Pillow"]
print("\nPackages:")
for p in pkgs:
    try:
        print(f"  {p:22} {metadata.version(p)}")
    except metadata.PackageNotFoundError:
        print(f"  {p:22} NOT INSTALLED")

try:
    import torch
    print("\nTorch CUDA available:", torch.cuda.is_available())
except Exception as e:
    print("\nTorch import failed:", e)

try:
    import mediapipe as mp
    from mediapipe.tasks.python import vision
    ok = hasattr(vision, "HandLandmarker")
    print("MediaPipe Tasks HandLandmarker:", "OK" if ok else "MISSING",
          "| legacy mp.solutions:", hasattr(mp, "solutions"))
except Exception as e:
    print("MediaPipe import failed:", e)

model = Path(__file__).resolve().parents[1] / "models" / "hand_landmarker.task"
print("Model file:", "found" if model.exists() else "missing -> run scripts/download_models.py")

try:
    import cv2
    cap = cv2.VideoCapture(0)
    ok, frame = cap.read()
    cap.release()
    print("Webcam  :", f"OK {frame.shape[1]}x{frame.shape[0]}" if ok else "cannot read frame")
except Exception as e:
    print("Webcam check failed:", e)

try:
    import pyttsx3
    eng = pyttsx3.init()
    print("TTS     : engine OK, voices:", len(eng.getProperty("voices")))
except Exception as e:
    print("TTS check failed:", e)
