def decide_next_move(state):
    if state['goal_ahead'] and not state['front_blocked']:
        return "FORWARD"
    if state['goal_on_left'] and not state['left_blocked']:
        return "LEFT"
    if state['goal_on_right'] and not state['right_blocked']:
        return "RIGHT"
    if not state['front_blocked']:
        return "FORWARD"
    if not state['left_blocked']:
        return "LEFT"
    if not state['right_blocked']:
        return "RIGHT"
    return "STOP"
