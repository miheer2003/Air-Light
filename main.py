import time
import sys
import threading
import cv2
import numpy as np
from camera import CameraStream
from hand_tracker import HandTracker
from gesture_classifier import GestureClassifier
from gesture_mapper import GestureMapper
from bulb_controller import BulbController
from logger import logger

class AirLightApp:
    def __init__(self):
        logger.info("Initializing AirLight App...")
        
        self.camera = CameraStream()
        self.tracker = HandTracker()
        self.classifier = GestureClassifier()
        self.bulb = BulbController()
        self.mapper = GestureMapper(self.bulb)
        
        self.is_running = False
        self.camera_failed = False
        
        self.fps_start_time = time.time()
        self.fps_frame_count = 0
        self.current_fps = 0
        
        # Status info for HUD overlay
        self.status = {
            "gesture": "None",
            "brightness": "100%",
            "color": "White",
            "power": "OFF",
            "fps": "0",
            "bulb": "Disconnected"
        }

    def start(self):
        """Starts the application."""
        if not self.camera.start():
            logger.error("Could not start camera. Exiting.")
            self.camera_failed = True
            
        self.is_running = True
        logger.info("Starting main loop.")
        
        # Create OpenCV window
        cv2.namedWindow("AirLight - AI Smart Lighting", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("AirLight - AI Smart Lighting", 1100, 700)
        
        while self.is_running:
            if self.camera_failed:
                # Show error frame
                error_frame = np.zeros((700, 1100, 3), dtype=np.uint8)
                cv2.putText(error_frame, "Camera Not Found", (300, 350), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                cv2.imshow("AirLight - AI Smart Lighting", error_frame)
            else:
                self._process_frame()
            
            # Check for quit key (ESC or 'q')
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):
                break
                
        self.on_exit()

    def _process_frame(self):
        """Process a single frame."""
        ret, frame = self.camera.get_frame()
        if not ret:
            return
            
        self.fps_frame_count += 1
        now = time.time()
        if now - self.fps_start_time > 1.0:
            self.current_fps = self.fps_frame_count
            self.fps_frame_count = 0
            self.fps_start_time = now
            self.status["fps"] = str(self.current_fps)
            
        # Process Frame for Hands
        proc_frame, hands_landmarks = self.tracker.process_frame(frame)
        
        gesture_text = "None"
        brightness_val = None
        
        if hands_landmarks:
            lm_list = hands_landmarks[0]
            gesture_text, brightness_val = self.classifier.process_hand(lm_list)
            
            if gesture_text != "None":
                self.status["gesture"] = gesture_text
                if brightness_val is not None:
                    self.status["brightness"] = f"{int(brightness_val)}%"
            
            # Execute Mapper in a separate thread
            threading.Thread(
                target=self.mapper.handle_gesture, 
                args=(gesture_text, brightness_val),
                daemon=True
            ).start()
        
        # Update connection status
        bulb_status = f"{self.bulb.connected_count}/{self.bulb.total_count} Connected"
        if self.bulb.mock_mode:
            bulb_status = f"MOCK MODE ({self.bulb.total_count} configured)"
        self.status["bulb"] = bulb_status
        
        power_status = "ON" if self.mapper.last_power_state else "OFF"
        self.status["power"] = power_status
        
        color_status = self.mapper.last_color if self.mapper.last_color else "White"
        self.status["color"] = color_status.capitalize()
        
        # Draw HUD overlay
        display_frame = self._draw_hud(proc_frame)
        
        cv2.imshow("AirLight - AI Smart Lighting", display_frame)

    def _draw_hud(self, frame):
        """Draw a heads-up display overlay on the camera frame."""
        h, w = frame.shape[:2]
        
        # Create a wider canvas with a dark panel on the right
        panel_width = 320
        canvas = np.zeros((h, w + panel_width, 3), dtype=np.uint8)
        canvas[:h, :w] = frame
        
        # Dark panel background with subtle gradient
        panel = canvas[:, w:]
        panel[:] = (30, 30, 35)
        
        # Draw a subtle separator line
        cv2.line(canvas, (w, 0), (w, h), (60, 60, 70), 2)
        
        # Title
        cv2.putText(canvas, "AirLight", (w + 20, 45), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 200, 255), 2)
        cv2.putText(canvas, "AI Smart Lighting", (w + 20, 75), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 160), 1)
        
        # Separator
        cv2.line(canvas, (w + 15, 90), (w + panel_width - 15, 90), (60, 60, 70), 1)
        
        # Status items
        y_start = 130
        y_step = 55
        
        items = [
            ("Gesture", self.status["gesture"], self._get_gesture_color(self.status["gesture"])),
            ("Power", self.status["power"], (0, 255, 100) if self.status["power"] == "ON" else (0, 0, 200)),
            ("Brightness", self.status["brightness"], (255, 255, 200)),
            ("Color", self.status["color"], self._get_color_preview(self.status["color"])),
            ("Bulb", self.status["bulb"], (0, 255, 100) if "Connected" in self.status["bulb"] else (0, 150, 255)),
            ("FPS", self.status["fps"], (200, 200, 200)),
        ]
        
        for i, (label, value, color) in enumerate(items):
            y = y_start + i * y_step
            # Label
            cv2.putText(canvas, label, (w + 20, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, (130, 130, 140), 1)
            # Value
            cv2.putText(canvas, str(value), (w + 20, y + 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Draw gesture guide at the bottom
        y_guide = h - 120
        cv2.line(canvas, (w + 15, y_guide - 15), (w + panel_width - 15, y_guide - 15), (60, 60, 70), 1)
        cv2.putText(canvas, "Gestures", (w + 20, y_guide + 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.55, (150, 150, 160), 1)
        
        guides = [
            "Palm=ON  Fist=OFF",
            "Pinch=Brightness",
            "1-4 Fingers=Colors",
            "Swipe=Cycle  Q=Quit",
        ]
        for i, guide in enumerate(guides):
            cv2.putText(canvas, guide, (w + 20, y_guide + 30 + i * 22), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.42, (100, 100, 110), 1)
        
        return canvas
    
    def _get_gesture_color(self, gesture):
        """Return a color based on the gesture type."""
        colors = {
            "Open Palm": (0, 255, 100),
            "Closed Fist": (0, 0, 255),
            "Pinch": (0, 255, 255),
            "Thumbs Up": (0, 200, 255),
            "Thumbs Down": (255, 0, 200),
            "Rock": (255, 255, 0),
            "Swipe Right": (255, 200, 0),
            "Swipe Left": (255, 200, 0),
        }
        return colors.get(gesture, (200, 200, 200))
    
    def _get_color_preview(self, color_name):
        """Return BGR color for the UI preview."""
        colors = {
            "White": (255, 255, 255),
            "Red": (0, 0, 255),
            "Green": (0, 255, 0),
            "Blue": (255, 0, 0),
            "Yellow": (0, 255, 255),
            "Purple": (255, 0, 128),
            "Cyan": (255, 255, 0),
            "Orange": (0, 128, 255),
            "Warm_white": (100, 200, 255),
        }
        return colors.get(color_name, (200, 200, 200))

    def on_exit(self):
        """Gracefully shuts down."""
        logger.info("Shutting down AirLight...")
        self.is_running = False
        self.camera.stop()
        self.tracker.close()
        cv2.destroyAllWindows()
        sys.exit(0)

if __name__ == "__main__":
    app = AirLightApp()
    app.start()
