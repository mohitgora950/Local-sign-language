import sys
import time
import logging
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from signlang.hand_tracker import HandTracker, draw_hand
from signlang import gestures as G
from signlang.speech import SpeechController
from signlang.gestures import hand_side

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

speech = SpeechController()
speech.say("Ready")   # you should HEAR this at startup; if not, speech engine is the problem

HAND_GONE_STOP_SECONDS = 0.15   # hand missing this long -> silence immediately
hand_missing_since = None


class GestureState:
    """Debounce detections and emit each stable recognized transition once."""

    def __init__(self, stable_seconds=0.1):
        self.stable_seconds = stable_seconds
        self.candidate = None
        self.candidate_since = time.monotonic()
        self.stable = None
        self.last_spoken = None

    def update(self, detected, now=None):
        now = time.monotonic() if now is None else now

        if detected == "UNCERTAIN":      # frames disagree (fast motion): keep state
            return False, self.stable

        if detected != self.candidate:
            self.candidate = detected
            self.candidate_since = now
            logger.info("Gesture candidate changed: %s", detected or "No hand")

        if now - self.candidate_since < self.stable_seconds:
            return False, self.stable

        if detected == self.stable:
            return False, self.stable

        self.stable = detected
        if detected in (None, "Unknown gesture"):
            self.last_spoken = None
            logger.info("Gesture state cleared: %s", detected or "No hand")
            return False, self.stable

        if detected == self.last_spoken:
            return False, self.stable

        self.last_spoken = detected
        logger.info("Stable gesture transition: %s", detected)
        return True, detected


tracker = None
cap = None

gesture_state = GestureState()
classifier = G.GestureClassifier()
display_text = "No hand detected"
detected = "-"

try:
    tracker = HandTracker(max_hands=1)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Could not open webcam.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Webcam frame could not be read.")
            break

        frame = cv2.flip(frame, 1)
        hands = tracker.process(frame)
        now = time.monotonic()
        side = ""

        if hands:
            hand = hands[0]
            draw_hand(frame, hand)
            side = hand_side(hand.handedness)   # corrected Left/Right

            fh, fw = frame.shape[:2]
            detected, info = classifier.update(hand.landmarks, hand.handedness, aspect=fw / fh)
            spoke, stable = gesture_state.update(detected, now)
            display_text = stable if stable and detected in (stable, "UNCERTAIN") else "Checking..."

            logger.debug("Frame: raw=%s fixed=%s score=%.2f detected=%s info=%s stable=%s",
                         hand.handedness, side, hand.score, detected, info, stable or "None")

            hand_missing_since = None
            if spoke:
                speech.say(detected)          # replaces anything still being spoken
            elif stable in (None, "Unknown gesture") and detected == stable:
                speech.stop()
        else:
            display_text = "No hand detected"
            gesture_state.update(None, now)
            classifier.reset()
            if hand_missing_since is None:
                hand_missing_since = now
            if now - hand_missing_since >= HAND_GONE_STOP_SECONDS:
                speech.stop()                 # hand removed -> stop talking, drop queue

        cv2.putText(frame, "Gesture: " + display_text, (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Now: " + (detected if hands else "-"), (10, 165),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)
        if hands:
            cv2.putText(frame, "Your " + side.upper() + " hand", (10, 105),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, "Fingers(T I M R P): %s  Points: %s" % (info["bits"], info["orient"]),
                        (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)
        cv2.putText(frame, "Q = Quit | H = swap Left/Right label", (10, 135),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("Sign Language Translator", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("h"):
            G.SWAP_HANDEDNESS = not G.SWAP_HANDEDNESS
            logger.info("Left/Right label swap is now %s", G.SWAP_HANDEDNESS)

finally:
    if cap is not None:
        cap.release()
    if tracker is not None:
        tracker.close()
    cv2.destroyAllWindows()
    speech.close()