
import pygame
from setup.character_selection import load_characters

DEFAULT_PLAYERS = [
    {"name": "Alexander", "character": None},
    {"name": "Viktor", "character": None},
    {"name": "Tim", "character": None},
]

class SetupMenu:
    def __init__(self):
        screen = pygame.display.get_surface()
        self.screen = screen
        width = screen.get_width()
        height = screen.get_height()
        self.players = DEFAULT_PLAYERS.copy()
        self.available_characters = load_characters()
        self.selected_character_index = [0 for _ in self.players]
        self.selected_player_index = 0
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 48)
        self.name_edit_mode = True  # toggles name editing
        self.temp_name_buffer = self.players[self.selected_player_index]["name"]

        if self.available_characters:
            self.selected_character_index = [
                i % len(self.available_characters) for i in range(len(self.players))
            ]
        else:
            self.selected_character_index = [0 for _ in self.players]  # default to 0s

        
        self.done = False

    def is_done(self):
        return self.done

    def get_player_data(self):
        return self.players
    def handle_input(self, event):
            if event.type == pygame.KEYDOWN:
                if self.name_edit_mode:
                    if event.key == pygame.K_RETURN:
                        self.players[self.selected_player_index]["name"] = self.temp_name_buffer
                        self.name_edit_mode = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.temp_name_buffer = self.temp_name_buffer[:-1]
                    elif event.key == pygame.K_TAB:
                        self.players[self.selected_player_index]["name"] = self.temp_name_buffer
                        self.selected_player_index = (self.selected_player_index + 1) % len(self.players)
                        self.temp_name_buffer = self.players[self.selected_player_index]["name"]
                    elif event.unicode.isprintable():
                        self.temp_name_buffer += event.unicode
                else:
                    if event.key == pygame.K_LEFT:
                        self.selected_character_index[self.selected_player_index] -= 1
                        self.selected_character_index[self.selected_player_index] %= len(self.available_characters)
                    elif event.key == pygame.K_RIGHT:
                        self.selected_character_index[self.selected_player_index] += 1
                        self.selected_character_index[self.selected_player_index] %= len(self.available_characters)
                    elif event.key == pygame.K_TAB:
                        self.selected_player_index = (self.selected_player_index + 1) % len(self.players)
                    elif event.key == pygame.K_RETURN:
                        self.assign_selected_characters()
                        self.done = True
                    elif event.key == pygame.K_n:
                        self.name_edit_mode = True
                        self.temp_name_buffer = self.players[self.selected_player_index]["name"]

    def draw(self):
        self.screen.fill((30, 30, 30))
        title = self.title_font.render("Setup Menu", True, (255, 255, 255))
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 20))

        y_offset = 100
        for i, player in enumerate(self.players):
            color = (255, 255, 255) if i != self.selected_player_index else (100, 255, 100)

            name_display = self.temp_name_buffer if i == self.selected_player_index and self.name_edit_mode else player["name"]
            label = self.font.render(f"Player {i + 1}: {name_display}", True, color)
            self.screen.blit(label, (50, y_offset))

            char = self.available_characters[self.selected_character_index[i]]
            char_label = self.font.render(f"Character: {char['name']}", True, (200, 200, 100))
            self.screen.blit(char_label, (300, y_offset))

            y_offset += 60

        instructions = self.font.render("TAB to switch | ←/→ to change char | N to edit name | ENTER to start", True, (180, 180, 180))
        self.screen.blit(instructions, (50, self.screen.get_height() - 40))

        pygame.display.flip()

    def assign_default_characters(self):
        if not self.available_characters:
            print("Warning: No characters available. Skipping default assignment.")
            return

        for i, index in enumerate(self.selected_character_index):
            self.players[i]["character"] = self.available_characters[index]
    def assign_selected_characters(self):
        for i, index in enumerate(self.selected_character_index):
            self.players[i]["character"] = self.available_characters[index]
