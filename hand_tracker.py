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
                
                # Draw minimal HUD brackets around the hand
                x_coords = [cx for cx, cy in lm_list]
                y_coords = [cy for cx, cy in lm_list]
                min_x, max_x = min(x_coords) - 20, max(x_coords) + 20
                min_y, max_y = min(y_coords) - 20, max(y_coords) + 20
                
                bracket_color = (0, 255, 100) # Acid Green
                b_len = 12
                thick = 2
                cv2.line(frame, (min_x, min_y), (min_x + b_len, min_y), bracket_color, thick)
                cv2.line(frame, (min_x, min_y), (min_x, min_y + b_len), bracket_color, thick)
                cv2.line(frame, (max_x, min_y), (max_x - b_len, min_y), bracket_color, thick)
                cv2.line(frame, (max_x, min_y), (max_x, min_y + b_len), bracket_color, thick)
                cv2.line(frame, (min_x, max_y), (min_x + b_len, max_y), bracket_color, thick)
                cv2.line(frame, (min_x, max_y), (min_x, max_y - b_len), bracket_color, thick)
                cv2.line(frame, (max_x, max_y), (max_x - b_len, max_y), bracket_color, thick)
                cv2.line(frame, (max_x, max_y), (max_x, max_y - b_len), bracket_color, thick)

                # Draw skeleton (White lines, Green joints)
                for conn in self.connections:
                    p1 = lm_list[conn[0]]
                    p2 = lm_list[conn[1]]
                    cv2.line(frame, p1, p2, (200, 200, 200), 1)
                    
                for cx, cy in lm_list:
                    cv2.circle(frame, (cx, cy), 3, (0, 255, 100), cv2.FILLED)
                    
        return frame, hands_landmarks

    def close(self):
        if hasattr(self.landmarker, 'close'):
            self.landmarker.close()
