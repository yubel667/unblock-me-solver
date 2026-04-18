import pygame
import time
from typing import List, Dict, Optional
from board import BoardState, Loc, HorizontalSlider, VerticalSlider, BOARD_SIZE

# Colors
BOARD_COLOR = (101, 67, 33)    # Dark Brown
SLIDER_COLOR = (186, 140, 99)  # Authentic Wood (Light Brown/Oak)
TARGET_COLOR = (200, 0, 0)     # Red
GRID_COLOR = (70, 45, 20)      # Darker Brown
TEXT_COLOR = (240, 240, 240)

TILE_SIZE = 80
MARGIN = 60
SCREEN_WIDTH = BOARD_SIZE * TILE_SIZE + MARGIN * 2
SCREEN_HEIGHT = BOARD_SIZE * TILE_SIZE + MARGIN * 2 + 100

SECONDS_PER_TILE = 0.15 # Constant speed: 0.15s per tile moved

def get_tile_rect(y, x):
    return MARGIN + x * TILE_SIZE, MARGIN + y * TILE_SIZE, TILE_SIZE, TILE_SIZE

def draw_board_base(screen):
    # Fill background
    screen.fill((40, 40, 40))
    # Draw Board background
    pygame.draw.rect(screen, BOARD_COLOR, (MARGIN, MARGIN, BOARD_SIZE * TILE_SIZE, BOARD_SIZE * TILE_SIZE))
    
    # Draw Exit gap
    exit_y = MARGIN + 2 * TILE_SIZE
    exit_x = MARGIN + BOARD_SIZE * TILE_SIZE
    pygame.draw.rect(screen, (0, 0, 0), (exit_x - 5, exit_y + 10, 10, TILE_SIZE - 20))

    # Draw Grid lines
    for i in range(BOARD_SIZE + 1):
        pygame.draw.line(screen, GRID_COLOR, (MARGIN, MARGIN + i * TILE_SIZE), (MARGIN + BOARD_SIZE * TILE_SIZE, MARGIN + i * TILE_SIZE), 1)
        pygame.draw.line(screen, GRID_COLOR, (MARGIN + i * TILE_SIZE, MARGIN), (MARGIN + i * TILE_SIZE, MARGIN + BOARD_SIZE * TILE_SIZE), 1)

def draw_sliders(screen, state: BoardState, moving_info=None, alpha=0.0):
    moving_char = moving_info["char"] if moving_info else None
    
    # Draw Horizontal Sliders
    for s in state.horizontal_sliders:
        color = TARGET_COLOR if s.is_target else SLIDER_COLOR
        fy, fx = s.pos.y, s.pos.x
        
        if moving_char == s.char:
            # Interpolate
            moving_to = moving_info["to"]
            curr_y = fy + (moving_to[0] - fy) * alpha
            curr_x = fx + (moving_to[1] - fx) * alpha
        else:
            curr_y, curr_x = fy, fx
            
        px = MARGIN + curr_x * TILE_SIZE + 4
        py = MARGIN + curr_y * TILE_SIZE + 4
        width = TILE_SIZE * s.length - 8
        height = TILE_SIZE - 8
        pygame.draw.rect(screen, color, (px, py, width, height), 0, 8)
        pygame.draw.rect(screen, (0,0,0), (px, py, width, height), 2, 8)

    # Draw Vertical Sliders
    for s in state.vertical_sliders:
        color = SLIDER_COLOR
        fy, fx = s.pos.y, s.pos.x
        
        if moving_char == s.char:
            # Interpolate
            moving_to = moving_info["to"]
            curr_y = fy + (moving_to[0] - fy) * alpha
            curr_x = fx + (moving_to[1] - fx) * alpha
        else:
            curr_y, curr_x = fy, fx
            
        px = MARGIN + curr_x * TILE_SIZE + 4
        py = MARGIN + curr_y * TILE_SIZE + 4
        width = TILE_SIZE - 8
        height = TILE_SIZE * s.length - 8
        pygame.draw.rect(screen, color, (px, py, width, height), 0, 8)
        pygame.draw.rect(screen, (0,0,0), (px, py, width, height), 2, 8)

def draw_ui(screen, status_text, level_id, show_controls, fonts):
    # Status
    if status_text:
        img = fonts['main'].render(status_text, True, TEXT_COLOR)
        screen.blit(img, (MARGIN, MARGIN + BOARD_SIZE * TILE_SIZE + 10))
    
    # Level ID
    if level_id:
        img = fonts['title'].render(f"Unblock Me: {level_id}", True, TEXT_COLOR)
        screen.blit(img, (MARGIN, 15))

    if show_controls:
        controls = [
            "ENTER: Toggle Auto-play",
            "SPACE: Animate Next Step",
            "RIGHT/LEFT: Jump Next/Prev",
            "R: Reset",
            "ESC: Quit"
        ]
        for i, line in enumerate(controls):
            img = fonts['ctrl'].render(line, True, (160, 160, 160))
            screen.blit(img, (MARGIN + 250, MARGIN + BOARD_SIZE * TILE_SIZE + 10 + i * 20))

def run_visualizer(initial_state: BoardState, solution: Optional[List[Dict]], autoplay=False, show_controls=True, level_id=None):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("Unblock Me Solver")
    
    fonts = {
        'main': pygame.font.SysFont(None, 28),
        'title': pygame.font.SysFont(None, 36, bold=True),
        'ctrl': pygame.font.SysFont(None, 22)
    }

    # Merge consecutive moves and calculate duration based on distance
    merged_solution = []
    if solution:
        for move in solution:
            if merged_solution and merged_solution[-1]["char"] == move["char"]:
                merged_solution[-1]["to"] = move["to"]
            else:
                merged_solution.append(move.copy())
        
        # Calculate duration for each merged move
        for move in merged_solution:
            # Manhattan distance (sliders move linearly)
            dist = abs(move["to"][0] - move["from"][0]) + abs(move["to"][1] - move["from"][1])
            move["duration"] = max(0.05, dist * SECONDS_PER_TILE)
    
    # Prepare steps
    states = [initial_state]
    if merged_solution:
        curr = initial_state
        for move in merged_solution:
            new_h = list(curr.horizontal_sliders)
            new_v = list(curr.vertical_sliders)
            
            moved = False
            for i, s in enumerate(new_h):
                if s.char == move["char"]:
                    new_h[i] = HorizontalSlider(Loc(move["to"][0], move["to"][1]), s.length, s.is_target, s.char)
                    moved = True
                    break
            if not moved:
                for i, s in enumerate(new_v):
                    if s.char == move["char"]:
                        new_v[i] = VerticalSlider(Loc(move["to"][0], move["to"][1]), s.length, s.char)
                        moved = True
                        break
            
            if moved:
                curr = BoardState(new_h, new_v)
                states.append(curr)
            else:
                break

    running = True
    step_idx = 0
    paused = not autoplay
    single_step = False
    anim_start_time = time.time()
    clock = pygame.time.Clock()
    
    POST_MOVE_DELAY = 0.3

    while running:
        is_final = (step_idx >= len(states) - 1)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN: # Toggle Autoplay
                    if is_final:
                        running = False
                    else:
                        paused = not paused
                        single_step = False
                        anim_start_time = time.time()
                elif event.key == pygame.K_SPACE: # Play next move with animation
                    if is_final:
                        running = False
                    elif paused:
                        paused = False
                        single_step = True
                        anim_start_time = time.time()
                elif event.key == pygame.K_RIGHT:
                    if step_idx < len(states) - 1:
                        step_idx += 1
                    paused = True
                    single_step = False
                elif event.key == pygame.K_LEFT:
                    if step_idx > 0:
                        step_idx -= 1
                    paused = True
                    single_step = False
                elif event.key == pygame.K_r:
                    step_idx = 0
                    paused = True
                    single_step = False

        alpha = 0.0
        curr_state = states[step_idx]
        move_info = None
        
        if not paused and not is_final:
            move_info = merged_solution[step_idx]
            duration = move_info["duration"]
            elapsed = time.time() - anim_start_time
            
            if elapsed >= duration + POST_MOVE_DELAY:
                step_idx += 1
                anim_start_time = time.time()
                if single_step:
                    paused = True
                    single_step = False
                is_final = (step_idx >= len(states) - 1)
                curr_state = states[step_idx]
                move_info = None
            elif elapsed >= duration:
                # Finished animation, in delay period
                curr_state = states[step_idx + 1]
                move_info = None
            else:
                # In animation period
                alpha = min(1.0, elapsed / duration)

        # Draw
        draw_board_base(screen)
        draw_sliders(screen, curr_state, move_info, alpha)
        
        status = f"Step {step_idx}/{len(states)-1}"
        if states[step_idx].is_success():
            status += " - SOLVED!"
        elif paused:
            status += " (PAUSED)"
            
        draw_ui(screen, status, level_id, show_controls, fonts)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
