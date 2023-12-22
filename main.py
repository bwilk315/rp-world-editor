
import pygame

# Program settings (feel free to customize)
WIDTH = 640
HEIGHT = 640
TILE_PX = 64
FPS = 30

pygame.init()
pygame.display.set_caption("RP map editor")
window = pygame.display.set_mode((WIDTH, HEIGHT))
tile_count = WIDTH // TILE_PX if WIDTH < HEIGHT else HEIGHT // TILE_PX
frame_duration = 1000 // FPS
run = True
white = (255, 255, 255)
gray = (128, 128, 128)
black = (0, 0, 0)

# 2D array of elements containing arrPos, tileId, [list of lines identified by lineIds]
tile_data = []
drawn_lines = []
# Event handling variables
mouse_pos = None
drag_start = None
is_drag = False
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYUP:
            if event.dict['unicode'] == 'w':
                # Clear the plane file
                with open('generated.plane', 'w+') as file:
                    file.write('')
                # Write my world data
                with open('generated.plane', 'a') as file:
                    # Dimensions
                    file.write(f'{tile_count} {tile_count} ;')
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.dict['button'] == 1:
                is_drag = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.dict['button'] == 1:
                is_drag = False
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.dict['pos']

    window.fill((0, 0, 0, 0))

    # Draw reference grid
    for y in range(tile_count):
        for x in range(tile_count):
            border = 1
            pygame.draw.rect(
                window,
                gray,
                pygame.Rect(x * TILE_PX, y * TILE_PX, TILE_PX, TILE_PX),
            )
            pygame.draw.rect(
                window,
                black,
                pygame.Rect(x * TILE_PX + border, y * TILE_PX + border, TILE_PX - border * 2, TILE_PX - border * 2),
            )
    # Draw already drawn lines
    for line in drawn_lines:
        pygame.draw.line(
            window,
            white,
            (*line[:2],),
            (*line[2:4],)
        )
    # Handle line-drawing feature
    if is_drag and mouse_pos is not None:
        if drag_start is None:
            drag_start = mouse_pos
        pygame.draw.line(
            window,
            white,
            drag_start,
            mouse_pos
        )
    elif drag_start is not None:
        drawn_lines.append((*drag_start, *mouse_pos))
        # What are tiles through which line goes through?
        # what are line equations for each of them that would line up into a big one?
        sx, sy = drag_start # Start x,y
        ex, ey = mouse_pos # End x,y

        drag_start = None

    pygame.display.flip()
    pygame.time.delay(frame_duration)

pygame.quit()
