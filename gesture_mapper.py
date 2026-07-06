import time
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
        self.cooldown = 0.8  # seconds — increased for better accuracy
        
        # State tracking to avoid redundant commands
        self.last_power_state = None
        self.last_color = None
        self.last_brightness = None
        
        self.colors = ["white", "red", "green", "blue", "yellow", "purple", "cyan", "orange", "warm_white"]
        self.current_color_idx = 0

    def handle_gesture(self, gesture: str, value: Optional[float] = None):
        """Processes a gesture and triggers the bulb if necessary."""
        current_time = time.time()
        
        # Brightness (Pinch) - handled smoothly
        if gesture == "Pinch" and value is not None:
            # Only update if brightness changed significantly (>= 8%)
            brightness_val = int(value)
            if self.last_brightness is None or abs(self.last_brightness - brightness_val) >= 8:
                # Cooldown for brightness to avoid flooding the network
                if current_time - self.last_action_time > 0.25:
                    logger.info(f"Setting brightness to {brightness_val}%")
                    self.bulb.set_brightness(brightness_val)
                    self.last_brightness = brightness_val
                    self.last_action_time = current_time
            return

        # Discrete gestures - require full cooldown
        if current_time - self.last_action_time < self.cooldown:
            return
            
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
        elif gesture == "2 Fingers":
            action_taken = self._set_color("red")
        elif gesture == "3 Fingers":
            action_taken = self._set_color("green")
        elif gesture == "4 Fingers":
            action_taken = self._set_color("blue")
            
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

        if action_taken:
            self.last_action_time = current_time

    def _set_color(self, color: str) -> bool:
        if self.last_color != color:
            logger.info(f"Setting color to {color}")
            self.bulb.set_color(color)
            self.last_color = color
            return True
        return False
