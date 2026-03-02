import pygame
from animations.flash import FlashEffect
from map.visibility_manager import TileVisibility
from utils.image_cache import get_icon
from utils.logger import log_debug
from utils import globals as G
from ui.components.portrait_box import PortraitBox
from utils.enums import UIMode

class HUD:
    def __init__(self):
        self.round_flash = FlashEffect(duration=30, max_intensity=255, base_color=(255, 255, 128))
        self.first_icon = get_icon("firstplayer", size=(50, 50))
        self.combat_icon = get_icon("combat", size=(50, 50))
        self.camera_icon = get_icon("camera", size=(50, 50))
        self.hourglass_icon = get_icon("hourglass", size=(50, 50))
        self.DEFAULT_PORTRAIT_SCALE = 0.85
        self.force_wide_all = False  # Set to True to disable compact mode entirely
        G.gamestate.register_listener("round_started", self.on_round_started)

        # Dummy to get height of player boxes dynamically
        icons = getattr(G, "stat_icons", {})
        dummy = PortraitBox(None, icons, scale=1.0)
        self.portrait_height = dummy.HEIGHT


    def on_round_started(self, round_number):
        self.round_flash.trigger()

    def draw_portrait(self, surface, player, box, x, y, compact=False):
        is_active = (player == G.gamestate.get_active_player())
        outline_color = (255, 220, 0) if is_active else (100, 100, 100)
        outline_thickness = 2

        # Choose correct height
        height = box.get_height(compact=compact)

        # Single rectangular outline
        border_rect = pygame.Rect(x - 3, y - 3, box.WIDTH + 6, height + 6)
        pygame.draw.rect(surface, outline_color, border_rect, outline_thickness)

        # Vertical name label
        font = G.hud_font
        name_surf = font.render(player.player_name, True, (255, 255, 255))
        name_surf_rotated = pygame.transform.rotate(name_surf, 90)
        name_x = x - name_surf_rotated.get_width() - 12
        name_y = y + (height - name_surf_rotated.get_height()) // 2
        surface.blit(name_surf_rotated, (name_x, name_y))

        # Draw correct box
        if compact:
            box.draw_compact(surface, x, y)
        else:
            box.draw_wide(surface, x, y)

    def draw_player_panel(self, surface):
        spacing = 26
        x = 35
        y = 30

        for player in G.gamestate.players:
            is_active = (player == G.gamestate.get_active_player())
            compact = not is_active and not self.force_wide_all
            scale = 1.0 if not compact else 0.85
            box = PortraitBox(player, G.stat_icons, scale=scale)

            self.draw_portrait(surface, player, box, x, y, compact=compact)
            y += box.get_total_height(compact=compact) + spacing

    def draw_enemy_panel(self, surface):
        spacing = 20
        scale = 0.7
        x = surface.get_width() - 35  # Anchor to right edge
        y = 30

        for enemy in G.gamestate.enemies:
            tile = getattr(enemy, "tile", None)
            if not tile or tile.visibility_state != TileVisibility.VISIBLE:
                continue

            box = PortraitBox(enemy, G.stat_icons, scale=scale)
            height = box.get_total_height(compact=True)

            # Right-align the box
            x_aligned = x - box.WIDTH

            # Draw outline and name if needed
            pygame.draw.rect(surface, (100, 0, 0), pygame.Rect(x_aligned - 3, y - 3, box.WIDTH + 6, height + 6), 2)

            box.draw_compact(surface, x_aligned, y)
            y += height + spacing


    def draw_camera_mode(self, surface):
        icon = self.camera_icon
        mode_index = G.gamemap.camera.camera_mode_index
        mode_name = G.gamemap.camera.CAMERA_MODES[mode_index].capitalize()
        label = f"<TAB> {mode_name} Mode"

        font = G.hud_font
        text_surf = font.render(label, True, (255, 255, 255))

        icon_size = 50
        padding = 10
        spacing = 12
        text_w, text_h = text_surf.get_size()

        total_width = icon_size + spacing + text_w + padding * 2
        total_height = max(icon_size, text_h) + padding * 2

        x = surface.get_width() // 2 - total_width // 2
        y = surface.get_height() - total_height - 10

        # Draw background
        bg_rect = pygame.Rect(x, y, total_width, total_height)
        pygame.draw.rect(surface, (20, 20, 20), bg_rect, border_radius=6)
        pygame.draw.rect(surface, (80, 80, 80), bg_rect, 2, border_radius=6)

        # Draw icon (locked position)
        icon_y = y + (total_height - icon_size) // 2
        surface.blit(icon, (x + padding, icon_y))

        # Draw label text
        text_x = x + padding + icon_size + spacing
        text_y = y + (total_height - text_h) // 2
        surface.blit(text_surf, (text_x, text_y))


    def draw_round_tracker(self, surface):
        font = G.menu_font
        text = font.render(G.gamestate.get_round_display_text(), True, (255, 255, 255))
        text_w, text_h = text.get_size()

        banner_padding = 10
        icon_size = 60
        spacing = 10

        banner_width = icon_size + spacing + text_w + banner_padding * 2
        banner_height = max(text_h, icon_size) + banner_padding

        banner_x = surface.get_width() // 2 - banner_width // 2
        banner_y = 12

        pygame.draw.rect(surface, (20, 20, 20), (banner_x, banner_y, banner_width, banner_height), border_radius=8)
        border_color = self.round_flash.update_and_get_color()
        if border_color:
            pygame.draw.rect(surface, border_color, (banner_x, banner_y, banner_width, banner_height), 3, border_radius=8)
        else:
            pygame.draw.rect(surface, (100, 100, 100), (banner_x, banner_y, banner_width, banner_height), 2, border_radius=8)

        icon_y = banner_y + banner_height // 2 - icon_size // 2
        text_y = banner_y + banner_height // 2 - text_h // 2

        if self.hourglass_icon:
            surface.blit(self.hourglass_icon, (banner_x + banner_padding, icon_y))

        surface.blit(text, (banner_x + banner_padding + icon_size + spacing, text_y))

    def draw_board_state_debug(self, surface):
        """
        Draws a small debug box showing the last MQTT board state.
        Positioned next to the round tracker.
        """

        state = getattr(G, "last_board_state", None)
        if not isinstance(state, list) or not state:
            if state is not None:
                log_debug("MQTT", f"HUD draw: Unexpected state type: {type(state)} — {state}")
            return

        font = G.font
        lines = []

        for obj in state[:4]:
            obj_type = obj.get("type", "")
            raw_label = obj.get("label") or obj.get("value") or obj.get("id") or obj.get("face") or "<unknown>"

            if obj_type == "dice":
                label = f"Dice: {raw_label}"
            elif obj_type == "card":
                label = f"Card: {raw_label}"
            else:
                label = raw_label

            confidence = obj.get("confidence", None)
            lines.append(f"• {label}")
            if confidence is not None:
                lines.append(f"  conf: {confidence:.2f}")


        if not lines:
            return
    
        total = sum(int(o["value"]) for o in state if o.get("type") == "dice" and o.get("is_confident", True))
        lines.append(f"Dice Total: {total}")

        rendered = [font.render(line, True, (255, 255, 255)) for line in lines]
        width = max(r.get_width() for r in rendered) + 16
        height = sum(r.get_height() for r in rendered) + 16

        # Position just to the right of round tracker
        banner_padding = 10
        icon_size = 60
        spacing = 10
        text = G.menu_font.render(G.gamestate.get_round_display_text(), True, (255, 255, 255))
        banner_width = icon_size + spacing + text.get_width() + banner_padding * 2
        banner_x = surface.get_width() // 2 - banner_width // 2
        banner_y = 12

        x = banner_x + banner_width + 12
        y = banner_y

        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (30, 30, 30), rect, border_radius=6)
        pygame.draw.rect(surface, (80, 80, 80), rect, 2, border_radius=6)

        cy = y + 8
        for r in rendered:
            surface.blit(r, (x + 8, cy))
            cy += r.get_height()



    def draw(self, surface):
        player = G.gamestate.get_active_player()

        self.draw_player_panel(surface)
        self.draw_enemy_panel(surface) 
        self.draw_camera_mode(surface)
        self.draw_round_tracker(surface)
        self.draw_board_state_debug(surface)

        # Loading icon
        if G.is_recognizer_busy:
            G.loading_icon.update()
            screen_w, screen_h = surface.get_size()
            pos = (screen_w - 500, screen_h - 180)  # bottom right corner
            G.loading_icon.draw(surface, pos)
                
        if G.context_menu and G.gamestate.ui_mode != UIMode.INSPECTION:
            G.context_menu.update_for_player_tile(player.tile.grid_pos)
            G.context_menu.draw(surface, player.tile)