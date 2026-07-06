import time
import threading
from typing import Optional
from logger import logger
from bulb_controller import BulbController

class GestureMapper:
    """
    Maps semantic gestures to concrete bulb actions.
    Ensures commands are not spammed (cooldowns & state caching).
    """
    def __init__(self, bulb_controller: BulbController):
        self.bulb = bulb_controller
        self.last_action_time = 0
        self.cooldown = 0.8  # seconds
        self.lock = threading.Lock()
        
        # State tracking to avoid redundant commands
        self.last_power_state = None
        self.last_color = None
        self.last_brightness = None
        self.last_saturation = None
        
        self.colors = ["white", "red", "green", "blue", "yellow", "purple", "cyan", "orange", "warm_white"]
        self.current_color_idx = 0

    def handle_gesture(self, gesture: str, value: Optional[float] = None):
        """Processes a gesture and triggers the bulb if necessary."""
        current_time = time.time()
        
        # Density / Saturation (Pinch) - handled smoothly
        if gesture == "Pinch" and value is not None:
            sat_val = int(value)
            if self.last_saturation is None or abs(self.last_saturation - sat_val) >= 8:
                if current_time - self.last_action_time > 0.25:
                    logger.info(f"Setting saturation (density) to {sat_val}%")
                    self.bulb.set_saturation(sat_val)
                    self.last_saturation = sat_val
                    self.last_action_time = current_time
            return

        # Discrete gestures - require full cooldown
        with self.lock:
            if current_time - self.last_action_time < self.cooldown:
                return
            self.last_action_time = current_time
            
        action_taken = False

        if gesture == "Open Palm":
            if self.last_power_state != True:
                logger.info("Gesture: Open Palm -> Turn ON")
                self.bulb.turn_on()
                self.last_power_state = True
                action_taken = True
                
        elif gesture == "Closed Fist":
            if self.last_power_state != False:
                logger.info("Gesture: Closed Fist -> Turn OFF")
                self.bulb.turn_off()
                self.last_power_state = False
                action_taken = True
                
        elif gesture == "1 Finger":
            action_taken = self._set_color("white")
        elif gesture == "2 Fingers" or gesture == "Peace Sign":
            action_taken = self._set_color("red")
        elif gesture == "3 Fingers":
            action_taken = self._set_color("green")
        elif gesture == "4 Fingers":
            action_taken = self._set_color("blue")
        elif gesture == "OK Sign":
            self.bulb.set_scene(4)
            logger.info("Gesture: OK Sign -> Scene 4")
            action_taken = True
            
        elif gesture == "Thumbs Up":
            action_taken = self._set_color("warm_white")
            if action_taken:
                logger.info("Gesture: Thumbs Up -> Warm White")
                
        elif gesture == "Thumbs Down":
            action_taken = self._set_color("purple")
            if action_taken:
                logger.info("Gesture: Thumbs Down -> Purple")
                
        elif gesture == "Rock":
            action_taken = self._set_color("cyan")
            if action_taken:
                logger.info("Gesture: Rock -> Cyan")
            
        elif gesture == "Swipe Right":
            self.current_color_idx = (self.current_color_idx + 1) % len(self.colors)
            action_taken = self._set_color(self.colors[self.current_color_idx])
            logger.info(f"Gesture: Swipe Right -> Next Color ({self.colors[self.current_color_idx]})")
            
        elif gesture == "Swipe Left":
            self.current_color_idx = (self.current_color_idx - 1) % len(self.colors)
            action_taken = self._set_color(self.colors[self.current_color_idx])
            logger.info(f"Gesture: Swipe Left -> Prev Color ({self.colors[self.current_color_idx]})")
            
        elif gesture == "Swipe Up":
            self.last_brightness = min(100, (self.last_brightness or 50) + 15)
            self.bulb.set_brightness(self.last_brightness)
            action_taken = True
            logger.info(f"Gesture: Swipe Up -> Brightness {self.last_brightness}%")
            
        elif gesture == "Swipe Down":
            self.last_brightness = max(1, (self.last_brightness or 50) - 15)
            self.bulb.set_brightness(self.last_brightness)
            action_taken = True
            logger.info(f"Gesture: Swipe Down -> Brightness {self.last_brightness}%")

        if action_taken:
            pass # already updated last_action_time inside lock

    def _set_color(self, color: str) -> bool:
        if self.last_color != color:
            logger.info(f"Setting color to {color}")
            self.bulb.set_color(color)
            self.last_color = color
            return True
        return False
