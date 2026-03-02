
import pygame
from utils.enums import TileVisibility



class Tile:
    def __init__(self, x, y, width, height, tile_type_data):
        self.grid_pos = (x, y)
        self.rect = pygame.Rect(x * width, y * height, width, height)

        self.type = tile_type_data.get("type", "default")
        self.name = tile_type_data.get("name", "Unknown")
        self.actions = tile_type_data.get("actions", [])
        self.walkable = tile_type_data.get("walkable", True)
        self.max_occupants = tile_type_data.get("max_occupants", 6)
        self.occupants = []
        self.event_trigger = None
        self.visibility_state = TileVisibility.HIDDEN

        self.standee_positions = self._generate_standee_slots()

    def _generate_standee_slots(self):
        slots = []
        w, h = self.rect.width, self.rect.height
        spacing = w // (self.max_occupants + 1)
        center_y = self.rect.top + h // 2
        size = min(w, h) // 6

        for i in range(self.max_occupants):
            x = self.rect.left + spacing * (i + 1)
            y = center_y
            slot_rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
            slots.append(slot_rect)
        return slots

    def add_occupant(self, entity):
        if len(self.occupants) >= self.max_occupants:
            return False
        self.occupants.append(entity)
        return True

    def remove_occupant(self, entity):
        if entity in self.occupants:
            self.occupants.remove(entity)
            return True
        return False

    def get_first_available_slot(self, entity_type="player"):
        if len(self.occupants) >= self.max_occupants:
            return None
        if entity_type == "enemy":
            return self.standee_positions[-(len([e for e in self.occupants if e.get("type") == "enemy"]) + 1)]
        else:
            return self.standee_positions[len([e for e in self.occupants if e.get("type") != "enemy"])]

    def draw_debug_slots(self, screen, offset_x=0, offset_y=0):
        for rect in self.standee_positions:
            offset_rect = rect.move(offset_x, offset_y)
            pygame.draw.rect(screen, (255, 255, 0), offset_rect, 1)
    def draw_standees(self, screen, offset_x=0, offset_y=0):
        if self.visibility_state.name != "VISIBLE":
            return
        for i, entity in enumerate(self.occupants):
            slot = self.standee_positions[i]
            offset_rect = slot.move(offset_x, offset_y)
            pygame.draw.circle(screen, (0, 150, 255), offset_rect.center, 6)