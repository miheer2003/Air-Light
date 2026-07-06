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
        self.frame_count = 0  # For scan line animation
        
        self.status = {
            "gesture": "None",
            "brightness": 100,
            "saturation": 100,
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
        
        cv2.namedWindow("AirLight", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("AirLight", 1100, 650)
        
        while self.is_running:
            if self.camera_failed:
                error_frame = np.zeros((650, 1100, 3), dtype=np.uint8)
                cv2.putText(error_frame, "CAMERA NOT FOUND", (320, 325), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 65), 2)
                cv2.imshow("AirLight", error_frame)
            else:
                self._process_frame()
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):
                break
                
        self.on_exit()

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
                if brightness_val is not None:
                    if gesture_text == "Dial":
                        self.status["saturation"] = int(brightness_val)
                    else:
                        self.status["brightness"] = int(brightness_val)
            
            threading.Thread(
                target=self.mapper.handle_gesture, 
                args=(gesture_text, brightness_val),
                daemon=True
            ).start()
        
        bulb_status = f"{self.bulb.connected_count}/{self.bulb.total_count} Online"
        if self.bulb.mock_mode:
            bulb_status = f"MOCK [{self.bulb.total_count}]"
        self.status["bulb"] = bulb_status
        
        self.status["power"] = "ON" if self.mapper.last_power_state else "OFF"
        
        color_status = self.mapper.last_color if self.mapper.last_color else "White"
        self.status["color"] = color_status.upper()
        
        display_frame = self._draw_hud(proc_frame)
        cv2.imshow("AirLight", display_frame)

    def _draw_rounded_rect(self, img, pt1, pt2, color, thickness, radius=12):
        """Draw a rounded rectangle."""
        x1, y1 = pt1
        x2, y2 = pt2
        
        # Draw filled rounded rectangle using overlapping shapes
        cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
        cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, thickness)
        
        cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness)
        cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness)

    def _draw_hud(self, frame):
        """Draw a futuristic HUD overlay."""
        h, w = frame.shape[:2]
        
        # Colors - Neon green + dark theme
        NEON_GREEN = (65, 255, 0)    # BGR
        NEON_CYAN = (255, 230, 0)     # BGR
        DIM_GREEN = (30, 120, 0)
        DARK_BG = (18, 18, 20)
        PANEL_BG = (25, 25, 30)
        GRID_COLOR = (35, 40, 30)
        TEXT_DIM = (80, 90, 70)
        TEXT_BRIGHT = (200, 220, 180)
        
        panel_width = 330
        canvas = np.zeros((h, w + panel_width, 3), dtype=np.uint8)
        canvas[:, :w] = frame
        
        # === RIGHT PANEL ===
        panel = canvas[:, w:]
        panel[:] = DARK_BG
        
        # Subtle grid pattern on panel
        for y_line in range(0, h, 20):
            cv2.line(canvas, (w, y_line), (w + panel_width, y_line), GRID_COLOR, 1)
        for x_line in range(w, w + panel_width, 20):
            cv2.line(canvas, (x_line, 0), (x_line, h), GRID_COLOR, 1)
        
        # Glowing separator line
        cv2.line(canvas, (w, 0), (w, h), NEON_GREEN, 2)
        cv2.line(canvas, (w + 1, 0), (w + 1, h), DIM_GREEN, 1)
        
        # === TITLE BLOCK ===
        cv2.putText(canvas, "AIRLIGHT", (w + 20, 45), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.1, NEON_GREEN, 2)
        cv2.putText(canvas, "GESTURE CONTROL SYSTEM", (w + 20, 68), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT_DIM, 1)
        
        # Title underline with glow
        cv2.line(canvas, (w + 15, 80), (w + panel_width - 15, 80), DIM_GREEN, 1)
        cv2.line(canvas, (w + 15, 81), (w + 100, 81), NEON_GREEN, 2)
        
        # === STATUS BLOCKS ===
        y = 105
        
        # POWER indicator
        power_on = self.status["power"] == "ON"
        power_color = NEON_GREEN if power_on else (0, 0, 180)
        # Power dot
        cv2.circle(canvas, (w + 30, y + 12), 8, power_color, -1)
        cv2.circle(canvas, (w + 30, y + 12), 10, power_color, 1)
        cv2.putText(canvas, "POWER", (w + 50, y + 8), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT_DIM, 1)
        cv2.putText(canvas, self.status["power"], (w + 50, y + 28), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, power_color, 2)
        y += 55
        
        # GESTURE
        cv2.putText(canvas, "ACTIVE GESTURE", (w + 20, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT_DIM, 1)
        gesture = self.status["gesture"]
        g_color = NEON_GREEN if gesture != "None" else TEXT_DIM
        cv2.putText(canvas, gesture.upper(), (w + 20, y + 28), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.75, g_color, 2)
        # Blinking indicator when active
        if gesture != "None" and self.frame_count % 10 < 7:
            cv2.circle(canvas, (w + panel_width - 30, y + 18), 5, NEON_GREEN, -1)
        y += 60
        
        # BRIGHTNESS BAR
        cv2.putText(canvas, "BRIGHTNESS", (w + 20, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT_DIM, 1)
        brightness = self.status["brightness"] if isinstance(self.status["brightness"], int) else 100
        # Bar background
        bar_x = w + 20
        bar_w = panel_width - 40
        bar_h = 14
        cv2.rectangle(canvas, (bar_x, y + 8), (bar_x + bar_w, y + 8 + bar_h), (40, 40, 45), -1)
        # Bar fill
        fill_w = int(bar_w * brightness / 100)
        if fill_w > 0:
            # Gradient-like fill
            for i in range(fill_w):
                intensity = int(255 * (i / bar_w))
                col = (0, intensity, 0)
                cv2.line(canvas, (bar_x + i, y + 9), (bar_x + i, y + 8 + bar_h - 1), col, 1)
        # Bar border
        cv2.rectangle(canvas, (bar_x, y + 8), (bar_x + bar_w, y + 8 + bar_h), DIM_GREEN, 1)
        # Percentage text
        cv2.putText(canvas, f"{brightness}%", (bar_x + bar_w - 45, y + 21), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, NEON_GREEN, 1)
        y += 40
        
        # DENSITY (SATURATION) BAR
        cv2.putText(canvas, "DENSITY", (w + 20, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT_DIM, 1)
        saturation = self.status.get("saturation", 100)
        # Bar background
        cv2.rectangle(canvas, (bar_x, y + 8), (bar_x + bar_w, y + 8 + bar_h), (40, 40, 45), -1)
        # Bar fill
        fill_w = int(bar_w * saturation / 100)
        if fill_w > 0:
            for i in range(fill_w):
                intensity = int(255 * (i / bar_w))
                col = (0, intensity, intensity) # Cyan tint for density
                cv2.line(canvas, (bar_x + i, y + 9), (bar_x + i, y + 8 + bar_h - 1), col, 1)
        # Bar border
        cv2.rectangle(canvas, (bar_x, y + 8), (bar_x + bar_w, y + 8 + bar_h), (0, 100, 100), 1)
        # Percentage text
        cv2.putText(canvas, f"{saturation}%", (bar_x + bar_w - 45, y + 21), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, NEON_CYAN, 1)
        y += 40
        
        # COLOR
        cv2.putText(canvas, "COLOR", (w + 20, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT_DIM, 1)
        color_name = self.status["color"]
        color_preview = self._get_color_bgr(color_name)
        # Color swatch
        cv2.rectangle(canvas, (w + 20, y + 8), (w + 50, y + 30), color_preview, -1)
        cv2.rectangle(canvas, (w + 20, y + 8), (w + 50, y + 30), DIM_GREEN, 1)
        cv2.putText(canvas, color_name, (w + 60, y + 26), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_BRIGHT, 2)
        y += 50
        
        # NETWORK STATUS
        cv2.line(canvas, (w + 15, y - 5), (w + panel_width - 15, y - 5), DIM_GREEN, 1)
        cv2.putText(canvas, "NETWORK", (w + 20, y + 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT_DIM, 1)
        bulb_status = self.status["bulb"]
        is_online = "Online" in bulb_status or "MOCK" in bulb_status
        net_color = NEON_GREEN if is_online else (0, 0, 200)
        cv2.putText(canvas, bulb_status, (w + 20, y + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.55, net_color, 1)
        y += 55
        
        # FPS
        cv2.putText(canvas, "FPS", (w + 20, y + 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT_DIM, 1)
        cv2.putText(canvas, self.status["fps"], (w + 60, y + 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, NEON_CYAN, 1)
        
        # === BOTTOM GESTURE GUIDE ===
        y_guide = h - 130
        cv2.line(canvas, (w + 15, y_guide), (w + panel_width - 15, y_guide), DIM_GREEN, 1)
        cv2.putText(canvas, "COMMANDS", (w + 20, y_guide + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, NEON_GREEN, 1)
        
        guides = [
            ("PALM", "ON", NEON_GREEN),
            ("FIST", "OFF", (0, 0, 200)),
            ("PINCH", "BRIGHTNESS", NEON_CYAN),
            ("1 FINGER + ROTATE", "DENSITY", (0, 255, 255)),
            ("SWIPE", "CYCLE", TEXT_BRIGHT),
        ]
        gx = w + 20
        gy = y_guide + 32
        for label, action, color in guides:
            cv2.putText(canvas, label, (gx, gy), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.33, color, 1)
            cv2.putText(canvas, action, (gx + 120, gy), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.33, TEXT_DIM, 1)
            gy += 18
        
        # === CAMERA OVERLAY - Corner markers ===
        marker_len = 25
        marker_color = NEON_GREEN
        # Top-left
        cv2.line(canvas, (5, 5), (5 + marker_len, 5), marker_color, 2)
        cv2.line(canvas, (5, 5), (5, 5 + marker_len), marker_color, 2)
        # Top-right
        cv2.line(canvas, (w - 5, 5), (w - 5 - marker_len, 5), marker_color, 2)
        cv2.line(canvas, (w - 5, 5), (w - 5, 5 + marker_len), marker_color, 2)
        # Bottom-left
        cv2.line(canvas, (5, h - 5), (5 + marker_len, h - 5), marker_color, 2)
        cv2.line(canvas, (5, h - 5), (5, h - 5 - marker_len), marker_color, 2)
        # Bottom-right
        cv2.line(canvas, (w - 5, h - 5), (w - 5 - marker_len, h - 5), marker_color, 2)
        cv2.line(canvas, (w - 5, h - 5), (w - 5, h - 5 - marker_len), marker_color, 2)
        
        # Scan line effect on camera feed
        scan_y = (self.frame_count * 3) % h
        cv2.line(canvas, (0, scan_y), (w, scan_y), (0, 60, 0), 1)
        
        # Camera label
        cv2.putText(canvas, "LIVE FEED", (15, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, NEON_GREEN, 1)
        cv2.circle(canvas, (90, 20), 4, (0, 0, 255), -1)  # Red recording dot
        
        # ESC to quit hint
        cv2.putText(canvas, "[Q] QUIT", (w + panel_width - 90, h - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, TEXT_DIM, 1)
        
        return canvas
    
    def _get_color_bgr(self, color_name):
        """Return BGR color for preview swatch."""
        colors = {
            "WHITE": (255, 255, 255),
            "RED": (0, 0, 255),
            "GREEN": (0, 255, 0),
            "BLUE": (255, 0, 0),
            "YELLOW": (0, 255, 255),
            "PURPLE": (255, 0, 128),
            "CYAN": (255, 255, 0),
            "ORANGE": (0, 128, 255),
            "WARM_WHITE": (100, 200, 255),
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
