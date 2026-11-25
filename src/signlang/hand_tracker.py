"""Thin wrapper over MediaPipe Tasks HandLandmarker (MediaPipe >= 1.x).

Why a wrapper: the rest of the project only needs "frame in -> landmarks out",
so if MediaPipe's API changes again we only edit this file.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision

# 21 landmark pairs forming the hand skeleton (index numbers as in MediaPipe docs)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),            # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),            # index
    (5, 9), (9, 10), (10, 11), (11, 12),       # middle
    (9, 13), (13, 14), (14, 15), (15, 16),     # ring
    (13, 17), (17, 18), (18, 19), (19, 20),    # pinky
    (0, 17),                                   # palm edge
]

DEFAULT_MODEL = Path(__file__).resolve().parents[2] / "models" / "hand_landmarker.task"


@dataclass
class HandResult:
    landmarks: np.ndarray   # shape (21, 3): x, y normalised to [0,1], z relative depth
    handedness: str         # "Left" or "Right" (as seen by the camera image)
    score: float            # handedness confidence


class HandTracker:
    def __init__(self, model_path: Path | str = DEFAULT_MODEL, max_hands: int = 1,
                 detection_conf: float = 0.5, tracking_conf: float = 0.5):
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(
                f"{model_path} not found. Run: python scripts/download_models.py")
        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_conf,
            min_hand_presence_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._t0 = time.monotonic()

    def process(self, frame_bgr: np.ndarray) -> list[HandResult]:
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        ts_ms = int((time.monotonic() - self._t0) * 1000)   # must increase every call
        res = self._landmarker.detect_for_video(mp_image, ts_ms)
        out: list[HandResult] = []
        for lms, hand in zip(res.hand_landmarks, res.handedness):
            arr = np.array([[p.x, p.y, p.z] for p in lms], dtype=np.float32)
            out.append(HandResult(arr, hand[0].category_name, float(hand[0].score)))
        return out

    def close(self) -> None:
        self._landmarker.close()


def draw_hand(frame_bgr: np.ndarray, hand: HandResult) -> None:
    """Draw skeleton and joints on the frame in place."""
    h, w = frame_bgr.shape[:2]
    pts = [(int(x * w), int(y * h)) for x, y, _ in hand.landmarks]
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame_bgr, pts[a], pts[b], (0, 255, 0), 2)
    for p in pts:
        cv2.circle(frame_bgr, p, 4, (0, 0, 255), -1)
