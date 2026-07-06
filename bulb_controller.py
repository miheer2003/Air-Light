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
        self.mock_mode = config.mock_mode
        self.devices = []
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

    @property
    def is_connected(self):
        return len(self.devices) > 0 or self.mock_mode
        
    @property
    def connected_count(self):
        if self.mock_mode:
            return len(config.devices)
        return len(self.devices)
        
    @property
    def total_count(self):
        return len(config.devices)

    def connect(self):
        """Attempts to connect to the bulbs."""
        if self.mock_mode:
            logger.info("BulbController running in MOCK MODE (No real Tuya connection).")
            return

        self.devices = []
        for dev_config in config.devices:
            ip = dev_config.get("ip", "")
            dev_id = dev_config.get("id", "")
            local_key = dev_config.get("key", "")
            
            try:
                logger.info(f"Connecting to bulb at {ip}...")
                device = tinytuya.BulbDevice(
                    dev_id=dev_id,
                    address=ip,
                    local_key=local_key,
                    version=3.3
                )
                device.set_socketPersistent(True) # Keep connection alive
                
                # Test connection
                status = device.status()
                if 'Error' in status or status == {}:
                    raise Exception("Tuya status returned error or empty")
                    
                self.devices.append(device)
                logger.info(f"Successfully connected to bulb at {ip}.")
            except Exception as e:
                logger.error(f"Failed to connect to bulb at {ip}: {e}")
                
        if len(self.devices) == 0 and config.mock_mode:
            logger.info("No real bulbs connected, falling back to MOCK MODE.")

    def turn_on(self):
        if not self.is_connected: return
        with self.lock:
            if self.mock_mode:
                logger.debug(f"[MOCK] {self.total_count} Bulbs ON")
                return
            for device in self.devices:
                try:
                    device.turn_on()
                except Exception as e:
                    logger.error(f"Error turning on bulb: {e}")

    def turn_off(self):
        if not self.is_connected: return
        with self.lock:
            if self.mock_mode:
                logger.debug(f"[MOCK] {self.total_count} Bulbs OFF")
                return
            for device in self.devices:
                try:
                    device.turn_off()
                except Exception as e:
                    logger.error(f"Error turning off bulb: {e}")

    def set_brightness(self, percentage: int):
        """Sets brightness (0-100)."""
        if not self.is_connected: return
        # Ensure within bounds
        percentage = max(1, min(100, percentage))
        
        with self.lock:
            if self.mock_mode:
                logger.debug(f"[MOCK] {self.total_count} Bulbs Brightness -> {percentage}%")
                return
            for device in self.devices:
                try:
                    device.set_brightness_percentage(percentage)
                except Exception as e:
                    logger.error(f"Error setting brightness for bulb: {e}")

    def set_color(self, color_name: str):
        """Sets the bulb to a specific color."""
        if not self.is_connected: return
        
        if color_name not in self.color_map:
            logger.warning(f"Unknown color: {color_name}")
            return
            
        with self.lock:
            if self.mock_mode:
                logger.debug(f"[MOCK] {self.total_count} Bulbs Color -> {color_name}")
                return
            for device in self.devices:
                try:
                    if color_name == "white":
                        device.set_mode('white')
                    else:
                        h, s, v = self.color_map[color_name]
                        device.set_colour(h, s, v)
                except Exception as e:
                    logger.error(f"Error setting color for bulb: {e}")
