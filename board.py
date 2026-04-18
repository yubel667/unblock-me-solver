from numpy import np
import enum
from typing import List

class Loc:
    def __init__(self, y, x):
        self.y = y
        self.x = x

class Direction(enum.Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

# Each board should have exactly 1 target slider.
class HorizontalSlider:
    def __init__(self, pos: Loc, length: int, is_target: bool = False):
        self.pos = pos
        self.length = length
        self.is_target = is_target

    def get_identifier(self):
        return f"H{self.pos.y}{self.pos.x}{self.length}{'T' if self.is_target else ''}"


class VerticalSlider:
    def __init__(self, pos: Loc, length: int):
        self.pos = pos
        self.length = length

    def get_identifier(self):
        return f"V{self.pos.y}{self.pos.x}{self.length}"

BOARD_SIZE = 6 # Board size is fixed.
EXIT_LOC = Loc(2, 5) # Exit is fixed.

class BoardState:

    def __init__(self, horizonal_sliders: List[HorizontalSlider], vertical_sliders: List[VerticalSlider]):
        self.horizontal_sliders = horizonal_sliders
        self.vertical_slides = vertical_sliders

    def get_value():
        # For BFS to determine search order.
        # TODO: the closer the target to EXIT_LOC, the higher.
        # the less obstacle from the target to the EXIT_LOC, the higher.
        pass

    def is_success():
        #TODO: the target slider touches the EXIT LOC means success.
        pass

    def get_state_identifier(self):
        all_states = [s.get_identifier() for s in self.horizontal_sliders] + [s.get_identifier() for s in self.vertical_slides]
        return "".join(sorted(all_states)) # all in one string tracking unique state.
    
    def get_neighbor_states() -> List[BoardState]:
        # TODO: implement it. for each slider, check if it can move up or down if it is virtical slider
        # or left or right if it is horizontal slider. for example, it can move up if the space up is free and
        # within the board boundary. gather all states and return it.
