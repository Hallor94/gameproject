# file: font_testscreen.py

import pygame
from config import constants as C
from utils import globals as G

# === Sample text for demo ===
LOREM = "The quick brown fox jumps over the lazy dog."

# === Font labels and font references from globals ===
FONT_ENTRIES = [
    ("Default Font", lambda: G.font),
    ("Title Font", lambda: G.title_font),
    ("Menu Font", lambda: G.menu_font),
    ("Stats Font", lambda: G.stat_font),
    ("Flavor Font", lambda: G.flavor_font),
    ("Dialogue Font", lambda: G.dialogue_font),
    ("Speech Font", lambda: G.speech_font),
    ("Floating Font", lambda: G.floating_font),
]

def main():
    pygame.init()
    screen = pygame.display.set_mode(C.BASE_RESOLUTION)
    pygame.display.set_caption("Font Preview")
    G.init(screen)

    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill((25, 25, 25))

        y = 30
        for label, font_func in FONT_ENTRIES:
            font = font_func()
            if font:
                label_surf = G.get_font(22, bold=True).render(label, True, (255, 255, 100))
                text_surf = font.render(LOREM, True, (255, 255, 255))

                screen.blit(label_surf, (50, y))
                y += label_surf.get_height() + 4
                screen.blit(text_surf, (70, y))
                y += text_surf.get_height() + 20

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(C.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
