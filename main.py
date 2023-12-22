
import os
import math
import pygame

# Program settings (feel free to customize)
WIDTH = 640
HEIGHT = 640
TILE_PX = 64
FPS = 60

# Colors
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)

pygame.init()
pygame.display.set_caption("RP map editor")
window = pygame.display.set_mode((WIDTH, HEIGHT))
# Amount of tiles along horizontal and vertical axis
tile_count = (WIDTH // TILE_PX) if (WIDTH < HEIGHT) else (HEIGHT // TILE_PX)
# Duration of a frame in miliseconds
frame_duration = 1000 // FPS

def screen_to_tile(x, y, global_=True) -> tuple:
    """ Converts screen coordinates to tile's coordinates """
    cx = x % TILE_PX / TILE_PX
    cy = 1.0 - (y % TILE_PX / TILE_PX)
    if global_:
        cx += x // TILE_PX
        cy += (tile_count - 1) - y // TILE_PX
    return (cx, cy)

def tile_to_screen(x, y) -> tuple:
    return (
        x * TILE_PX,
        (tile_count - 1 - y) * TILE_PX
    )

drawn_lines = []   # Each element defines a line by two points (x1, y1) and (x2, y2)
colored_rects = [] # Positions of colored rectangles
mouse_pos = None   # Current mouse position
start_pos = None   # Position set once when LMB is pressed
is_lmb_held = False
run = True
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
                is_lmb_held = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.dict['button'] == 1:
                is_lmb_held = False
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.dict['pos']

    window.fill(BLACK)

    # Draw reference grid
    for y in range(tile_count):
        for x in range(tile_count):
            pygame.draw.rect(
                surface = window,
                color   = GRAY,
                rect    = pygame.Rect(x * TILE_PX, y * TILE_PX, TILE_PX, TILE_PX),
                width   = 1
            )
    # Draw colored rectangles
    for cr in colored_rects:
        pygame.draw.rect(
            surface = window,
            color   = GRAY,
            rect    = pygame.Rect(cr[0], cr[1], TILE_PX, TILE_PX)
        )
    # Draw already drawn lines
    for line in drawn_lines:
        pygame.draw.line(
            surface   = window,
            color     = WHITE,
            start_pos = (line[0], line[1]),
            end_pos   = (line[2], line[3])
        )
    # Provide line-drawing feature
    if is_lmb_held and mouse_pos is not None:
        if start_pos is None:
            start_pos = mouse_pos
        #print(screen_to_tile(*mouse_pos, False))
        pygame.draw.line(
            surface   = window,
            color     = WHITE,
            start_pos = start_pos,
            end_pos   = mouse_pos
        )
    # Save the drawn line
    elif start_pos is not None:
        colored_rects.clear()
        drawn_lines.clear()
        drawn_lines.append((*start_pos, *mouse_pos))
        # Perform DDA to find hit points
        hits = []
        # Global and local position of the starting and ending tile
        globalStartX, globalStartY = screen_to_tile(*start_pos, True)
        localStartX, localStartY = screen_to_tile(*start_pos, False)
        globalEndX, globalEndY = screen_to_tile(*mouse_pos, True)
        # Coordinates of a direction vector, it gets normalized
        dirX = mouse_pos[0] - start_pos[0]
        dirY = -1 * (mouse_pos[1] - start_pos[1])
        dirLength = math.sqrt(dirX ** 2 + dirY ** 2)
        dirLength = (1e30) if (dirLength == 0) else dirLength
        dirX /= dirLength
        dirY /= dirLength
        # Distances needed to walk along line in order to move by one in X or Y axis
        deltaDistX = (1e30) if (dirX == 0) else (1.0 / abs(dirX))
        deltaDistY = (1e30) if (dirY == 0) else (1.0 / abs(dirY))
        # Stepping direction indicators
        stepX = (-1) if (dirX < 0) else (1)
        stepY = (-1) if (dirY < 0) else (1)
        # Initial distances, move by them to enter DDA stepping cycle
        initialDistX = (1.0 - localStartX) if (stepX == 1) else localStartX
        initialDistY = (1.0 - localStartY) if (stepY == 1) else localStartY
        # Total distance made by moving in both axes by one reapetedly, now only initial
        totalDistX = initialDistX * deltaDistX
        totalDistY = initialDistY * deltaDistY
        # Tile position on the map (dynamic)
        tilePosX = math.floor(globalStartX)
        tilePosY = math.floor(globalStartY)
        # Stop tile position (tile in which end of the line sits)
        stopTileX = math.floor(globalEndX)
        stopTileY = math.floor(globalEndY)
        # Position of the hit (dynamic)
        hitX = None
        hitY = None
        
        # Perform DDA stepping
        os.system("clear")
        for i in range(128):
            colored_rects.append(tile_to_screen(tilePosX, tilePosY))
            # If stop tile is reached exit the loop
            if tilePosX == stopTileX and tilePosY == stopTileY:
                break
            # Otherwise step appropriately
            if totalDistX < totalDistY:
                hitX = globalStartX + dirX * totalDistX
                hitY = globalStartY + dirY * totalDistX
                totalDistX += deltaDistX
                tilePosX += stepX
            else:
                hitX = globalStartX + dirX * totalDistY
                hitY = globalStartY + dirY * totalDistY
                totalDistY += deltaDistY
                tilePosY += stepY
            # Process the hit point
            print(hitX, hitY)

        start_pos = None

    pygame.display.flip()
    pygame.time.wait(frame_duration)

pygame.quit()
