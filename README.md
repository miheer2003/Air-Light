# AirLight – AI Gesture Controlled Smart Lighting System

AirLight is a desktop application that uses your computer's webcam to recognize hand gestures and control a Halonix (Tuya-based) Wi-Fi Smart RGB Bulb in real time. It uses OpenCV and MediaPipe for fast, on-device gesture recognition and TinyTuya for local network bulb control.

## Project Overview

AirLight maps specific hand gestures (like an open palm, closed fist, or finger counts) to smart bulb commands (Power On/Off, Brightness, Color). It features a modern desktop UI built with CustomTkinter that displays live webcam feed, recognized gestures, and bulb status.

### Features
- **Power Control**: Open Palm (Turn ON), Closed Fist (Turn OFF)
- **Brightness Control**: Pinch gesture (distance between thumb and index)
- **Color Control**: 
  - 1 Finger: White
  - 2 Fingers: Red
  - 3 Fingers: Green
  - 4 Fingers: Blue
  - 5 Fingers: Yellow
- **Color Swiping**: Swipe Right (Next Color), Swipe Left (Previous Color)
- **Live UI**: Real-time webcam feed, gesture feedback, connection status, and logs.

## Architecture Diagram
*(Placeholder for Architecture Diagram)*

## Folder Structure
```
AirLight/
│
├── main.py                # Application entry point
├── camera.py              # Manages webcam capture in a separate thread
├── hand_tracker.py        # Wraps MediaPipe for hand landmark extraction
├── gesture_detector.py    # Analyzes landmarks to detect finger states/movement
├── gesture_classifier.py  # Classifies raw states into discrete gestures
├── gesture_mapper.py      # Maps classified gestures to bulb actions
├── bulb_controller.py     # TinyTuya integration for local bulb control
├── ui.py                  # CustomTkinter modern GUI
├── config.py              # Handles loading/saving settings
├── logger.py              # Application logging setup
├── utils.py               # Math helpers and smoothing algorithms
├── assets/                # Images and icons
├── docs/                  # Additional documentation
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/AirLight.git
   cd AirLight
   ```

2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

To control your Halonix/Tuya smart bulb locally, you need its `Device IP`, `Device ID`, and `Local Key`.

1. Run the Tuya IoT setup (see TinyTuya documentation) to extract your `Device ID` and `Local Key`.
2. Edit the `config.json` (created on first run) with your bulb's details, or use the Settings menu in the app UI.

## Running

Start the application by running:
```bash
python main.py
```

## Screenshots Placeholder
*(Add screenshots of the CustomTkinter UI here)*

## Future Improvements
- Voice Control
- Face Recognition Authentication
- Custom Gesture Training
- Music Reactive Lighting
- Schedule Lights
- Multiple Smart Bulbs support

## License
MIT License
