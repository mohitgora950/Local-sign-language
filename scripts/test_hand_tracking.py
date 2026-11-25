"""Step 1: webcam + hand skeleton. Press q to quit."""
import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from signlang.hand_tracker import HandTracker, draw_hand  # noqa: E402

tracker = HandTracker(max_hands=1)
cap = cv2.VideoCapture(0)
prev = time.perf_counter()

while True:
    ok, frame = cap.read()
    if not ok:
        break
     # frame = cv2.flip(frame, 1)                  # mirror view, feels natural
    for hand in tracker.process(frame):
        draw_hand(frame, hand)
        cv2.putText(frame, f"{hand.handedness} {hand.score:.2f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    now = time.perf_counter()
    cv2.putText(frame, f"FPS {1/(now-prev):.0f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    prev = now
    cv2.imshow("Hand tracking test (q to quit)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
tracker.close()
cv2.destroyAllWindows()
