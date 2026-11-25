# Roadmap

| Step | What | Output | Viva point |
|---|---|---|---|
| 0 | Scaffold, licence, env check | this zip | Why MIT, why new MediaPipe API |
| 1 | Webcam hand tracking test | `scripts/test_hand_tracking.py` | What are 21 landmarks |
| 2 | Data collection tool (landmarks -> CSV, per person) | `scripts/collect_data.py` | Why own data, why person-wise split |
| 3 | Landmark normalisation + MLP training | `train.py`, metrics | Why wrist-relative + scale-normalised |
| 4 | Honest evaluation + confusion matrix | report tables | Data leakage explained |
| 5 | Real-time inference, smoothing, hold-to-confirm | `src/signlang/predictor.py` | Why smoothing, why threshold |
| 6 | UI (CustomTkinter) + text-to-speech thread | `app.py` | Threading, offline TTS |
| 7 | ONNX export + FPS/latency benchmark | benchmark table | Quantization |
| 8 | Report, PPT, viva Q&A | docs | Everything |
