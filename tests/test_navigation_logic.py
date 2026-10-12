import pytest
from generated.navigation_logic import decide_next_move

def test_goal_ahead_not_blocked():
    state = {
        "goal_ahead": True,
        "goal_on_left": False,
        "goal_on_right": False,
        "front_blocked": False,
        "left_blocked": False,
        "right_blocked": False
    }
    assert decide_next_move(state) == "FORWARD"

def test_goal_on_left_not_blocked():
    state = {
        "goal_ahead": False,
        "goal_on_left": True,
        "goal_on_right": False,
        "front_blocked": False,
        "left_blocked": False,
        "right_blocked": False
    }
    assert decide_next_move(state) == "LEFT"

def test_goal_on_right_not_blocked():
    state = {
        "goal_ahead": False,
        "goal_on_left": False,
        "goal_on_right": True,
        "front_blocked": False,
        "left_blocked": False,
        "right_blocked": False
    }
    assert decide_next_move(state) == "RIGHT"

def test_front_blocked_left_free():
    state = {
        "goal_ahead": False,
        "goal_on_left": False,
        "goal_on_right": False,
        "front_blocked": True,
        "left_blocked": False,
        "right_blocked": False
    }
    assert decide_next_move(state) == "LEFT"

def test_front_blocked_right_free():
    state = {
        "goal_ahead": False,
        "goal_on_left": False,
        "goal_on_right": False,
        "front_blocked": True,
        "left_blocked": False,
        "right_blocked": False
    }
    assert decide_next_move(state) == "RIGHT"

def test_all_directions_blocked():
    state = {
        "goal_ahead": False,
        "goal_on_left": False,
        "goal_on_right": False,
        "front_blocked": True,
        "left_blocked": True,
        "right_blocked": True
    }
    assert decide_next_move(state) == "STOP"

def test_goal_ahead_front_blocked():
    state = {
        "goal_ahead": True,
        "goal_on_left": False,
        "goal_on_right": False,
        "front_blocked": True,
        "left_blocked": False,
        "right_blocked": False
    }
    assert decide_next_move(state) in ["LEFT", "RIGHT"]

def test_goal_on_left_left_blocked():
    state = {
        "goal_ahead": False,
        "goal_on_left": True,
        "goal_on_right": False,
        "front_blocked": False,
        "left_blocked": True,
        "right_blocked": False
    }
    assert decide_next_move(state) in ["FORWARD", "RIGHT"]

def test_goal_on_right_right_blocked():
    state = {
        "goal_ahead": False,
        "goal_on_left": False,
        "goal_on_right": True,
        "front_blocked": False,
        "left_blocked": False,
        "right_blocked": True
    }
    assert decide_next_move(state) in ["FORWARD", "LEFT"]