import pygame
import sys
import os
import time
from typing import List, Optional, Tuple
from board import Loc, HorizontalSlider, VerticalSlider, BoardState, BOARD_SIZE
import board_io
import visualizer as vis
from parsing_util import normalize_level_path

# UI Constants
WINDOW_WIDTH = vis.SCREEN_WIDTH
WINDOW_HEIGHT = vis.SCREEN_HEIGHT

class LevelEditor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.sliders = []
        self.target_char = '0'
        
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    content = f.read()
                state = board_io.parse_from_text(content)
                self.sliders = list(state.horizontal_sliders) + list(state.vertical_sliders)
            except Exception as e:
                print(f"Error loading level: {e}")

        self.drag_start = None # (y, x)
        self.drag_current = None # (y, x)

    def get_occupied_cells(self):
        occupied = {}
        for s in self.sliders:
            for cell in s.get_cells():
                occupied[(cell.y, cell.x)] = s
        return occupied

    def get_next_char(self):
        chars = set(s.char for s in self.sliders)
        if self.target_char not in chars:
            return self.target_char
        
        for c in "123456789abcdefghijklmnopqrstuvwxyz":
            if c not in chars:
                return c
        return "?"

    def check_valid(self):
        occupied = {}
        target_count = 0
        target_slider = None
        
        for s in self.sliders:
            is_target = isinstance(s, HorizontalSlider) and s.is_target
            if is_target:
                target_count += 1
                target_slider = s
            
            for cell in s.get_cells():
                if not (0 <= cell.y < BOARD_SIZE and 0 <= cell.x < BOARD_SIZE):
                    return False, f"Slider {s.char} out of bounds"
                if (cell.y, cell.x) in occupied:
                    return False, f"Collision at ({cell.y}, {cell.x})"
                occupied[(cell.y, cell.x)] = s.char

        if target_count != 1:
            return False, "Must have exactly one target slider (0)"
        
        if not isinstance(target_slider, HorizontalSlider):
            return False, "Target slider must be horizontal"
        
        if target_slider.pos.y != 2:
            return False, "Target slider must be on row 2 (exit row)"

        return True, "Ready to save (S)"

    def save(self):
        valid, msg = self.check_valid()
        if not valid:
            return False, f"Cannot Save: {msg}"
        
        h_sliders = [s for s in self.sliders if isinstance(s, HorizontalSlider)]
        v_sliders = [s for s in self.sliders if isinstance(s, VerticalSlider)]
        
        state = BoardState(h_sliders, v_sliders)
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w') as f:
            f.write(board_io.save_as_text(state))
        return True, "Level saved!"

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(f"Unblock Me Editor - {os.path.basename(self.file_path)}")
        clock = pygame.time.Clock()
        
        fonts = {
            'main': pygame.font.SysFont(None, 28),
            'title': pygame.font.SysFont(None, 36, bold=True),
            'ctrl': pygame.font.SysFont(None, 22)
        }
        
        status_msg = ""
        status_color = (255, 255, 255)
        
        while True:
            mouse_pos = pygame.mouse.get_pos()
            # Convert mouse to grid
            gx = (mouse_pos[0] - vis.MARGIN) // vis.TILE_SIZE
            gy = (mouse_pos[1] - vis.MARGIN) // vis.TILE_SIZE
            in_grid = 0 <= gx < BOARD_SIZE and 0 <= gy < BOARD_SIZE

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        if in_grid:
                            self.drag_start = (gy, gx)
                            self.drag_current = (gy, gx)
                    elif event.button == 3: # Right click to remove
                        if in_grid:
                            occupied = self.get_occupied_cells()
                            if (gy, gx) in occupied:
                                slider_to_remove = occupied[(gy, gx)]
                                self.sliders = [s for s in self.sliders if s.char != slider_to_remove.char]

                elif event.type == pygame.MOUSEMOTION:
                    if self.drag_start:
                        self.drag_current = (gy, gx)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.drag_start:
                        y1, x1 = self.drag_start
                        y2, x2 = gy, gx
                        
                        # Minimum length 2
                        if y1 == y2 and abs(x2 - x1) >= 1: # Horizontal
                            start_x = min(x1, x2)
                            length = abs(x2 - x1) + 1
                            char = self.get_next_char()
                            if char != "?":
                                is_target = (char == self.target_char)
                                new_slider = HorizontalSlider(Loc(y1, start_x), length, is_target, char)
                                self.sliders.append(new_slider)
                        elif x1 == x2 and abs(y2 - y1) >= 1: # Vertical
                            start_y = min(y1, y2)
                            length = abs(y2 - y1) + 1
                            char = self.get_next_char()
                            if char != "?":
                                new_slider = VerticalSlider(Loc(start_y, x1), length, char)
                                self.sliders.append(new_slider)
                        
                        self.drag_start = None
                        self.drag_current = None

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        success, msg = self.save()
                        status_msg = msg
                        status_color = (0, 255, 0) if success else (255, 0, 0)
                        if success:
                            pygame.display.flip()
                            time.sleep(0.5)
                            pygame.quit()
                            return
                    elif event.key == pygame.K_x:
                        if in_grid:
                            occupied = self.get_occupied_cells()
                            if (gy, gx) in occupied:
                                slider_to_remove = occupied[(gy, gx)]
                                self.sliders = [s for s in self.sliders if s.char != slider_to_remove.char]
                    elif event.key == pygame.K_t:
                        if in_grid:
                            occupied = self.get_occupied_cells()
                            if (gy, gx) in occupied:
                                new_target = occupied[(gy, gx)]
                                # Swap target property
                                new_sliders = []
                                for s in self.sliders:
                                    if s.char == new_target.char:
                                        if isinstance(s, HorizontalSlider):
                                            # Make this one target
                                            new_sliders.append(HorizontalSlider(s.pos, s.length, True, s.char))
                                        else:
                                            # Vertical can't be target, but we keep it
                                            new_sliders.append(s)
                                    elif isinstance(s, HorizontalSlider) and s.is_target:
                                        # Make old target non-target
                                        new_sliders.append(HorizontalSlider(s.pos, s.length, False, s.char))
                                    else:
                                        new_sliders.append(s)
                                self.sliders = new_sliders
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return

            # Drawing
            vis.draw_board_base(screen)
            
            # Temporary state for visualization
            h_sliders = [s for s in self.sliders if isinstance(s, HorizontalSlider)]
            v_sliders = [s for s in self.sliders if isinstance(s, VerticalSlider)]
            vis.draw_sliders(screen, BoardState(h_sliders, v_sliders))

            # Draw drag preview
            if self.drag_start and self.drag_current:
                y1, x1 = self.drag_start
                y2, x2 = self.drag_current
                if y1 == y2 and x2 != x1: # Horizontal preview
                    px = vis.MARGIN + min(x1, x2) * vis.TILE_SIZE + 4
                    py = vis.MARGIN + y1 * vis.TILE_SIZE + 4
                    width = (abs(x2 - x1) + 1) * vis.TILE_SIZE - 8
                    height = vis.TILE_SIZE - 8
                    pygame.draw.rect(screen, (200, 200, 200), (px, py, width, height), 2, 8)
                elif x1 == x2 and y2 != y1: # Vertical preview
                    px = vis.MARGIN + x1 * vis.TILE_SIZE + 4
                    py = vis.MARGIN + min(y1, y2) * vis.TILE_SIZE + 4
                    width = vis.TILE_SIZE - 8
                    height = (abs(y2 - y1) + 1) * vis.TILE_SIZE - 8
                    pygame.draw.rect(screen, (200, 200, 200), (px, py, width, height), 2, 8)

            # UI Text
            valid, msg = self.check_valid()
            display_msg = status_msg if status_msg else msg
            color = status_color if status_msg else ((0, 255, 0) if valid else (200, 200, 200))
            
            # Draw UI without visualizer's default controls to save space
            vis.draw_ui(screen, display_msg, os.path.basename(self.file_path), False, fonts)
            
            # Dedicated Instructions area for Editor
            inst_font = fonts['ctrl']
            instructions = [
                "Drag: Create Slider",
                "X / Right-Click: Remove",
                "T: Set Target",
                "S: Save & Exit",
                "ESC: Quit"
            ]
            for i, line in enumerate(instructions):
                img = inst_font.render(line, True, (160, 160, 160))
                # Adjust x to start earlier and prevent overflow
                screen.blit(img, (vis.MARGIN + 280, vis.MARGIN + BOARD_SIZE * vis.TILE_SIZE + 10 + i * 18))

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    level_id = sys.argv[1] if len(sys.argv) > 1 else "starter/new"
    file_path = normalize_level_path(level_id)
    LevelEditor(file_path).run()
