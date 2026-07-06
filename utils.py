import math
import numpy as np
from typing import Tuple

def calculate_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    """
    Calculates Euclidean distance between two 2D points (x, y).
    """
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def calculate_angle(p1: Tuple[int, int], p2: Tuple[int, int], p3: Tuple[int, int]) -> float:
    """
    Calculates the angle formed by three points (p1, p2, p3) where p2 is the vertex.
    Returns angle in degrees.
    """
    # Vectors
    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])
    
    # Dot product and magnitudes
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.hypot(v1[0], v1[1])
    mag2 = math.hypot(v2[0], v2[1])
    
    if mag1 * mag2 == 0:
        return 0.0
        
    cos_angle = dot / (mag1 * mag2)
    # Ensure cos_angle is within valid range [-1, 1] due to floating point precision
    cos_angle = max(-1.0, min(1.0, cos_angle))
    
    angle_rad = math.acos(cos_angle)
    return math.degrees(angle_rad)

class ExponentialMovingAverage:
    """
    Applies exponential smoothing to a stream of values to reduce jitter.
    """
    def __init__(self, alpha: float = 0.2):
        """
        alpha: Smoothing factor (0 < alpha <= 1). 
               Higher alpha discounts older observations faster.
        """
        self.alpha = alpha
        self.value = None
        
    def update(self, new_value: float) -> float:
        if self.value is None:
            self.value = new_value
        else:
            self.value = self.alpha * new_value + (1 - self.alpha) * self.value
        return self.value

    def get(self) -> float:
        return self.value if self.value is not None else 0.0
