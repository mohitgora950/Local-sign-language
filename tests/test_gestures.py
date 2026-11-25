"""Synthetic-landmark tests (no webcam needed)."""
import sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from signlang import gestures as g

W = np.array([0.5, 0.8])
MCP = {1: (0.42, 0.55), 2: (0.50, 0.52), 3: (0.58, 0.55), 4: (0.65, 0.60)}

def make_hand(bits, orient):
    p = np.zeros((21, 3))
    p[0, :2] = W
    p[1, :2] = (0.43, 0.72); p[2, :2] = (0.38, 0.66); p[3, :2] = (0.34, 0.61)
    p[4, :2] = (0.24, 0.55) if bits & 16 else (0.45, 0.62)
    for f, base in zip((1, 2, 3, 4), (5, 9, 13, 17)):
        m = np.array(MCP[f]); ext = bits & (1 << (4 - f))
        p[base, :2] = m
        p[base + 1, :2] = m + (0, -0.07)
        p[base + 2, :2] = m + ((0, -0.16) if ext else (0, -0.03))
        p[base + 3, :2] = m + ((0, -0.22) if ext else (0, 0.03))
    ang = {"UP": 0, "RIGHT": 90, "DOWN": 180, "LEFT": 270}[orient]
    a = np.deg2rad(ang); R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    p[:, :2] = (p[:, :2] - W) @ R.T + W
    return p

seen = {}
for o in g.ORIENTS:
    for hs in ("Left", "Right"):
        for bits in range(32):
            # feed the RAW (swapped) MediaPipe label so corrected side == hs
            raw = "Right" if hs == "Left" else "Left"
            w, info = g.classify(make_hand(bits, o), raw)
            assert info["bits"] == format(bits, "05b") and info["orient"] == o and info["side"] == hs, (bits, o, hs, info)
            seen.setdefault(w, []).append((o, hs, bits))
print("distinct outputs:", len(seen))
print("Unknown cases:", len(seen.get("Unknown gesture", [])))
assert len(seen) >= 200, len(seen)

def one(bits, o="UP", hs="Right"):
    return g.classify(make_hand(bits, o), "Left" if hs == "Right" else "Right")[0]
assert one(0b11111) == "HELLO"
assert one(0b11001) == "I LOVE YOU"
assert one(0b10000) == "YES"
assert one(0b00000) == "FIST"
assert one(0b01100) == "PEACE"
assert one(0b00100) == "NOT HAPPY" and one(0b00001) == "RUDE" and one(0b00100, "DOWN") == "GO AWAY"   # professor mode
g.PROFESSOR_MODE = False
assert one(0b00100) == "FUCK YOU" and one(0b00001) == "ASSHOLE" and one(0b00100, "DOWN") == "GO TO HELL"
g.PROFESSOR_MODE = True
assert one(0b01000) == "ONE POINT"
# aspect ratio 4:3 must not change result
for b_ in (0b11111, 0b00100, 0b11001, 0b00000):
    h_ = make_hand(b_, "UP"); h_[:, 0] = (h_[:, 0] - 0.5) / (4/3) + 0.5
    assert g.classify(h_, "Left", aspect=4/3)[0] == g.classify(make_hand(b_, "UP"), "Left")[0]
# thumbs down
h = make_hand(0b10000, "UP"); h[4, :2] = (0.45, 0.95)
assert g.classify(h, "Left")[0] == "NO"
# handedness swap
assert g.hand_side("Right") == "Left" and g.hand_side("Left") == "Right"
# left vs right give different words for same pose
assert one(0b01011, "UP", "Left") != one(0b01011, "UP", "Right")
print("named + handedness tests OK")

# GestureState transition test (copy of app logic)
sys.path.insert(0, str(Path(__file__).parent))
import importlib.util
_root = Path(__file__).resolve().parents[1]
src = next(p for p in (_root / "scripts" / "sign_language_app.py", Path(__file__).parent / "sign_language_app.py") if p.exists()).read_text()
start = src.index("class GestureState"); end = src.index("tracker = None")
ns = {"time": time, "logger": __import__("logging").getLogger("t")}
exec(src[start:end], ns)
gs = ns["GestureState"](0.4)
t = 0.0; spoken = []
def feed(d, secs):
    global t
    for _ in range(int(secs * 30)):
        t += 1 / 30
        s, _x = gs.update(d, t)
        if s: spoken.append(d)
feed("HELLO", 1); feed("I LOVE YOU", 1); feed("HELLO", 1); feed("HELLO", 1)
feed(None, 1); feed("HELLO", 1); feed("WATER", 1); feed("Unknown gesture", .5); feed("WATER", 1)
print("spoken:", spoken)
assert spoken == ["HELLO", "I LOVE YOU", "HELLO", "HELLO", "WATER", "WATER"], spoken
print("GestureState OK")


# ---------- noise + smoothing + fast-gesture tests ----------
rng = np.random.default_rng(0)
def noisy(bits, o="UP", sigma=0.025):
    h = make_hand(bits, o).copy(); h[:, :2] += rng.normal(0, sigma, (21, 2)); return h

def accuracy(use_filter, target_bits, expect, n=600, sigma=0.025):
    c = g.GestureClassifier(); ok = 0
    for _ in range(n):
        if use_filter:
            w, _i = c.update(noisy(target_bits, sigma=sigma), "Left")
            ok += (w == expect)
        else:
            ok += (g.classify(noisy(target_bits, sigma=sigma), "Left")[0] == expect)
    return ok / n

for name, bits, exp in (("YES", 0b10000, "YES"), ("HELLO", 0b11111, "HELLO"), ("PINKY", 0b00001, "RUDE"), ("ILY", 0b11001, "I LOVE YOU")):
    print(f"{name}: raw per-frame {accuracy(False, bits, exp):.0%} -> filtered {accuracy(True, bits, exp):.0%}")
assert accuracy(True, 0b10000, "YES") > 0.9 and accuracy(True, 0b11111, "HELLO") > 0.9

# fast gestures: each pose shown for only ~0.25 s at 30 fps, no pause in between
c = g.GestureClassifier()
ns2 = {"time": time, "logger": __import__("logging").getLogger("t")}
exec(src[start:end], ns2)
gs2 = ns2["GestureState"](0.1)
src_poses = [0b11111, 0b11001, 0b10000, 0b01100, 0b11111]
spoken2 = []; t0 = 0.0
for bits in src_poses:
    for _ in range(8):                      # 8 frames = 0.27 s
        t0 += 1/30
        w, _i = c.update(noisy(bits, sigma=0.006), "Left")
        s_, _st = gs2.update(w, t0)
        if s_: spoken2.append(w)
print("fast sequence spoken:", spoken2)
assert spoken2 == ["HELLO", "I LOVE YOU", "YES", "PEACE", "HELLO"], spoken2
print("ALL OK")