import pytest
from unittest.mock import MagicMock
from gesture_mapper import GestureMapper

@pytest.fixture
def mapper():
    mock_bulb = MagicMock()
    return GestureMapper(mock_bulb)

def test_open_palm_turns_on_bulb(mapper):
    mapper.handle_gesture("Open Palm")
    mapper.bulb.turn_on.assert_called_once()
    assert mapper.last_power_state == True

def test_closed_fist_turns_off_bulb(mapper):
    # First turn it on so the state allows turning off
    mapper.last_power_state = True
    # Bypass cooldown for test by artificially resetting it
    mapper.last_action_time = 0
    
    mapper.handle_gesture("Closed Fist")
    mapper.bulb.turn_off.assert_called_once()
    assert mapper.last_power_state == False

def test_pinch_sets_brightness(mapper):
    mapper.handle_gesture("Pinch", 50.0)
    mapper.bulb.set_brightness.assert_called_once_with(50)
    assert mapper.last_brightness == 50

def test_cooldown_prevents_spam(mapper):
    mapper.handle_gesture("Open Palm")
    mapper.bulb.turn_on.assert_called_once()
    
    # Reset mock to count calls again
    mapper.bulb.turn_on.reset_mock()
    
    # Try again immediately (cooldown is 0.5s)
    mapper.handle_gesture("Open Palm")
    mapper.bulb.turn_on.assert_not_called()
