import time
import threading
import cv2
import numpy as np
from camera import CameraStream
from hand_tracker import HandTracker
from gesture_classifier import GestureClassifier
from gesture_mapper import GestureMapper
from bulb_controller import BulbController
from logger import logger

class AirLightCore:
    def __init__(self):
        logger.info("Initializing AirLight Core...")
        
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
        self.frame_count = 0
        
        self.status = {
            "gesture": "None",
            "brightness": 100,
            "saturation": 100,
            "color": "White",
            "power": "OFF",
            "fps": "0",
            "bulb": "Disconnected"
        }
        
        self.current_frame = None
        self.lock = threading.Lock()
        
        self.last_heartbeat = time.time()
        self.camera_paused = False

    def ping_heartbeat(self):
        self.last_heartbeat = time.time()

    def start(self):
        """Starts the background camera and processing loop."""
        if not self.camera.start():
            logger.error("Could not start camera. Exiting.")
            self.camera_failed = True
            return
            
        self.is_running = True
        logger.info("Starting background processing loop.")
        
        # Run process loop in a background thread
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
    def _run_loop(self):
        while self.is_running:
            # Check heartbeat
            if time.time() - self.last_heartbeat > 3.0:
                if not self.camera_paused:
                    logger.info("Client disconnected. Suspending camera...")
                    self.camera.stop()
                    self.camera_paused = True
            else:
                if self.camera_paused:
                    logger.info("Client reconnected. Resuming camera...")
                    if self.camera.start():
                        self.camera_paused = False
                    else:
                        logger.error("Failed to resume camera.")

            if not self.camera_paused:
                self._process_frame()
                
            time.sleep(0.01) # Small sleep to prevent 100% CPU

    def stop(self):
        self.is_running = False
        self.camera.stop()
        self.bulb.turn_off()

    def _process_frame(self):
        """Process a single frame."""
        ret, frame = self.camera.get_frame()
        if not ret:
            return
        
        self.frame_count += 1
        self.fps_frame_count += 1
        now = time.time()
        if now - self.fps_start_time > 1.0:
            self.current_fps = self.fps_frame_count
            self.fps_frame_count = 0
            self.fps_start_time = now
            self.status["fps"] = str(self.current_fps)
            
        proc_frame, hands_landmarks = self.tracker.process_frame(frame)
        
        gesture_text = "None"
        brightness_val = None
        
        if hands_landmarks:
            lm_list = hands_landmarks[0]
            gesture_text, brightness_val = self.classifier.process_hand(lm_list)
            
            if gesture_text != "None":
                self.status["gesture"] = gesture_text
                if brightness_val is not None and gesture_text == "Pinch":
                    self.status["saturation"] = int(brightness_val)
            
            threading.Thread(
                target=self.mapper.handle_gesture, 
                args=(gesture_text, brightness_val),
                daemon=True
            ).start()
            
        # Sync values from mapper
        if self.mapper.last_brightness is not None:
            self.status["brightness"] = self.mapper.last_brightness
        if self.mapper.last_saturation is not None:
            self.status["saturation"] = self.mapper.last_saturation
        
        bulb_status = f"{self.bulb.connected_count}/{self.bulb.total_count} Online"
        if self.bulb.mock_mode:
            bulb_status = f"MOCK [{self.bulb.total_count}]"
        self.status["bulb"] = bulb_status
        
        self.status["power"] = "ON" if self.mapper.last_power_state else "OFF"
        
        if not self.bulb.mock_mode and hasattr(self.bulb, 'bulb') and self.bulb.bulb:
            self.status["ip"] = self.bulb.bulb.address
        else:
            self.status["ip"] = "N/A (Mock Mode)"
        
        color_status = self.mapper.last_color if self.mapper.last_color else "White"
        self.status["color"] = color_status.upper()
        
        with self.lock:
            # Store the processed frame (with landmarks) for web streaming
            self.current_frame = proc_frame.copy()

    def get_jpeg_frame(self):
        """Yields a JPEG encoded frame for video streaming."""
        with self.lock:
            if self.current_frame is None:
                return None
            ret, buffer = cv2.imencode('.jpg', self.current_frame)
            if not ret:
                return None
            return buffer.tobytes()

    def get_status(self):
        """Returns the current status dictionary."""
        return self.status
