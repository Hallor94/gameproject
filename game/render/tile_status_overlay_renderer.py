# file: render/tile_status_overlay_renderer.py

import pygame
from animations.flicker import FlickerEffect
from utils.enums import TileOverlayState, TileVisibility
from utils.image_cache import get_overlay
from utils.logger import log_warn


class TileStatusOverlayRenderer:
    def __init__(self):
        self.overlay_layers = {"behind": [], "above": []}
        self.flickers_by_tile = {}

    def get_flicker_for(self, tile):
        key = (tile.grid_x, tile.grid_y)
        if key not in self.flickers_by_tile:
            self.flickers_by_tile[key] = FlickerEffect(seed=sum(key))
        effect = self.flickers_by_tile[key]
        effect.update(dt=1)
        return effect

    def register_overlay(self, name, draw_function, layer="behind"):
        """
        Register an overlay function to a draw phase: 'behind' (under standees) or 'above' (over standees).
        Each draw_function takes (surface, tile, rect).
        """
        if layer not in self.overlay_layers:
            raise ValueError(f"[Overlay] Invalid layer name: {layer}")
        self.overlay_layers[layer].append((name, draw_function))

    def draw_phase(self, surface, tile, camera, phase):
        if tile.visibility_state.name != "VISIBLE":
            return
        rect = camera.get_scaled_rect(tile.world_rect)
        for name, fn in self.overlay_layers.get(phase, []):
            fn(surface, tile, rect)

# === Internal global instance ===
_tile_status_renderer = TileStatusOverlayRenderer()

# === Layer: Static light fixture (behind standee) ===
def draw_fixture(surface, tile, rect):
    if tile.tile_overlay_status == TileOverlayState.FIRE:
        return
    try:
        img = get_overlay(
            "overlay_lightfixture_on" if tile.light_on else "overlay_lightfixture_off",
            size=(rect.width, rect.height)
        )
        surface.blit(img, rect.topleft)
    except Exception as e:
        log_warn("TileOverlay", f"Failed to load lamp image: {e}", file=__file__)

def draw_light_beam(surface, tile, rect):
    if tile.tile_overlay_status == TileOverlayState.FIRE:
        return
    
    if not getattr(tile, "light_on", True):
        return

    try:
        beam_img = get_overlay("overlay_light", size=(rect.width, rect.height))
        if beam_img is None:
            return

        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for y in range(rect.height):
            alpha = int(120 * (1.0 - (y / rect.height) ** 1.8))  # Fade faster toward bottom
            pygame.draw.line(mask, (255, 255, 255, alpha), (0, y), (rect.width, y))

        faded_beam = beam_img.copy()
        faded_beam.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(faded_beam, rect.topleft)

    except Exception as e:
        log_warn("TileOverlay", f"Failed to render light beam: {e}", file=__file__)

def draw_darkness_overlay(surface, tile, rect):
    if tile.tile_overlay_status == TileOverlayState.FIRE:
        return
    
    if getattr(tile, "light_on", True):
        return

    darkness = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    darkness.fill((0, 0, 0, 180))  # Tune alpha to match your style
    surface.blit(darkness, rect.topleft)

# === Public drawing function ===
def draw_tile_status(surface, tile, camera, phase="behind"):
    _tile_status_renderer.draw_phase(surface, tile, camera, phase)

def draw_fire_base(surface, tile, rect):
    if tile.tile_overlay_status != TileOverlayState.FIRE:
        return
    try:
        img = get_overlay("overlay_flame", size=(rect.width, rect.height))
        if img:
            flicker = _tile_status_renderer.get_flicker_for(tile)
            alpha = flicker.get_alpha()

            flame = img.copy()
            flame.set_alpha(alpha)
            surface.blit(flame, rect.topleft)
    except Exception as e:
        log_warn("TileOverlay", f"Failed to render fire base: {e}", file=__file__)

def draw_fire_smoke(surface, tile, rect):
    if tile.tile_overlay_status != TileOverlayState.FIRE:
        return
    try:
        img = get_overlay("overlay_smoke", size=(rect.width, rect.height))
        if img:
            flicker = _tile_status_renderer.get_flicker_for(tile)
            alpha = flicker.get_alpha()

            smoke = img.copy()
            smoke.set_alpha(220+int(alpha/10))
            surface.blit(smoke, rect.topleft)
    except Exception as e:
        log_warn("TileOverlay", f"Failed to render fire smoke: {e}", file=__file__)


def draw_fire_glow(surface, tile, rect):
    if tile.tile_overlay_status != TileOverlayState.FIRE:
        return

    try:
        flicker = _tile_status_renderer.get_flicker_for(tile)
        alpha = flicker.get_alpha()

        glow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        glow.fill((200, 80, 0, int(alpha * 0.6)))

        surface.blit(glow, rect.topleft)
        

    except Exception as e:
        log_warn("TileOverlay", f"Failed to render fire glow: {e}", file=__file__)



# === Register built-in overlays ===
_tile_status_renderer.register_overlay("fixture", draw_fixture, layer="behind")
_tile_status_renderer.register_overlay("light_beam", draw_light_beam, layer="above")
_tile_status_renderer.register_overlay("darkness", draw_darkness_overlay, layer="above")
_tile_status_renderer.register_overlay("fire_base", draw_fire_base, layer="behind")
_tile_status_renderer.register_overlay("fire_smoke", draw_fire_smoke, layer="above")
_tile_status_renderer.register_overlay("fire_glow", draw_fire_glow, layer="above")

# Future: _tile_status_renderer.register_overlay("smoke", draw_smoke_overlay, layer="above")
