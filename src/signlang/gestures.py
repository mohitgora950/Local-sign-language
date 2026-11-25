"""Rule-based gesture vocabulary: 5 finger states x 4 hand orientations x 2 hands = 256 gestures.

Each gesture = (which fingers are extended) + (which way the hand points) + (left/right hand).
This is a CUSTOM vocabulary, not real ASL. Pure numpy/python, no cv2 needed (testable).
"""
import numpy as np

# MediaPipe labels come out swapped on this setup -> flip them here (one place only).
SWAP_HANDEDNESS = True

# True = abusive words are replaced by clean ones (safe for professor/viva demo).
# Set False only for private fun use.
PROFESSOR_MODE = True
_CLEAN = {
    "FUCK YOU": "NOT HAPPY", "GO TO HELL": "GO AWAY", "ASSHOLE": "RUDE",
    "BULLSHIT": "NONSENSE", "SHUT UP": "QUIET", "DAMN IT": "OH NO",
    "WHAT THE HELL": "WHAT", "STUPID": "WRONG", "LOSER": "TRY AGAIN",
}

ORIENTS = ["UP", "DOWN", "LEFT", "RIGHT"]

# index = orient*64 + hand*32 + bits ; hand 0 = Left, 1 = Right
# bits = thumb*16 + index*8 + middle*4 + ring*2 + pinky
_W = """
STOP WATER FOOD HOME SCHOOL BOOK PEN PHONE FRIEND FAMILY MOTHER FATHER BROTHER SISTER BABY TEACHER
DOCTOR HELP PLEASE SORRY THANKS WELCOME GOOD BAD HAPPY SAD ANGRY TIRED HUNGRY THIRSTY SICK COLD
HOT BIG SMALL FAST SLOW OPEN CLOSE START FINISH WAIT COME GO SIT STAND WALK RUN SLEEP WAKE
EAT DRINK READ WRITE LISTEN SPEAK SEE LOOK THINK KNOW LEARN TEACH WORK PLAY LOVE LIKE WANT NEED
HAVE GIVE TAKE BRING SEND BUY SELL PAY MONEY PRICE FREE CHEAP COSTLY SHOP MARKET BANK OFFICE
TODAY TOMORROW YESTERDAY MORNING AFTERNOON EVENING NIGHT WEEK MONTH YEAR TIME CLOCK HOUR MINUTE NOW LATER
EARLY LATE ALWAYS NEVER SOMETIMES AGAIN MORE LESS ALL NONE SOME MANY FEW EVERY BOTH ONLY
ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN HUNDRED THOUSAND FIRST SECOND THIRD LAST NEXT
RED BLUE GREEN YELLOW BLACK WHITE ORANGE PINK PURPLE BROWN GREY GOLD SILVER LIGHT DARK BRIGHT DULL
SUN MOON STAR SKY CLOUD RAIN WIND SNOW FIRE EARTH RIVER SEA MOUNTAIN TREE FLOWER GARDEN FOREST
DOG CAT BIRD FISH COW HORSE GOAT SHEEP LION TIGER ELEPHANT MONKEY RABBIT SNAKE BEAR DEER ANT
BREAD RICE MILK TEA COFFEE SUGAR SALT FRUIT APPLE BANANA MANGO EGG MEAT VEGETABLE SOUP CAKE SNACK
BUS TRAIN CAR BIKE PLANE BOAT ROAD BRIDGE STATION TICKET MAP CITY VILLAGE COUNTRY WORLD ADDRESS
HEAD HAIR EYE EAR NOSE MOUTH TEETH HAND ARM LEG FOOT HEART BRAIN BODY FACE SKIN BONE
SHIRT PANTS SHOES HAT BAG WATCH GLASSES BELT SOCKS JACKET UMBRELLA KEY DOOR WINDOW TABLE CHAIR BED
COMPUTER MOUSE KEYBOARD SCREEN INTERNET EMAIL MESSAGE CALL VIDEO MUSIC SONG DANCE GAME MOVIE PHOTO CAMERA
QUESTION ANSWER RIGHT WRONG TRUE FALSE SAME DIFFERENT EASY HARD SAFE DANGER CAREFUL QUIET LOUD CLEAN DIRTY
""".split()
_W = _W[:256]
assert len(_W) == 256 and len(set(_W)) == 256, (len(_W), len(set(_W)))
WORDS = _W

# Well-known named gestures override table entries. key = (orientation, bits)
# bits = thumb index middle ring pinky  (1 = extended)
_NAMED = {
    ("UP", 0b11111): "HELLO",
    ("UP", 0b11001): "I LOVE YOU",
    ("UP", 0b10000): "YES",
    ("UP", 0b01100): "PEACE",
    ("UP", 0b01000): "ONE POINT",
    ("UP", 0b00000): "FIST",
    ("UP", 0b00100): "FUCK YOU",       # middle finger
    ("DOWN", 0b00100): "GO TO HELL",   # middle finger pointing down
    ("UP", 0b00001): "ASSHOLE",        # only pinky
    ("UP", 0b10100): "BULLSHIT",       # thumb + middle
    ("UP", 0b01001): "ROCK ON",        # index + pinky
    ("UP", 0b10001): "CALL ME",        # thumb + pinky
    ("UP", 0b11000): "LOSER",          # L shape
    ("UP", 0b01110): "THREE",          # index middle ring
    ("UP", 0b01111): "FOUR",
    ("UP", 0b00110): "SHUT UP",        # middle + ring
    ("UP", 0b00011): "DAMN IT",        # ring + pinky
    ("UP", 0b01101): "WHAT THE HELL",  # index ring pinky
    ("UP", 0b11100): "STUPID",         # thumb index middle
    ("UP", 0b10111): "OK",             # (also triggered by pinch rule below)
}


def _d(a, b):
    return float(np.linalg.norm(a[:2] - b[:2]))


def hand_side(handedness):
    """Return 'Left'/'Right' after correcting MediaPipe's swapped label."""
    if SWAP_HANDEDNESS:
        return "Left" if handedness == "Right" else "Right"
    return handedness


def finger_ratios(p):
    """[thumb, index, middle, ring, pinky] extension ratios (bigger = more extended)."""
    w = p[0]
    palm_w = max(_d(p[5], p[17]), 1e-3)
    r = [_d(p[4], p[17]) / palm_w]
    for tip, mcp in ((8, 5), (12, 9), (16, 13), (20, 17)):
        r.append(_d(p[tip], w) / max(_d(p[mcp], w), 1e-3))
    return r


# single-threshold (stateless) limits, and hysteresis (open, close) limits
_LIMIT = [1.30, 1.45, 1.45, 1.45, 1.45]
_OPEN = [1.42, 1.58, 1.58, 1.58, 1.55]
_CLOSE = [1.18, 1.32, 1.32, 1.32, 1.32]


def finger_bits(p):
    return [r > t for r, t in zip(finger_ratios(p), _LIMIT)]


def orientation(p):
    v = p[9, :2] - p[0, :2]  # wrist -> middle MCP (image coords, y down)
    if abs(v[1]) >= abs(v[0]):
        return "UP" if v[1] < 0 else "DOWN"
    return "LEFT" if v[0] < 0 else "RIGHT"


def classify(landmarks, handedness, aspect=1.0, ext=None):
    word, info = _classify(landmarks, handedness, aspect, ext)
    if PROFESSOR_MODE:
        word = _CLEAN.get(word, word)
    return word, info


def _classify(landmarks, handedness, aspect=1.0, ext=None):
    """Return (word, info). aspect = frame width / height (fixes stretched x distances)."""
    p = np.array(landmarks, dtype=float)
    p[:, 0] *= aspect
    palm = max(_d(p[0], p[9]), 1e-3)
    if ext is None:
        ext = finger_bits(p)
    bits = sum(int(e) << (4 - i) for i, e in enumerate(ext))
    orient = orientation(p)
    side = hand_side(handedness)
    info = dict(bits=format(bits, "05b"), orient=orient, side=side)

    # Thumbs-down: fist, thumb pointing below the wrist
    if bits == 0b10000 and float(p[4, 1] - p[0, 1]) > 0.35 * palm:
        return "NO", info
    # Thumbs-up must really point up
    if bits == 0b10000 and orient == "UP" and float(p[4, 1] - p[0, 1]) > -0.35 * palm:
        return "Unknown gesture", info
    # OK sign: thumb tip touches index tip, other three fingers extended
    if (bits & 0b00111) == 0b00111 and _d(p[4], p[8]) < 0.30 * palm and orient == "UP":
        return "OK", info

    if (orient, bits) in _NAMED:
        return _NAMED[(orient, bits)], info
    idx = ORIENTS.index(orient) * 64 + (1 if side == "Right" else 0) * 32 + bits
    return WORDS[idx], info


def all_gesture_names():
    names = list(WORDS)
    for w in list(_NAMED.values()) + ["NO", "OK"]:
        if w not in names:
            names.append(w)
    return names


class GestureClassifier:
    """Stateful: per-finger hysteresis + majority vote over the last few frames.

    update() returns (word, info). word == "UNCERTAIN" while frames disagree
    (e.g. hand is mid-motion) - the app must ignore it, not treat it as Unknown.
    """

    def __init__(self, window=5, min_share=0.6):
        self.state = [False] * 5
        self.window = window
        self.min_share = min_share
        self.recent = []
        self.sides = []
        self.last_info = {}

    def reset(self):
        self.state = [False] * 5
        self.recent = []
        self.sides = []

    def update(self, landmarks, handedness, aspect=1.0):
        p = np.array(landmarks, dtype=float)
        p[:, 0] *= aspect
        for i, r in enumerate(finger_ratios(p)):
            if r > _OPEN[i]:
                self.state[i] = True
            elif r < _CLOSE[i]:
                self.state[i] = False
        self.sides = (self.sides + [handedness])[-9:]
        handedness = max(set(self.sides), key=self.sides.count)   # stable label
        word, info = classify(landmarks, handedness, aspect, ext=list(self.state))
        self.last_info = info
        self.recent.append(word)
        self.recent = self.recent[-self.window:]
        top = max(set(self.recent), key=self.recent.count)
        if self.recent.count(top) / len(self.recent) >= self.min_share and len(self.recent) >= 3:
            return top, info
        return "UNCERTAIN", info