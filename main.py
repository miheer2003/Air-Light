import time
import sys
import threading
from ui import AirLightUI
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
        
        self.ui = AirLightUI(on_exit=self.on_exit, on_reconnect=self.on_reconnect)
        self.is_running = False
        
        self.fps_start_time = time.time()
        self.fps_frame_count = 0
        self.current_fps = 0

    def start(self):
        """Starts the application."""
        if not self.camera.start():
            logger.error("Could not start camera. Exiting.")
            sys.exit(1)
            
        self.is_running = True
        logger.info("Starting main loop.")
        
        # Start the processing loop
        self.process_loop()
        
        # Start the UI mainloop (blocks until exit)
        self.ui.mainloop()

    def process_loop(self):
        """Main processing loop scheduled by Tkinter."""
        if not self.is_running:
            return
            
        ret, frame = self.camera.get_frame()
        if ret:
            self.fps_frame_count += 1
            now = time.time()
            if now - self.fps_start_time > 1.0:
                self.current_fps = self.fps_frame_count
                self.fps_frame_count = 0
                self.fps_start_time = now
                self.ui.update_status("fps", str(self.current_fps))
                
            # Process Frame for Hands
            proc_frame, hands_landmarks = self.tracker.process_frame(frame)
            
            gesture_text = "None"
            brightness_val = None
            
            if hands_landmarks:
                # We only process the first detected hand to avoid confusion
                lm_list = hands_landmarks[0]
                gesture_text, brightness_val = self.classifier.process_hand(lm_list)
                
                # Update UI Status
                if gesture_text != "None":
                    self.ui.update_status("gesture", gesture_text)
                    if brightness_val is not None:
                        self.ui.update_status("brightness", f"{int(brightness_val)}%")
                
                # Execute Mapper in a separate thread to prevent blocking the UI
                threading.Thread(
                    target=self.mapper.handle_gesture, 
                    args=(gesture_text, brightness_val),
                    daemon=True
                ).start()
                
            # Update Video Feed
            self.ui.update_frame(proc_frame)
            
        # Update connection status
        bulb_status = "Connected" if self.bulb.is_connected else "Disconnected"
        if self.bulb.mock_mode:
            bulb_status = "MOCK MODE"
        self.ui.update_status("bulb", bulb_status)
        
        power_status = "ON" if self.mapper.last_power_state else "OFF"
        self.ui.update_status("power", power_status)
        
        color_status = self.mapper.last_color if self.mapper.last_color else "White"
        self.ui.update_status("color", color_status.capitalize())

        # Schedule next loop
        self.ui.after(10, self.process_loop)

    def on_reconnect(self):
        """Triggered by UI Reconnect button."""
        logger.info("Manual reconnect requested.")
        threading.Thread(target=self.bulb.connect, daemon=True).start()

    def on_exit(self):
        """Gracefully shuts down."""
        logger.info("Shutting down AirLight...")
        self.is_running = False
        self.camera.stop()
        self.tracker.close()
        self.ui.quit()
        self.ui.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = AirLightApp()
    app.start()
