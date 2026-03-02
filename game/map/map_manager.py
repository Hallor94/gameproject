
# Central map logic and state
import pygame
import random
from .tile_loader import load_tile_types
from .tile import Tile
from .tile import TileVisibility
from utils.enums import FogOfWarMode


class MapManager:
    def __init__(self, rows, cols, tile_width, tile_height, fog_mode=FogOfWarMode.NORMAL):
        self.rows = rows
        self.cols = cols
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.offset_x = 0
        self.offset_y = 0
        self.fog_mode = fog_mode

        self.tile_types = load_tile_types()
        self.default_tile = {
            "type": "empty",
            "name": "Empty",
            "actions": [],
            "walkable": True
        }
        self.tile_limits = {
            "sleeping_quarters": 2,
            "kitchen": 1,
            "canteen": 1,
            "storage": 3,
            "armory": 2,
            "power_core": 1,
            "lock": 1,
            "corridor": -1,
            "office": 2
        }

        self.tiles = self.generate_static_map()
        self.doors = []

    def generate_static_map(self):
        tiles_flat = self.rows * self.cols
        tile_pool = []

        for tile_type in self.tile_types:
            type_id = tile_type["type"]
            limit = self.tile_limits.get(type_id, -1)
            if limit == -1:
                tile_pool.extend([tile_type] * tiles_flat)
            else:
                tile_pool.extend([tile_type] * limit)

        if not tile_pool:
            tile_pool = [self.default_tile] * tiles_flat

        random.shuffle(tile_pool)
        tile_pool = tile_pool[:tiles_flat]

        index = 0
        tiles = []
        for row in range(self.rows):
            tile_row = []
            for col in range(self.cols):
                tile_type = tile_pool[index] if index < len(tile_pool) else self.default_tile
                tile = Tile(col, row, self.tile_width, self.tile_height, tile_type)
                tile.visibility_state = TileVisibility.HIDDEN
                tile_row.append(tile)
                index += 1
            tiles.append(tile_row)

        return tiles
    
    def draw(self, screen):
        font = pygame.font.SysFont(None, 20)

        for row in self.tiles:
            for tile in row:
                offset_rect = tile.rect.move(self.offset_x, self.offset_y)

                
                if tile.visibility_state == TileVisibility.HIDDEN:
                    if self.fog_mode == FogOfWarMode.KNOWN_LAYOUT:
                        pygame.draw.rect(screen, (40, 40, 60), offset_rect)
                        pygame.draw.rect(screen, (80, 80, 80), offset_rect, 1)
                        name_surf = font.render(tile.name, True, (80, 80, 80))
                        screen.blit(name_surf, (offset_rect.x + 4, offset_rect.y + 4))
                    else:
                        pygame.draw.rect(screen, (20, 20, 20), offset_rect)
                        pygame.draw.rect(screen, (40, 40, 40), offset_rect, 1)

                elif tile.visibility_state == TileVisibility.DISCOVERED:
                    pygame.draw.rect(screen, (60, 60, 60), offset_rect)
                    pygame.draw.rect(screen, (80, 80, 80), offset_rect, 2)
                    name_surf = font.render(tile.name, True, (100, 100, 100))
                    screen.blit(name_surf, (offset_rect.x + 4, offset_rect.y + 4))
                elif tile.visibility_state == TileVisibility.VISIBLE:
                    pygame.draw.rect(screen, (100, 100, 100), offset_rect)
                    pygame.draw.rect(screen, (80, 80, 80), offset_rect, 2)
                    name_surf = font.render(tile.name, True, (255, 255, 255))
                    screen.blit(name_surf, (offset_rect.x + 4, offset_rect.y + 4))

                tile.draw_debug_slots(screen, self.offset_x, self.offset_y)

        for door in self.doors:
            t1_state = door.tile_a.visibility_state
            t2_state = door.tile_b.visibility_state

            if not (
                t1_state in (TileVisibility.VISIBLE, TileVisibility.DISCOVERED) or
                t2_state in (TileVisibility.VISIBLE, TileVisibility.DISCOVERED)
            ):
                continue  # skip hidden doors

            rect_a = door.tile_a.rect.move(self.offset_x, self.offset_y)
            rect_b = door.tile_b.rect.move(self.offset_x, self.offset_y)
            center_a = rect_a.center
            center_b = rect_b.center
            mid_x = (center_a[0] + center_b[0]) // 2
            mid_y = (center_a[1] + center_b[1]) // 2
            color = (0, 255, 0) if door.open else (255, 0, 0)
            pygame.draw.circle(screen, color, (mid_x, mid_y), 8)


    def get_door_between(self, tile1, tile2):
        key = frozenset((tile1, tile2))
        for door in self.doors:
            if frozenset((door.tile_a, door.tile_b)) == key:
                return door
        return None

    def can_move_between(self, tile1, tile2):
        door = self.get_door_between(tile1, tile2)
        if door:
            return door.open
        return False

    def get_adjacent_tiles(self, tile):
        x, y = tile.grid_pos
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= ny < self.rows and 0 <= nx < self.cols:
                neighbors.append(self.tiles[ny][nx])
        return neighbors

    def can_see_through(self, tile_a, tile_b):
        door = self.get_door_between(tile_a, tile_b)
        return door is not None and door.open

    def update_visibility(self, player_tiles):
        for row in self.tiles:
            for tile in row:
                if self.fog_mode == FogOfWarMode.BOARDGAME:
                    tile.visibility_state = TileVisibility.VISIBLE
                elif self.fog_mode == FogOfWarMode.KNOWN_LAYOUT:
                    if tile.visibility_state == TileVisibility.VISIBLE:
                        tile.visibility_state = TileVisibility.DISCOVERED
                else:  # NORMAL
                    if tile.visibility_state == TileVisibility.VISIBLE:
                        tile.visibility_state = TileVisibility.DISCOVERED

        if self.fog_mode in [FogOfWarMode.NORMAL, FogOfWarMode.KNOWN_LAYOUT]:
            for tile in player_tiles:
                tile.visibility_state = TileVisibility.VISIBLE
                for neighbor in self.get_adjacent_tiles(tile):
                    if self.can_see_through(tile, neighbor):
                        neighbor.visibility_state = TileVisibility.VISIBLE

