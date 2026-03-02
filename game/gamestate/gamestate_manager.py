# file: gamestate/gamestate_manager.py

from ai.ai_manager import handle_entity_turn
from utils.enums import TurnPhase
from utils import globals as G
from events.broadcaster import broadcast
from utils.logger import log_info, log_warn


class GameStateManager:
    def __init__(self, players, enemies, map_ref):
        self.players = players
        self.enemies = enemies
        self.map_ref = map_ref

        self.turn_order = players[:]
        self.ended_turns = set()
        self.round = 1
        self.TurnPhase = TurnPhase.PLAYER_TURN
        self.current_player_index = 0
        self.ui_mode = None

        self.message_manager = None  # Set externally
        self._event_listeners = {}  # Event system: {event_type: [callbacks]}

        self.begin_round()

    # --- Event System ---

    def register_listener(self, event_type, callback):
        if event_type not in self._event_listeners:
            self._event_listeners[event_type] = []
        self._event_listeners[event_type].append(callback)

    def dispatch_event(self, event_type, data=None):
        for callback in self._event_listeners.get(event_type, []):
            callback(data)

    # --- Turn & Round Logic ---

    def begin_round(self):
        self.TurnPhase = TurnPhase.PLAYER_TURN
        self.ended_turns.clear()
        self.current_player_index = 0
        log_info("GameState", f"--- Round {self.round} begins ---", file=__file__)

        for entity in self.players + self.enemies:
            if hasattr(entity, "effects"):
                entity.effects.tick_round_effects()

        if self.round == 1:
            self.apply_global_effect("adrenaline")

        G.tile_status_manager.tick_round()

        if self.message_manager:
            self.message_manager.show_floating(f"Round {self.round} Started")

        self.dispatch_event("round_started", self.round)
        self.start_player_turn(self.get_active_player())

    def advance_round(self):
        self.round += 1
        self.turn_order = self.turn_order[1:] + self.turn_order[:1]  # Rotate clockwise
        self.begin_round()

    def get_active_player(self):
        return self.turn_order[self.current_player_index]

    def start_player_turn(self, player):
        player_display = player.character_display_name
        log_info("GameState", f"{player_display}'s turn begins.", file=__file__)
        player = self.get_active_player()
        if self.message_manager:
            self.message_manager.show_floating(f"{player_display}'s turn!")
        broadcast("turn_started", {
            "event": "turn_started",
            "entity": player,
            "tile": player.tile
        })
        player.move_points_modified = player.move_points_modified
        player.move_points_current = player.move_points_modified

        self.dispatch_event("player_turn_started", player)

    def end_player_turn(self, player):
        self.ended_turns.add(player)
        broadcast("turn_ended", {
            "event": "turn_ended",
            "entity": player,
            "tile": player.tile
        })

        if len(self.ended_turns) >= len(self.turn_order):
            if self.message_manager:
                self.message_manager.show_floating("Round ended")
            self.TurnPhase = TurnPhase.ENEMY_TURN
            self.dispatch_event("player_TurnPhase_ended")
            self.process_enemy_turns()
        else:
            self.current_player_index = (self.current_player_index + 1) % len(self.turn_order)
            next_player = self.get_active_player()
            self.start_player_turn(next_player)

    def process_enemy_turns(self):
        log_info("GameState", "Enemies take their turns...", file=__file__)
        for enemy in self.enemies:
            handle_entity_turn(enemy, self.map_ref, self.players)
        self.dispatch_event("enemy_TurnPhase_ended")
        self.complete_round()

    def complete_round(self):
        self.TurnPhase = TurnPhase.ROUND_END
        self.advance_round()

    def get_visible_tiles(self):
        return [p.tile for p in self.players if p.tile is not None]

    def is_player_turn(self, player):
        return self.TurnPhase == TurnPhase.PLAYER_TURN and player not in self.ended_turns

    def get_round_display_text(self):
        return f"Round {self.round}"

    def apply_global_effect(self, effect_id):
        effect = G.effect_catalog.get(effect_id)
        if not effect:
            log_warn("GameState", f"No such effect: {effect_id}", file=__file__)
            return

        for entity in self.players + self.enemies:
            if hasattr(entity, "effects"):
                entity.effects.add_effect(effect)

    def __setattr__(self, name, value):
        if getattr(G, "DEBUG_ATTR_WARNINGS", False) and not hasattr(self, name):
            log_warn("GameState", f"{self.__class__.__name__} has no attribute '{name}'", file=__file__)
        super().__setattr__(name, value)
