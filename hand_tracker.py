import cv2
import mediapipe as mp
from typing import List, Tuple, Any

class HandTracker:
    """
    Wrapper around MediaPipe Hands solution.
    """
    def __init__(self, max_hands: int = 2, min_detection_confidence: float = 0.7, min_tracking_confidence: float = 0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils

    def process_frame(self, frame) -> Tuple[Any, List[List[Tuple[int, int]]]]:
        """
        Processes a BGR OpenCV frame.
        Returns the processed frame (with drawings) and a list of hands,
        where each hand is a list of (x, y) coordinates for the 21 landmarks.
        """
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        hands_landmarks = []
        h, w, c = frame.shape
        
        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                # Draw landmarks on the frame
                self.mp_draw.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)
                
                # Extract pixel coordinates
                lm_list = []
                for id, lm in enumerate(hand_lms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append((cx, cy))
                    
                hands_landmarks.append(lm_list)
                
        return frame, hands_landmarks

    def close(self):
        self.hands.close()
