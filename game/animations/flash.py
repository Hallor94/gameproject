class FlashEffect:
    def __init__(self, duration=30, max_intensity=255, base_color=(255, 255, 128)):
        self.duration = duration
        self.timer = 0
        self.max_intensity = max_intensity
        self.base_color = base_color

    def trigger(self):
        self.timer = self.duration

    def update_and_get_color(self):
        if self.timer <= 0:
            return None
        intensity = int(self.max_intensity * (self.timer / self.duration))
        r = min(255, self.base_color[0] * intensity // 255)
        g = min(255, self.base_color[1] * intensity // 255)
        b = min(255, self.base_color[2] * intensity // 255)
        self.timer -= 1
        return (r, g, b)
