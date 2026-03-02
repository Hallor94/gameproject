import pygame

def draw_bar(surface, rect, value, max_value, *, color=(255, 0, 0), bg_color=(40, 40, 40), 
              chunk_margin=1, show_label=True, font=None, label_color=(255, 255, 255)):
    """
    Draw a segmented bar (e.g. for HP/MOV).
    
    :param surface: Pygame surface to draw on
    :param rect: (x, y, w, h) tuple or pygame.Rect
    :param value: current value
    :param max_value: max value (number of segments)
    :param color: fill color
    :param bg_color: background bar color
    :param chunk_margin: gap between segments
    :param show_label: if True, draw value label centered
    :param font: optional pygame font
    :param label_color: color of the value label
    """
    if isinstance(rect, tuple):
        rect = pygame.Rect(rect)

    # Segment size
    total_width = rect.width
    chunk_count = max(max_value, 1)
    chunk_width = (total_width - chunk_margin * (chunk_count - 1)) // chunk_count
    chunk_height = rect.height

    for i in range(value):
        # First chunk: take the extra width
        if i == len(range(value)):
            cw = rect.width - (chunk_width + chunk_margin) * (value - 1)
            cx = rect.x
        else:
            cw = chunk_width
            cx = rect.x + (chunk_width + chunk_margin) * i

        chunk_rect = pygame.Rect(cx, rect.y, cw, chunk_height)
        pygame.draw.rect(surface, color, chunk_rect, border_radius=4)
        pygame.draw.rect(surface, (0, 0, 0), chunk_rect, width=1, border_radius=4)


    # Optional label
    if show_label:
        label = f"{value}/{max_value}"
        
        # Render black outline
        outline_color = (0, 0, 0)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            outline_surf = font.render(label, True, outline_color)
            outline_rect = outline_surf.get_rect(center=(rect.centerx + dx, rect.centery + dy))
            surface.blit(outline_surf, outline_rect)

        # Render main label
        text_surf = font.render(label, True, label_color)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

