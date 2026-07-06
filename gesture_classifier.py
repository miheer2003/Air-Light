import time
from typing import List, Tuple, Optional
from gesture_detector import GestureDetector
from utils import ExponentialMovingAverage
from config import config

class GestureClassifier:
    """
    Classifies raw hand features into discrete, semantic gestures
    and manages state (smoothing, cooldowns).
    """
    def __init__(self):
        self.detector = GestureDetector()
        self.last_action_time = 0
        self.brightness_ema = ExponentialMovingAverage(alpha=0.3)
        self.last_gesture = "None"
        
        # For swipe detection
        self.prev_hand_center = None
        self.swipe_threshold = 100  # pixels to move to register a swipe
        self.swipe_cooldown = 1.0   # seconds

    def process_hand(self, lm_list: List[Tuple[int, int]]) -> Tuple[str, Optional[float]]:
        """
        Given a list of landmarks for a single hand, returns the classified gesture
        and an optional value (e.g., brightness percentage).
        """
        if not lm_list:
            return "None", None

        current_time = time.time()
        center = self.detector.get_hand_center(lm_list)
        
        # 1. Check for Swipe (Hand moving fast horizontally)
        gesture = self._check_swipe(center, current_time)
        if gesture != "None":
            return gesture, None
            
        self.prev_hand_center = center
        
        # 2. Extract basic finger states
        open_fingers = self.detector.get_open_fingers(lm_list)
        count = sum(open_fingers)
        
        # 3. Check for Pinch (Brightness)
        is_pinching, pinch_dist, _ = self.detector.detect_pinch(lm_list)
        if is_pinching:
            # Map distance to percentage (0-100%)
            min_d, max_d = config.pinch_min_dist, config.pinch_max_dist
            mapped_val = max(0, min(100, int(((pinch_dist - min_d) / (max_d - min_d)) * 100)))
            smoothed_val = self.brightness_ema.update(mapped_val)
            return "Pinch", smoothed_val
            
        # 4. Classify discrete gestures
        gesture = "None"
        if count == 5:
            gesture = "Open Palm"
        elif count == 0:
            gesture = "Closed Fist"
        elif count == 1 and open_fingers[1] == 1: # Only index open
            gesture = "1 Finger"
        elif count == 2 and open_fingers[1] == 1 and open_fingers[2] == 1:
            gesture = "2 Fingers"
        elif count == 3 and open_fingers[1] == 1 and open_fingers[2] == 1 and open_fingers[3] == 1:
            gesture = "3 Fingers"
        elif count == 4 and open_fingers[0] == 0: # All except thumb
            gesture = "4 Fingers"
            
        return gesture, None

    def _check_swipe(self, center: Tuple[int, int], current_time: float) -> str:
        if self.prev_hand_center and (current_time - self.last_action_time) > self.swipe_cooldown:
            dx = center[0] - self.prev_hand_center[0]
            if dx > self.swipe_threshold:
                self.last_action_time = current_time
                self.prev_hand_center = center  # reset
                return "Swipe Right"
            elif dx < -self.swipe_threshold:
                self.last_action_time = current_time
                self.prev_hand_center = center  # reset
                return "Swipe Left"
        return "None"
