import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import List, Tuple, Any

class HandTracker:
    """
    Wrapper around MediaPipe Hands solution (Tasks API).
    """
    def __init__(self, max_hands: int = 2, min_detection_confidence: float = 0.7, min_tracking_confidence: float = 0.7):
        base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        
        self.connections = [
            (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), 
            (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15), 
            (15, 16), (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)
        ]

    def process_frame(self, frame) -> Tuple[Any, List[List[Tuple[int, int]]]]:
        """
        Processes a BGR OpenCV frame.
        Returns the processed frame (with drawings) and a list of hands,
        where each hand is a list of (x, y) coordinates for the 21 landmarks.
        """
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        # Detection
        detection_result = self.landmarker.detect(mp_image)
        
        hands_landmarks = []
        h, w, c = frame.shape
        
        if detection_result.hand_landmarks:
            for hand_lms in detection_result.hand_landmarks:
                lm_list = []
                for lm in hand_lms:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append((cx, cy))
                hands_landmarks.append(lm_list)
                
                # Draw manually since solutions drawing utils is missing
                for cx, cy in lm_list:
                    cv2.circle(frame, (cx, cy), 4, (0, 255, 0), cv2.FILLED)
                for conn in self.connections:
                    p1 = lm_list[conn[0]]
                    p2 = lm_list[conn[1]]
                    cv2.line(frame, p1, p2, (255, 0, 0), 2)
                    
        return frame, hands_landmarks

    def close(self):
        if hasattr(self.landmarker, 'close'):
            self.landmarker.close()
