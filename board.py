import enum
from typing import List, Optional, Set, Tuple
from dataclasses import dataclass

@dataclass(frozen=True)
class Loc:
    y: int
    x: int

class Direction(enum.Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

@dataclass(frozen=True)
class HorizontalSlider:
    pos: Loc
    length: int
    is_target: bool = False
    char: str = "0"

    def get_identifier(self):
        return f"H{self.pos.y}{self.pos.x}{self.length}{'T' if self.is_target else ''}"

    def get_cells(self) -> List[Loc]:
        return [Loc(self.pos.y, self.pos.x + i) for i in range(self.length)]

@dataclass(frozen=True)
class VerticalSlider:
    pos: Loc
    length: int
    char: str = "1"

    def get_identifier(self):
        return f"V{self.pos.y}{self.pos.x}{self.length}"

    def get_cells(self) -> List[Loc]:
        return [Loc(self.pos.y + i, self.pos.x) for i in range(self.length)]

BOARD_SIZE = 6 # Board size is fixed.
EXIT_LOC = Loc(2, 5) # Exit is fixed.

class BoardState:
    def __init__(self, horizontal_sliders: List[HorizontalSlider], vertical_sliders: List[VerticalSlider]):
        self.horizontal_sliders = tuple(horizontal_sliders)
        self.vertical_sliders = tuple(vertical_sliders)
        self._target_slider: Optional[HorizontalSlider] = next((s for s in self.horizontal_sliders if s.is_target), None)

    def is_success(self) -> bool:
        if not self._target_slider:
            return False
        # Success if any cell of the target slider is at EXIT_LOC
        return any(cell == EXIT_LOC for cell in self._target_slider.get_cells())

    def get_value(self) -> int:
        """Heuristic for search: higher is better."""
        if not self._target_slider:
            return 0
        
        # Distance from target slider's rightmost edge to the exit
        dist_to_exit = EXIT_LOC.x - (self._target_slider.pos.x + self._target_slider.length - 1)
        
        # Count obstacles between target and exit
        obstacles = 0
        occupied = self._get_occupancy_map()
        for x in range(self._target_slider.pos.x + self._target_slider.length, BOARD_SIZE):
            if (self._target_slider.pos.y, x) in occupied:
                obstacles += 1
                
        # Higher value for closer to exit and fewer obstacles
        return -(dist_to_exit + obstacles * 2)

    def get_state_identifier(self) -> str:
        all_states = [s.get_identifier() for s in self.horizontal_sliders] + \
                     [s.get_identifier() for s in self.vertical_sliders]
        return "".join(sorted(all_states))

    def _get_occupancy_map(self) -> Set[Tuple[int, int]]:
        occupied = set()
        for s in self.horizontal_sliders:
            for cell in s.get_cells():
                occupied.add((cell.y, cell.x))
        for s in self.vertical_sliders:
            for cell in s.get_cells():
                occupied.add((cell.y, cell.x))
        return occupied

    def get_neighbor_states(self) -> List['BoardState']:
        neighbors = []
        occupied = self._get_occupancy_map()

        # Try moving horizontal sliders
        for i, s in enumerate(self.horizontal_sliders):
            # Move Left
            curr_x = s.pos.x
            while curr_x > 0 and (s.pos.y, curr_x - 1) not in occupied:
                curr_x -= 1
                new_sliders = list(self.horizontal_sliders)
                new_sliders[i] = HorizontalSlider(Loc(s.pos.y, curr_x), s.length, s.is_target, s.char)
                neighbors.append(BoardState(new_sliders, list(self.vertical_sliders)))
            
            # Move Right
            curr_x = s.pos.x
            while curr_x + s.length < BOARD_SIZE and (s.pos.y, curr_x + s.length) not in occupied:
                curr_x += 1
                new_sliders = list(self.horizontal_sliders)
                new_sliders[i] = HorizontalSlider(Loc(s.pos.y, curr_x), s.length, s.is_target, s.char)
                neighbors.append(BoardState(new_sliders, list(self.vertical_sliders)))

        # Try moving vertical sliders
        for i, s in enumerate(self.vertical_sliders):
            # Move Up
            curr_y = s.pos.y
            while curr_y > 0 and (curr_y - 1, s.pos.x) not in occupied:
                curr_y -= 1
                new_v_sliders = list(self.vertical_sliders)
                new_v_sliders[i] = VerticalSlider(Loc(curr_y, s.pos.x), s.length, s.char)
                neighbors.append(BoardState(list(self.horizontal_sliders), new_v_sliders))
            
            # Move Down
            curr_y = s.pos.y
            while curr_y + s.length < BOARD_SIZE and (curr_y + s.length, s.pos.x) not in occupied:
                curr_y += 1
                new_v_sliders = list(self.vertical_sliders)
                new_v_sliders[i] = VerticalSlider(Loc(curr_y, s.pos.x), s.length, s.char)
                neighbors.append(BoardState(list(self.horizontal_sliders), new_v_sliders))

        return neighbors

    def __hash__(self):
        return hash(self.get_state_identifier())

    def __eq__(self, other):
        if not isinstance(other, BoardState):
            return False
        return self.get_state_identifier() == other.get_state_identifier()
