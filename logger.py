import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "AirLight", log_file: str = "airlight.log") -> logging.Logger:
    """
    Sets up a logger that logs to both console and a rotating file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent adding handlers multiple times if called again
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console Handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File Handler (10 MB max size, keep 3 backups)
        fh = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=3)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    return logger

# Global logger instance
logger = setup_logger()
