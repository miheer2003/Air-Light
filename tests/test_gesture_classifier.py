import pytest
from unittest.mock import MagicMock
from gesture_classifier import GestureClassifier

@pytest.fixture
def classifier():
    clf = GestureClassifier()
    # Mock detector to isolate classifier logic
    clf.detector = MagicMock()
    # Prevent swipe by default by setting hand center constant
    clf.detector.get_hand_center.return_value = (100, 100)
    clf.gesture_hold_threshold = 1
    return clf

def test_open_palm(classifier):
    # 5 open fingers
    classifier.detector.get_open_fingers.return_value = [1, 1, 1, 1, 1]
    classifier.detector.detect_pinch.return_value = (False, 0, None)
    
    gesture, val = classifier.process_hand([(0,0)]) # dummy lm_list
    assert gesture == "Open Palm"
    assert val is None

def test_closed_fist(classifier):
    # 0 open fingers
    classifier.detector.get_open_fingers.return_value = [0, 0, 0, 0, 0]
    classifier.detector.detect_pinch.return_value = (False, 0, None)
    
    gesture, val = classifier.process_hand([(0,0)])
    assert gesture == "Closed Fist"
    assert val is None

def test_pinch_brightness(classifier):
    # Pinch detected
    classifier.detector.get_open_fingers.return_value = [0, 0, 0, 0, 0]
    # Return (is_pinching, pinch_distance, center)
    classifier.detector.detect_pinch.return_value = (True, 100, (0,0))
    
    gesture, val = classifier.process_hand([(0,0)])
    assert gesture == "Pinch"
    assert val is not None
    assert 0 <= val <= 100

def test_one_finger(classifier):
    # Only index open
    classifier.detector.get_open_fingers.return_value = [0, 1, 0, 0, 0]
    classifier.detector.detect_pinch.return_value = (False, 0, None)
    
    gesture, val = classifier.process_hand([(0,0)])
    assert gesture == "1 Finger"

def test_swipe_right(classifier):
    classifier.prev_hand_center = (100, 100)
    classifier.detector.get_hand_center.return_value = (250, 100) # Moved right by 150 (>100)
    classifier.last_action_time = 0 # Cooldown passed
    
    gesture, val = classifier.process_hand([(0,0)])
    assert gesture == "Swipe Right"
