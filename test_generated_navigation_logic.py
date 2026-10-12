import unittest
from navigation_logic import decide_next_move

class TestNavigationLogic(unittest.TestCase):

    def test_goal_ahead_and_clear(self):
        state = {
            "goal_ahead": True,
            "goal_on_left": False,
            "goal_on_right": False,
            "front_blocked": False,
            "left_blocked": False,
            "right_blocked": False
        }
        self.assertEqual(decide_next_move(state), "FORWARD")

    def test_goal_on_left_and_clear(self):
        state = {
            "goal_ahead": False,
            "goal_on_left": True,
            "goal_on_right": False,
            "front_blocked": False,
            "left_blocked": False,
            "right_blocked": False
        }
        self.assertEqual(decide_next_move(state), "LEFT")

    def test_goal_on_right_and_clear(self):
        state = {
            "goal_ahead": False,
            "goal_on_left": False,
            "goal_on_right": True,
            "front_blocked": False,
            "left_blocked": False,
            "right_blocked": False
        }
        self.assertEqual(decide_next_move(state), "RIGHT")

    def test_all_blocked(self):
        state = {
            "goal_ahead": True,
            "goal_on_left": False,
            "goal_on_right": False,
            "front_blocked": True,
            "left_blocked": True,
            "right_blocked": True
        }
        self.assertEqual(decide_next_move(state), "STOP")

    def test_goal_ahead_but_front_blocked_goes_left(self):
        state = {
            "goal_ahead": True,
            "goal_on_left": False,
            "goal_on_right": False,
            "front_blocked": True,
            "left_blocked": False,
            "right_blocked": False
        }
        self.assertEqual(decide_next_move(state), "LEFT")

    def test_no_goal_but_front_clear(self):
        state = {
            "goal_ahead": False,
            "goal_on_left": False,
            "goal_on_right": False,
            "front_blocked": False,
            "left_blocked": False,
            "right_blocked": False
        }
        self.assertEqual(decide_next_move(state), "FORWARD")

if __name__ == '__main__':
    unittest.main()
