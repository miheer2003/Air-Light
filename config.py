import json
import os
from dataclasses import dataclass, asdict
from logger import logger

@dataclass
class AppConfig:
    device_ip: str = "192.168.1.100"
    device_id: str = "your_device_id"
    local_key: str = "your_local_key"
    camera_index: int = 0
    default_brightness: int = 100
    mock_mode: bool = True  # If True, won't crash if Tuya fails to connect
    
    # Settings for gesture smoothing
    cooldown_ms: int = 300
    pinch_min_dist: int = 20
    pinch_max_dist: int = 200
    
class ConfigManager:
    """Manages loading and saving configuration."""
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = AppConfig()
        self.load()

    def load(self):
        """Loads configuration from JSON file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    # Update config fields that exist in AppConfig
                    for key, value in data.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
                logger.info("Configuration loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        else:
            logger.info("Config file not found, creating default config.")
            self.save()

    def save(self):
        """Saves current configuration to JSON file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(asdict(self.config), f, indent=4)
            logger.info("Configuration saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

# Global config manager instance
config_manager = ConfigManager()
config = config_manager.config
