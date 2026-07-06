import tinytuya
import threading
import time
from typing import Optional
from logger import logger
from config import config

class BulbController:
    """
    Manages communication with the Tuya/Halonix smart bulb.
    Handles reconnects and gracefully falls back to mock mode if connection fails.
    """
    def __init__(self):
        self.ip = config.device_ip
        self.device_id = config.device_id
        self.local_key = config.local_key
        self.mock_mode = config.mock_mode
        
        self.device: Optional[tinytuya.BulbDevice] = None
        self.is_connected = False
        self.lock = threading.Lock()
        
        # Color mapping (Hue, Saturation, Value) for Tuya
        # Note: Tuya H: 0-360, S: 0-1000, V: 0-1000
        self.color_map = {
            "white": (0, 0, 1000),     # Actually handled via set_mode('white') usually, but this is a fallback
            "red": (0, 1000, 1000),
            "green": (120, 1000, 1000),
            "blue": (240, 1000, 1000),
            "yellow": (60, 1000, 1000)
        }
        
        self.connect()

    def connect(self):
        """Attempts to connect to the bulb."""
        if self.mock_mode:
            logger.info("BulbController running in MOCK MODE (No real Tuya connection).")
            self.is_connected = True
            return

        try:
            logger.info(f"Connecting to bulb at {self.ip}...")
            self.device = tinytuya.BulbDevice(
                dev_id=self.device_id,
                address=self.ip,
                local_key=self.local_key,
                version=3.3
            )
            self.device.set_socketPersistent(True) # Keep connection alive
            
            # Test connection
            status = self.device.status()
            if 'Error' in status or status == {}:
                raise Exception("Tuya status returned error or empty")
                
            self.is_connected = True
            logger.info("Successfully connected to bulb.")
        except Exception as e:
            self.is_connected = False
            logger.error(f"Failed to connect to bulb: {e}")
            if config.mock_mode:
                logger.info("Falling back to MOCK MODE.")
                self.is_connected = True # Fake connection for mock mode

    def turn_on(self):
        if not self.is_connected: return
        with self.lock:
            if self.mock_mode:
                logger.debug("[MOCK] Bulb ON")
                return
            try:
                self.device.turn_on()
            except Exception as e:
                logger.error(f"Error turning on: {e}")

    def turn_off(self):
        if not self.is_connected: return
        with self.lock:
            if self.mock_mode:
                logger.debug("[MOCK] Bulb OFF")
                return
            try:
                self.device.turn_off()
            except Exception as e:
                logger.error(f"Error turning off: {e}")

    def set_brightness(self, percentage: int):
        """Sets brightness (0-100)."""
        if not self.is_connected: return
        # Ensure within bounds
        percentage = max(1, min(100, percentage))
        
        with self.lock:
            if self.mock_mode:
                logger.debug(f"[MOCK] Brightness -> {percentage}%")
                return
            try:
                # Tuya brightness usually 10-1000 or 25-255 depending on bulb
                # We'll assume standard 10-1000 for standard tuya v3.3
                val = int((percentage / 100.0) * 1000)
                # Tuya library has set_brightness (0-100) or set_brightness_percentage
                # Using set_brightness_percentage for standard behavior
                self.device.set_brightness_percentage(percentage)
            except Exception as e:
                logger.error(f"Error setting brightness: {e}")

    def set_color(self, color_name: str):
        """Sets the bulb to a specific color."""
        if not self.is_connected: return
        
        if color_name not in self.color_map:
            logger.warning(f"Unknown color: {color_name}")
            return
            
        with self.lock:
            if self.mock_mode:
                logger.debug(f"[MOCK] Color -> {color_name}")
                return
            try:
                if color_name == "white":
                    self.device.set_mode('white')
                else:
                    h, s, v = self.color_map[color_name]
                    self.device.set_colour(h, s, v)
            except Exception as e:
                logger.error(f"Error setting color: {e}")
