import os
import sys
import pygame
from PIL import Image
from board_io import parse_from_text
from solver import solve
from parsing_util import normalize_level_path
import visualizer as vis
from board import Loc, HorizontalSlider, VerticalSlider, BoardState

# Offscreen rendering
os.environ['SDL_VIDEODRIVER'] = 'dummy'

FPS = 24
POST_MOVE_DELAY = 0.3
WAIT_FRAMES = int(POST_MOVE_DELAY * FPS)

def surface_to_pil(surface):
    raw_str = pygame.image.tostring(surface, "RGB")
    return Image.frombytes("RGB", surface.get_size(), raw_str)

def export_webp(level_id):
    pygame.init()
    
    file_path = normalize_level_path(level_id)
    if not os.path.exists(file_path):
        print(f"Error: Level {level_id} not found.")
        return

    try:
        with open(file_path, 'r') as f:
            content = f.read()
        initial_state = parse_from_text(content)
    except Exception as e:
        print(f"Error loading {level_id}: {e}")
        return

    print(f"Solving {level_id}...")
    solution, visited, duration = solve(initial_state)
    
    if solution is None:
        print("No solution found.")
        return

    # Extract level name for UI
    parts = file_path.split(os.sep)
    if len(parts) >= 2:
        level_name = os.path.join(parts[-2], os.path.basename(parts[-1])).replace(".txt", "")
    else:
        level_name = os.path.basename(file_path).replace(".txt", "")

    print(f"Solution found in {len(solution)} moves. Generating frames...")

    # Merge moves for visualization (consistent with visualizer.py)
    merged_solution = []
    for move in solution:
        if merged_solution and merged_solution[-1]["char"] == move["char"]:
            merged_solution[-1]["to"] = move["to"]
        else:
            merged_solution.append(move.copy())
    
    for move in merged_solution:
        dist = abs(move["to"][0] - move["from"][0]) + abs(move["to"][1] - move["from"][1])
        move["duration"] = max(0.05, dist * vis.SECONDS_PER_TILE)

    surface = pygame.Surface((vis.SCREEN_WIDTH, vis.SCREEN_HEIGHT))
    
    # Pre-init fonts (headless)
    fonts = {
        'main': pygame.font.SysFont(None, 28),
        'title': pygame.font.SysFont(None, 36, bold=True),
        'ctrl': pygame.font.SysFont(None, 22)
    }

    frames = []
    curr_state = initial_state
    
    def render_frame(state, move_info, alpha, step_idx):
        status = f"Move {step_idx}/{len(merged_solution)}"
        if state.is_success(): status += " - SOLVED!"
        vis.draw_board_base(surface)
        vis.draw_sliders(surface, state, moving_info=move_info, alpha=alpha)
        vis.draw_ui(surface, status, level_name, False, fonts)
        frames.append(surface_to_pil(surface))

    # 1. Initial pause
    for _ in range(FPS):
        render_frame(curr_state, None, 0.0, 0)

    for move_idx, move in enumerate(merged_solution):
        slide_frames = int(move["duration"] * FPS)
        
        # 2. Animation frames
        for i in range(slide_frames):
            alpha = i / float(slide_frames)
            render_frame(curr_state, move, alpha, move_idx)
        
        # Update state to the result of this merged move
        new_h = list(curr_state.horizontal_sliders)
        new_v = list(curr_state.vertical_sliders)
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
        curr_state = BoardState(new_h, new_v)
        
        # 3. Wait frames (post-move delay)
        for _ in range(WAIT_FRAMES):
            render_frame(curr_state, None, 0.0, move_idx + 1)
        
        print(f"  Processed move {move_idx + 1}/{len(merged_solution)}")

    # 4. Final pause
    for _ in range(FPS * 2):
        render_frame(curr_state, None, 0.0, len(merged_solution))

    # Save
    solutions_dir = "solutions"
    os.makedirs(solutions_dir, exist_ok=True)
    
    # Save in nested folders to match levels/
    out_path = os.path.join(solutions_dir, f"{level_name}.webp")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        quality=80,
        method=6
    )
    
    print(f"Exported to {out_path}")
    pygame.quit()

if __name__ == "__main__":
    level_id = sys.argv[1] if len(sys.argv) > 1 else "starter/1"
    export_webp(level_id)
