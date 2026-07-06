<div align="center">
  <h1>💡 AirLight</h1>
  <p><b>AI Gesture-Controlled Smart Lighting OS</b></p>

  [![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
  [![OpenCV](https://img.shields.io/badge/OpenCV-Native%20HUD-green.svg)](https://opencv.org)
  [![MediaPipe](https://img.shields.io/badge/MediaPipe-Tasks%20API-orange.svg)](https://developers.google.com/mediapipe)
  [![TinyTuya](https://img.shields.io/badge/TinyTuya-Local%20Network-red.svg)](https://github.com/jasonacox/tinytuya)
</div>

<br/>

**AirLight** is a modern, headless AI application that uses your computer's webcam to recognize hand gestures in real-time and control Tuya-based Wi-Fi Smart RGB Bulbs. Instead of reaching for your phone or a physical switch, you can now adjust your room's ambiance seamlessly with a wave of your hand. 

AirLight features a blazing-fast, pure-Python native OpenCV Heads-Up Display (HUD) with a minimalist Gen-Z "Hacker" aesthetic (Acid Green & Dark Gray). It operates purely locally, ensuring instantaneous response times with zero cloud latency.

---

## ✨ Key Features

- **Touchless Control**: Turn lights on/off, change colors, adjust brightness, and trigger scenes using intuitive AI hand tracking.
- **Gen-Z Tech Native HUD**: A high-contrast, minimalist heads-up display drawn directly over the camera feed, featuring custom targeting brackets and skeletal tracking.
- **Local Network Execution**: Connects directly to your bulb via your local Wi-Fi router (no cloud round-trips), resulting in command execution times of < 400ms.
- **Low Resource Footprint**: Built without heavy Electron wrappers or browser tabs. A specialized thread-sleep loop ensures it idles smoothly in the background without maxing out CPU cores.

---

## 🛠️ Installation

### 1. Clone & Install Dependencies
Ensure you have Python 3.9+ installed.

```bash
git clone https://github.com/miheer2003/Air-Light.git
cd Air-Light
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Tuya Credentials
You need to provide your Tuya bulb's local credentials. Open `config.json` and update it with your device details:

```json
{
  "bulb": {
    "ip": "192.168.1.100",
    "device_id": "YOUR_DEVICE_ID",
    "local_key": "YOUR_LOCAL_KEY",
    "version": 3.3
  },
  "mock_mode": false
}
```
*(If you do not have a bulb yet, you can leave `"mock_mode": true` to test the AI engine virtually).*

---

## 🚀 Usage

Run the application directly via the terminal:

```bash
python3 main.py
```

The native OpenCV Heads-Up Display will instantly launch. Perform gestures in front of your webcam to control the light. 
To exit the application, simply press `q` or `ESC` while focused on the camera window.

---

## 🖐️ Gesture Mapping

| Emoji | Gesture | Action |
|-------|---------|--------|
| 🖐️ | **Open Palm** | Turn bulb **ON** |
| ✊ | **Closed Fist** | Turn bulb **OFF** |
| 👆 | **Swipe Up/Down** | Adjust **Brightness** (± 15%) |
| 🤏 | **Pinch** | Adjust **Density / Saturation** |
| ☝️ | **1 Finger** | Set Color: **White** |
| ✌️ | **2 Fingers** | Set Color: **Red** |
| 🤟 | **3 Fingers** | Set Color: **Green** |
| 🖐 | **4 Fingers** | Set Color: **Blue** |
| 👌 | **OK Sign** | Set Scene: **Leisure** |
| 👉 | **Swipe Right** | Cycle to **next color** |
| 👈 | **Swipe Left** | Cycle to **previous color** |

---

## 🧠 Architecture Overview

AirLight is built using a highly decoupled architecture to ensure smooth video playback without blocking the AI inference or hardware I/O.

1. **AI Core (`hand_tracker.py`, `gesture_classifier.py`)**: Utilizes Google's MediaPipe Tasks API for blazing fast hand-landmark detection.
2. **Controller (`core.py`, `gesture_mapper.py`)**: Acts as the central state machine. Translates string-based gestures into concrete actions.
3. **Hardware Interface (`bulb_controller.py`)**: Wraps the `tinytuya` library to send raw byte commands to the physical bulb on the local network.
4. **Native OS (`main.py`)**: A native OpenCV rendering pipeline that intercepts the camera feed and overlays the Acid Green Tech HUD.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! 
Feel free to check the [issues page](https://github.com/miheer2003/Air-Light/issues).

## 📝 License

This project is open-source and available under the MIT License.

---
<div align="center">
  <i>Built with ❤️ using MediaPipe and TinyTuya.</i>
</div>
