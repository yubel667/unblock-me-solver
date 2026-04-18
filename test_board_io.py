import unittest
from board import Loc
from board_io import parse_from_text, save_as_text

class TestBoardIO(unittest.TestCase):
    def test_serialization_roundtrip(self):
        # 0001.txt representation
        # Indices:
        #   012345
        # 0: 1
        # 1: 1  5
        # 2:002 5
        # 3:  2
        # 4:3  444
        # 5:3
        original_text = (
            "+------+\n"
            "| 1    |\n"
            "| 1  5 |\n"
            "|002 5 \n"
            "|  2   |\n"
            "|3  444|\n"
            "|3     |\n"
            "+------+"
        )
        
        state = parse_from_text(original_text)
        
        # Check target slider (0)
        self.assertTrue(any(s.is_target and s.char == '0' for s in state.horizontal_sliders))
        target = next(s for s in state.horizontal_sliders if s.is_target)
        self.assertEqual(target.pos, Loc(2, 0))
        self.assertEqual(target.length, 2)
        
        # Check some obstacles
        # Slider 1 is vertical at (0, 1) length 2
        s1 = next(s for s in state.vertical_sliders if s.char == '1')
        self.assertEqual(s1.pos, Loc(0, 1))
        self.assertEqual(s1.length, 2)
        
        # Slider 4 is horizontal at (4, 3) length 3
        s4 = next(s for s in state.horizontal_sliders if s.char == '4')
        self.assertEqual(s4.pos, Loc(4, 3))
        self.assertEqual(s4.length, 3)

        # Slider 5 is vertical at (1, 4) length 2
        s5 = next(s for s in state.vertical_sliders if s.char == '5')
        self.assertEqual(s5.pos, Loc(1, 4))
        self.assertEqual(s5.length, 2)
        
        # Round trip
        serialized_text = save_as_text(state)
        self.assertEqual(serialized_text.strip(), original_text.strip())

    def test_multiple_obstacles(self):
        text = (
            "+------+\n"
            "|aabbcc|\n"
            "|d  e  |\n"
            "|d00e  \n"
            "|d  e  |\n"
            "|   ff |\n"
            "|      |\n"
            "+------+"
        )
        state = parse_from_text(text)
        # 3 horizontal on top (a, b, c) + target (0) + f = 5 horizontal
        self.assertEqual(len(state.horizontal_sliders), 5)
        # 2 vertical (d, e) = 2 vertical
        self.assertEqual(len(state.vertical_sliders), 2)
        
        # Verify vertical slider 'd' is at (1, 0) length 3
        sd = next(s for s in state.vertical_sliders if s.char == 'd')
        self.assertEqual(sd.pos, Loc(1, 0))
        self.assertEqual(sd.length, 3)

        # Verify target '0' is at (2, 1) length 2
        s0 = next(s for s in state.horizontal_sliders if s.is_target)
        self.assertEqual(s0.pos, Loc(2, 1))
        self.assertEqual(s0.length, 2)

        serialized = save_as_text(state)
        self.assertEqual(serialized.strip(), text.strip())

if __name__ == '__main__':
    unittest.main()
