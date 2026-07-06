from typing import List, Tuple
from utils import calculate_distance, calculate_angle

class GestureDetector:
    """
    Analyzes raw MediaPipe landmarks to extract basic features
    (e.g., open fingers, pinch distance, hand center).
    """
    def __init__(self):
        # Finger tip IDs in MediaPipe Hands
        self.tip_ids = [4, 8, 12, 16, 20]

    def get_hand_center(self, lm_list: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Returns the approximate center of the hand based on the wrist and knuckles."""
        if not lm_list or len(lm_list) < 21:
            return (0, 0)
        cx = (lm_list[0][0] + lm_list[5][0] + lm_list[17][0]) // 3
        cy = (lm_list[0][1] + lm_list[5][1] + lm_list[17][1]) // 3
        return (cx, cy)

    def is_finger_open(self, lm_list: List[Tuple[int, int]], finger_tip_id: int) -> bool:
        """Determines if a specific finger is open."""
        if not lm_list or len(lm_list) < 21:
            return False
            
        if finger_tip_id == 4:
            dist_tip = calculate_distance(lm_list[4], lm_list[17])
            dist_base = calculate_distance(lm_list[2], lm_list[17])
            return dist_tip > dist_base * 1.15  # Add margin to avoid false positives
        else:
            dist_tip = calculate_distance(lm_list[finger_tip_id], lm_list[0])
            dist_pip = calculate_distance(lm_list[finger_tip_id - 2], lm_list[0])
            return dist_tip > dist_pip * 1.1  # Add margin

    def get_open_fingers(self, lm_list: List[Tuple[int, int]]) -> List[int]:
        """Returns a list of 1s and 0s indicating which fingers are open."""
        fingers = []
        for tip_id in self.tip_ids:
            fingers.append(1 if self.is_finger_open(lm_list, tip_id) else 0)
        return fingers

    def count_open_fingers(self, lm_list: List[Tuple[int, int]]) -> int:
        """Returns the number of open fingers (0-5)."""
        return sum(self.get_open_fingers(lm_list))

    def detect_pinch(self, lm_list: List[Tuple[int, int]]) -> Tuple[bool, float, Tuple[int, int]]:
        """
        Detects if thumb (4) and index finger (8) are pinching.
        Strict: requires thumb+index close AND middle/ring/pinky closed.
        Returns: (is_pinching, distance, midpoint)
        """
        if not lm_list or len(lm_list) < 21:
            return False, 0.0, (0, 0)
            
        thumb_tip = lm_list[4]
        index_tip = lm_list[8]
        
        dist = calculate_distance(thumb_tip, index_tip)
        cx = (thumb_tip[0] + index_tip[0]) // 2
        cy = (thumb_tip[1] + index_tip[1]) // 2
        
        # Check other fingers are closed
        middle_open = self.is_finger_open(lm_list, 12)
        ring_open = self.is_finger_open(lm_list, 16)
        pinky_open = self.is_finger_open(lm_list, 20)
        
        # For pinch: index must be partially extended (not fully curled like a fist)
        # Check that index tip is further from wrist than index PIP
        index_tip_dist = calculate_distance(lm_list[8], lm_list[0])
        index_mcp_dist = calculate_distance(lm_list[5], lm_list[0])
        index_extended = index_tip_dist > index_mcp_dist * 0.7
        
        # Pinch requires:
        # 1. Middle, ring closed
        # 2. Index partially extended (not fist)
        # 3. Thumb and index within reasonable range
        is_pinching = (not middle_open and not ring_open and 
                      index_extended and dist < 200)
        
        return is_pinching, dist, (cx, cy)
