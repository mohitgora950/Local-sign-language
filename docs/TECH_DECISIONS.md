# Tech decisions (viva cheat-sheet)
Versions checked on PyPI on 08-Oct-2026.

| Tool | Latest | Our choice | Why / why not |
|---|---|---|---|
| MediaPipe | 1.1.0 | **Use, Tasks API (HandLandmarker)** | Legacy `mp.solutions.hands` is NOT in the 1.1.0 package (checked wheel contents). Older repos using `mp.solutions` break on new installs. Tasks API is the maintained one |
| OpenCV | 5.0.0.93 | opencv-contrib-python | MediaPipe depends on `opencv-contrib-python`; installing both variants causes conflicts |
| NumPy | 2.5.3 | Use | Needs Python >= 3.12 |
| PyTorch | 2.14.1 | Use (CPU build is enough) | Small landmark model trains in minutes on CPU |
| torchsummary | 1.5.1 (2018) | **Not used** | Abandoned. Use `torchinfo` |
| scikit-learn | 1.9.1 | Use | Metrics, group-wise split |
| CustomTkinter | 6.0.0 | Use | Modern UI over plain Tkinter, same learning curve |
| pyttsx3 | 2.99 | Use | Offline TTS, no API key |
| openai | 3.26.1 | **Not used** | Cloud + paid, not needed. Offline is a feature |
| ONNX Runtime | 1.30.0 | Later step | Fast CPU inference benchmark |
| Grad-CAM | 1.5.7 | Optional, only if we keep an image-CNN baseline | |
