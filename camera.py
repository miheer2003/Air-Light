import cv2
import threading
import time
from typing import Tuple, Any
from logger import logger
from config import config

class CameraStream:
    """
    Runs the OpenCV VideoCapture in a separate background thread.
    This prevents I/O blocking from slowing down the main UI or MediaPipe processing.
    """
    def __init__(self):
        self.camera_index = config.camera_index
        self.cap = None
        self.frame = None
        self.is_running = False
        self.lock = threading.Lock()
        
    def start(self) -> bool:
        """Starts the camera stream."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            logger.error(f"Failed to open camera with index {self.camera_index}")
            return False
            
        self.is_running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        logger.info("Camera stream started.")
        
        # Wait a moment for the first frame
        time.sleep(1.0)
        return True
        
    def _update(self):
        """Continuously reads frames from the camera."""
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Failed to grab frame.")
                time.sleep(0.1)
                continue
                
            # Flip horizontally for selfie view
            frame = cv2.flip(frame, 1)
            
            with self.lock:
                self.frame = frame
                
            time.sleep(0.01) # Small sleep to prevent maxing out CPU
            
    def get_frame(self) -> Tuple[bool, Any]:
        """Returns the most recent frame."""
        with self.lock:
            if self.frame is not None:
                return True, self.frame.copy()
            return False, None
            
    def stop(self):
        """Stops the camera stream."""
        self.is_running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
        logger.info("Camera stream stopped.")
