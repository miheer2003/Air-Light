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
        # Average of wrist (0), index knuckle (5), and pinky knuckle (17)
        cx = (lm_list[0][0] + lm_list[5][0] + lm_list[17][0]) // 3
        cy = (lm_list[0][1] + lm_list[5][1] + lm_list[17][1]) // 3
        return (cx, cy)

    def is_finger_open(self, lm_list: List[Tuple[int, int]], finger_tip_id: int) -> bool:
        """Determines if a specific finger is open."""
        if not lm_list or len(lm_list) < 21:
            return False
            
        # Thumb logic (different from other fingers because it moves horizontally relative to palm)
        if finger_tip_id == 4:
            # Simple heuristic: Thumb tip (4) is further from pinky knuckle (17) than thumb base (2)
            dist_tip = calculate_distance(lm_list[4], lm_list[17])
            dist_base = calculate_distance(lm_list[2], lm_list[17])
            return dist_tip > dist_base
        else:
            # Other fingers: Tip (e.g., 8) is higher (smaller y) than the PIP joint (e.g., 6)
            # This assumes an upright hand. A more robust way is distance to wrist (0)
            dist_tip = calculate_distance(lm_list[finger_tip_id], lm_list[0])
            dist_pip = calculate_distance(lm_list[finger_tip_id - 2], lm_list[0])
            return dist_tip > dist_pip

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
        Returns: (is_pinching, distance, midpoint)
        """
        if not lm_list or len(lm_list) < 21:
            return False, 0.0, (0, 0)
            
        thumb_tip = lm_list[4]
        index_tip = lm_list[8]
        
        dist = calculate_distance(thumb_tip, index_tip)
        cx = (thumb_tip[0] + index_tip[0]) // 2
        cy = (thumb_tip[1] + index_tip[1]) // 2
        
        # Other fingers should generally be closed for a clean pinch
        middle_open = self.is_finger_open(lm_list, 12)
        ring_open = self.is_finger_open(lm_list, 16)
        pinky_open = self.is_finger_open(lm_list, 20)
        
        # Consider it a pinch if distance is reasonable and other fingers are mostly closed
        is_pinching = not middle_open and not ring_open
        
        return is_pinching, dist, (cx, cy)
