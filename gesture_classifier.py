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
        self.brightness_ema = ExponentialMovingAverage(alpha=0.15)
        self.last_gesture = "None"
        self.gesture_hold_count = 0
        self.gesture_hold_threshold = 4  # Must see same gesture for 4 frames
        
        # For swipe detection
        self.prev_hand_center = None
        self.swipe_threshold = 130
        self.swipe_cooldown = 1.5

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
        
        # 3. Check for Pinch FIRST (before discrete gestures)
        is_pinching, pinch_dist, _ = self.detector.detect_pinch(lm_list)
        if is_pinching and pinch_dist < 180:
            min_d, max_d = config.pinch_min_dist, config.pinch_max_dist
            mapped_val = max(0, min(100, int(((pinch_dist - min_d) / (max_d - min_d)) * 100)))
            smoothed_val = self.brightness_ema.update(mapped_val)
            return "Pinch", smoothed_val
            
        # 4. Classify discrete gestures
        raw_gesture = self._classify_fingers(open_fingers, count, lm_list)
        
        # 5. Apply gesture hold filter
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
        
        # Open Palm: All 5 fingers open
        if count == 5:
            return "Open Palm"
            
        # Closed Fist: All fingers closed
        if count == 0:
            return "Closed Fist"
        
        # Thumbs Up: Only thumb open, pointing upward
        if open_fingers[0] == 1 and count == 1:
            if lm_list[4][1] < lm_list[2][1]:
                return "Thumbs Up"
                
        # Thumbs Down: Only thumb open, pointing down
        if open_fingers[0] == 1 and count == 1:
            if lm_list[4][1] > lm_list[2][1]:
                return "Thumbs Down"
        
        # Rock/Horns: Index and pinky open, others closed
        if open_fingers == [0, 1, 0, 0, 1] or open_fingers == [1, 1, 0, 0, 1]:
            return "Rock"
        
        # 1 Finger: Only index extended (thumb must be closed)
        if count == 1 and open_fingers[1] == 1 and open_fingers[0] == 0:
            return "1 Finger"
            
        # 2 Fingers: Index + Middle
        if count == 2 and open_fingers[1] == 1 and open_fingers[2] == 1:
            return "2 Fingers"
            
        # 3 Fingers: Index + Middle + Ring
        if count == 3 and open_fingers[1] == 1 and open_fingers[2] == 1 and open_fingers[3] == 1:
            return "3 Fingers"
            
        # 4 Fingers: All except thumb
        if count == 4 and open_fingers[0] == 0:
            return "4 Fingers"
            
        return "None"

    def _check_swipe(self, center: Tuple[int, int], current_time: float) -> str:
        if self.prev_hand_center and (current_time - self.last_action_time) > self.swipe_cooldown:
            dx = center[0] - self.prev_hand_center[0]
            if dx > self.swipe_threshold:
                self.last_action_time = current_time
                self.prev_hand_center = center
                return "Swipe Right"
            elif dx < -self.swipe_threshold:
                self.last_action_time = current_time
                self.prev_hand_center = center
                return "Swipe Left"
        return "None"
