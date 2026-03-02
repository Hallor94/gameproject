# file: animations/movement_animator.py

class MovementAnimator:
    def __init__(self):
        self.active_moves = []

    def start(self, entity, start_world_x, start_world_y, end_world_x, end_world_y, duration=0.3, on_complete=None):
        move = {
            "entity": entity,
            "start_world_x": start_world_x,
            "start_world_y": start_world_y,
            "end_world_x": end_world_x,
            "end_world_y": end_world_y,
            "duration": duration,
            "elapsed": 0.0,
            "on_complete": on_complete
        }
        self.active_moves.append(move)

    def update(self, dt):
        remaining = []
        for move in self.active_moves:
            move["elapsed"] += dt
            t = min(move["elapsed"] / move["duration"], 1.0)
            eased = t * t * (3 - 2 * t)  # smoothstep easing

            # Interpolate world position and apply
            x = (1 - eased) * move["start_world_x"] + eased * move["end_world_x"]
            y = (1 - eased) * move["start_world_y"] + eased * move["end_world_y"]
            move["entity"].world_x = x
            move["entity"].world_y = y

            if t < 1.0:
                remaining.append(move)
            else:
                if move.get("on_complete"):
                    move["on_complete"](move["entity"])
        self.active_moves = remaining

    def is_active(self):
        return bool(self.active_moves)
