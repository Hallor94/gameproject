# file: game/input/input_router.py

import pygame
from input.keymaps import DEFAULT_KEYMAP
from utils import globals as G

class InputRouter:
    def __init__(self, keymap=None):
        self.keymap = keymap or DEFAULT_KEYMAP
        self.subscribers = []

    def register(self, callback):
        """Register a function that takes (action: str) → returns True if handled."""
        if callback not in self.subscribers:
            self.subscribers.append(callback)

    def unregister(self, callback):
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        action = self.keymap.get(event.key)
        if not action:
            return

        for callback in self.subscribers:
            try:
                if callback(action):
                    break
            except AttributeError as e:
                if "'NoneType' object has no attribute 'ui_mode'" in str(e):
                    continue  # Gamestate not ready — skip this subscriber
                raise  # re-raise other errors