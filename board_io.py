from board import Loc, HorizontalSlider, VerticalSlider, BoardState, BOARD_SIZE
import numpy as np

def parse_from_text(text: str) -> BoardState:
    lines = [line for line in text.splitlines() if line.strip()]
    # Border is +------+ (length 8)
    # Content lines are |xxxxxx| or |xxxxxx  (length 8)
    grid_lines = lines[1:BOARD_SIZE + 1]
    
    char_to_locs = {}
    for y, line in enumerate(grid_lines):
        # Extract 6 characters after the first '|'
        content = line[1:BOARD_SIZE + 1]
        for x, char in enumerate(content):
            if char != ' ':
                if char not in char_to_locs:
                    char_to_locs[char] = []
                char_to_locs[char].append(Loc(y, x))
                
    horizontal_sliders = []
    vertical_sliders = []
    
    for char, locs in char_to_locs.items():
        min_y = min(l.y for l in locs)
        max_y = max(l.y for l in locs)
        min_x = min(l.x for l in locs)
        max_x = max(l.x for l in locs)
        
        is_horizontal = min_y == max_y
        is_vertical = min_x == max_x
        
        if is_horizontal:
            length = max_x - min_x + 1
            horizontal_sliders.append(HorizontalSlider(Loc(min_y, min_x), length, is_target=(char == '*'), char=char))
        elif is_vertical:
            length = max_y - min_y + 1
            vertical_sliders.append(VerticalSlider(Loc(min_y, min_x), length, char=char))
        else:
            # Handle potentially non-contiguous or complex shapes if they existed, 
            # but in Unblock Me they are always 1xN or Nx1.
            raise ValueError(f"Slider {char} is neither horizontal nor vertical at {locs}")
            
    return BoardState(horizontal_sliders, vertical_sliders)

def save_as_text(state: BoardState) -> str:
    grid = np.full((BOARD_SIZE, BOARD_SIZE), ' ')
    
    for s in state.horizontal_sliders:
        for cell in s.get_cells():
            grid[cell.y, cell.x] = s.char
            
    for s in state.vertical_sliders:
        for cell in s.get_cells():
            grid[cell.y, cell.x] = s.char
            
    res = ["+------+"]
    for y, row in enumerate(grid):
        row_str = "".join(row)
        if y == 2: # Exit row
            # Row 2 typically has no trailing '|' if it's the exit
            res.append("|" + row_str)
        else:
            res.append("|" + row_str + "|")
    res.append("+------+")
    
    return "\n".join(res)
