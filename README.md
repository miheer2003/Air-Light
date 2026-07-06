# 💡 AirLight — AI Gesture-Controlled Smart Lighting

> Control your Wi-Fi smart bulb with nothing but hand gestures.

AirLight is a desktop application that uses your computer's webcam to recognize hand gestures in real time and control a Halonix (Tuya-based) Wi-Fi Smart RGB Bulb. It uses **OpenCV** and **MediaPipe** for fast, on-device gesture recognition and **TinyTuya** for local network bulb control — no cloud required.

---

## ✨ Features

| Gesture | Action |
|---------|--------|
| ✋ Open Palm | Turn bulb **ON** |
| ✊ Closed Fist | Turn bulb **OFF** |
| 🤏 Pinch (thumb + index) | Adjust **brightness** (distance = intensity) |
| ☝️ 1 Finger | Set color → **White** |
| ✌️ 2 Fingers | Set color → **Red** |
| 🤟 3 Fingers | Set color → **Green** |
| 🖖 4 Fingers | Set color → **Blue** |
| 👉 Swipe Right | Cycle to **next color** |
| 👈 Swipe Left | Cycle to **previous color** |

**Live UI** displays the webcam feed, detected gesture, brightness level, current color, power state, FPS, and bulb connection status.

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────────────┐
│  Webcam      │────▶│  HandTracker │────▶│ GestureClassifier  │
│ (camera.py)  │     │ (MediaPipe)  │     │  (finger states,   │
└─────────────┘     └──────────────┘     │   pinch, swipe)    │
                                          └────────┬───────────┘
                                                   │
                                          ┌────────▼───────────┐
                                          │  GestureMapper      │
                                          │  (maps gestures to  │
                                          │   bulb commands)     │
                                          └────────┬───────────┘
                                                   │
                                          ┌────────▼───────────┐
                                          │  BulbController     │
                                          │  (TinyTuya local    │──▶ 💡 Smart Bulb(s)
                                          │   network control)  │
                                          └────────────────────┘
```

---

## 📁 Project Structure

```
AirLight/
├── main.py                 # Application entry point & main loop
├── camera.py               # Threaded webcam capture
├── hand_tracker.py         # MediaPipe Tasks API hand landmark detection
├── gesture_detector.py     # Low-level finger state & movement analysis
├── gesture_classifier.py   # Classifies landmarks into semantic gestures
├── gesture_mapper.py       # Maps gestures to bulb commands with cooldowns
├── bulb_controller.py      # TinyTuya integration (supports multiple bulbs)
├── ui.py                   # CustomTkinter desktop GUI
├── config.py               # Configuration management (AppConfig dataclass)
├── config.json             # User configuration (auto-created on first run)
├── hand_landmarker.task    # MediaPipe hand landmark model
├── logger.py               # Application logging
├── utils.py                # Math helpers (EMA smoothing, etc.)
├── requirements.txt        # Python dependencies
└── tests/                  # Unit tests
    ├── test_gesture_classifier.py
    └── test_gesture_mapper.py
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.9+** (tested on macOS with Apple Silicon)
- **Webcam** (built-in or USB)
- **Halonix Smart RGB Bulb** (or any Tuya-compatible Wi-Fi bulb) — *optional, the app works in Mock Mode without a real bulb*

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/AirLight.git
cd AirLight

# 2. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python3 main.py
```

> **macOS Note:** The first time you run the app, macOS will ask for **camera permission** for Terminal. Click "OK" to allow it.

---

## 🔌 Connecting Your Smart Bulb

AirLight starts in **Mock Mode** by default — gestures are recognized and logged, but no real bulb commands are sent. Follow these steps to connect a real bulb.

### Step 1: Set Up Your Bulb on the Tuya App

1. **Download** the [Tuya Smart](https://apps.apple.com/app/tuya-smart/id1034649547) or [Smart Life](https://apps.apple.com/app/smart-life/id1115101477) app on your phone.
2. **Create an account** and sign in.
3. **Add your bulb**: Tap "+" → "Lighting" → "Bulb (Wi-Fi)". Follow the in-app instructions to connect your Halonix bulb to your home Wi-Fi network.
4. **Verify** the bulb works by toggling it on/off from the app.

### Step 2: Get Your Device Credentials (Device ID, IP, Local Key)

You need three pieces of information from the Tuya platform to control the bulb locally:

#### Option A: Using the `tinytuya` Wizard (Recommended)

1. **Create a Tuya IoT Developer Account**:
   - Go to [iot.tuya.com](https://iot.tuya.com) and sign up.
   - Create a new **Cloud Project** → Select your data center region (e.g., "Western America" or "India").
   - Subscribe to the **IoT Core** API.

2. **Link your Tuya Smart / Smart Life account**:
   - In your Cloud Project → **Devices** → **Link Tuya App Account**.
   - Open the Tuya Smart app → **Me** → Tap the top right **QR code icon** → Scan the QR code shown on the Tuya IoT website.

3. **Run the TinyTuya wizard**:
   ```bash
   python3 -m tinytuya wizard
   ```
   - Enter your **API Key** (Access ID) and **API Secret** from the Tuya IoT cloud project.
   - Enter your **Device ID** (found in Tuya IoT → Devices).
   - The wizard will output your device's **IP address**, **Device ID**, and **Local Key**.

#### Option B: Manual Lookup

1. Go to [iot.tuya.com](https://iot.tuya.com) → your Cloud Project → **Devices** → **All Devices**.
2. Find your bulb and note the **Device ID**.
3. Use the **API Explorer** → call `GET /v1.0/devices/{device_id}` to find the **Local Key**.
4. Find the bulb's **local IP** by checking your router's DHCP client list, or run:
   ```bash
   python3 -m tinytuya scan
   ```

### Step 3: Update `config.json`

Open `config.json` in the project root and fill in your credentials:

```json
{
    "devices": [
        {
            "ip": "192.168.1.XXX",
            "id": "YOUR_DEVICE_ID",
            "key": "YOUR_LOCAL_KEY"
        }
    ],
    "camera_index": 0,
    "default_brightness": 100,
    "mock_mode": false,
    "cooldown_ms": 300,
    "pinch_min_dist": 20,
    "pinch_max_dist": 200
}
```

> **Key change:** Set `"mock_mode": false` to enable real bulb control.

#### Multiple Bulbs

To control multiple bulbs simultaneously, add more entries to the `devices` array:

```json
{
    "devices": [
        {
            "ip": "192.168.1.10",
            "id": "bulb1_device_id",
            "key": "bulb1_local_key"
        },
        {
            "ip": "192.168.1.11",
            "id": "bulb2_device_id",
            "key": "bulb2_local_key"
        }
    ],
    "mock_mode": false
}
```

All gestures will be broadcast to every connected bulb at once.

### Step 4: Run AirLight

```bash
python3 main.py
```

The status panel will show `"2/2 Connected"` (or however many bulbs you configured) instead of `"MOCK MODE"`.

---

## ⚙️ Configuration Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `devices` | array | 1 default entry | List of Tuya bulb configurations (`ip`, `id`, `key`) |
| `camera_index` | int | `0` | Webcam device index (0 = default camera) |
| `default_brightness` | int | `100` | Initial brightness percentage |
| `mock_mode` | bool | `true` | If `true`, bulb commands are logged but not sent |
| `cooldown_ms` | int | `300` | Minimum time between gesture actions (ms) |
| `pinch_min_dist` | int | `20` | Minimum pixel distance for pinch gesture |
| `pinch_max_dist` | int | `200` | Maximum pixel distance for pinch gesture |

---

## 🧪 Running Tests

```bash
python3 -m pytest tests/ -v
```

The test suite validates gesture classification logic and the gesture-to-bulb-command mapping using mocked hardware.

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `module 'mediapipe' has no attribute 'solutions'` | You have MediaPipe ≥ 0.10.18 which uses the Tasks API. The app already handles this — make sure `hand_landmarker.task` exists in the project root. |
| `OpenCV: not authorized to capture video` | macOS blocked camera access. Open System Settings → Privacy & Security → Camera → Enable for Terminal. |
| `Failed to connect to bulb` | Verify the IP/ID/Key in `config.json`. Ensure your computer and bulb are on the same Wi-Fi network. Try running `python3 -m tinytuya scan` to find the bulb. |
| `Failed to grab frame` warnings | The webcam briefly lost a frame. This is normal. If persistent, try changing `camera_index` in `config.json`. |
| UI window not appearing | Check if the window is behind other windows. On macOS, look for it in the Dock. |
| Bulb not responding to gestures | Check the "Bulb Status" in the UI. If it says "0/1 Connected", the bulb connection failed. Click "Reconnect" or verify credentials. |

---

## 🗺️ Future Improvements

- 🎤 Voice Control
- 🔐 Face Recognition Authentication
- 🧠 Custom Gesture Training
- 🎵 Music Reactive Lighting
- ⏰ Scheduled Lighting Scenes

---

## 📄 License

MIT License
