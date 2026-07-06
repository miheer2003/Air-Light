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
        self.brightness_ema = ExponentialMovingAverage(alpha=0.2)  # Smoother alpha
        self.last_gesture = "None"
        self.gesture_hold_count = 0  # Require multiple frames for a gesture to register
        self.gesture_hold_threshold = 3  # Must see same gesture for 3 frames
        
        # For swipe detection
        self.prev_hand_center = None
        self.swipe_threshold = 120  # pixels to move to register a swipe (increased)
        self.swipe_cooldown = 1.2   # seconds (increased)

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
        raw_gesture = self._classify_fingers(open_fingers, count, lm_list)
        
        # 5. Apply gesture hold filter (require N consecutive frames)
        if raw_gesture == self.last_gesture:
            self.gesture_hold_count += 1
        else:
            self.gesture_hold_count = 1
            self.last_gesture = raw_gesture
            
        if self.gesture_hold_count >= self.gesture_hold_threshold:
            return raw_gesture, None
        
        return "None", None
    
    def _classify_fingers(self, open_fingers: List[int], count: int, lm_list: List[Tuple[int, int]]) -> str:
        """Classify finger states into named gestures."""
        # Thumb=0, Index=1, Middle=2, Ring=3, Pinky=4
        
        # Thumbs Up: Only thumb open
        if open_fingers[0] == 1 and count == 1:
            # Verify thumb is pointing upward (tip above base)
            if lm_list[4][1] < lm_list[2][1]:  # y-coordinate: smaller = higher
                return "Thumbs Up"
                
        # Thumbs Down: Only thumb open, pointing down
        if open_fingers[0] == 1 and count == 1:
            if lm_list[4][1] > lm_list[2][1]:
                return "Thumbs Down"
        
        # Rock/Horns: Index and pinky open, others closed
        if open_fingers == [0, 1, 0, 0, 1] or open_fingers == [1, 1, 0, 0, 1]:
            return "Rock"
        
        # Standard gestures
        if count == 5:
            return "Open Palm"
        elif count == 0:
            return "Closed Fist"
        elif count == 1 and open_fingers[1] == 1:  # Only index open
            return "1 Finger"
        elif count == 2 and open_fingers[1] == 1 and open_fingers[2] == 1:
            return "2 Fingers"
        elif count == 3 and open_fingers[1] == 1 and open_fingers[2] == 1 and open_fingers[3] == 1:
            return "3 Fingers"
        elif count == 4 and open_fingers[0] == 0:  # All except thumb
            return "4 Fingers"
            
        return "None"

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
