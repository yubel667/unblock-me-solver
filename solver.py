import heapq
import time
import json
import sys
from typing import List, Tuple, Optional, Dict
from board import BoardState, Loc
from board_io import parse_from_text

def solve(initial_state: BoardState) -> Tuple[Optional[List[Dict]], int, float]:
    start_time = time.time()
    
    if initial_state.is_success():
        return [], 0, time.time() - start_time

    # Priority queue stores (f_score, g_score, state_id, state, path)
    # f_score = g_score + h_score
    # h_score = -state.get_value()
    
    # We use a counter for state_id to avoid comparing BoardState objects directly in heapq
    # if f_score and g_score are equal.
    counter = 0
    
    start_h = -initial_state.get_value()
    # (f, g, id, state, path)
    pq = [(start_h, 0, counter, initial_state, [])]
    
    # visited stores state_id -> g_score
    visited = {initial_state.get_state_identifier(): 0}
    
    nodes_expanded = 0

    while pq:
        f, g, _, curr_state, path = heapq.heappop(pq)
        nodes_expanded += 1

        if curr_state.is_success():
            end_time = time.time()
            return path, len(visited), end_time - start_time

        for neighbor in curr_state.get_neighbor_states():
            state_id = neighbor.get_state_identifier()
            new_g = g + 1
            
            if state_id not in visited or new_g < visited[state_id]:
                visited[state_id] = new_g
                h = -neighbor.get_value()
                
                # Find which slider moved to create the path entry
                move = find_move(curr_state, neighbor)
                new_path = path + [move]
                
                counter += 1
                heapq.heappush(pq, (new_g + h, new_g, counter, neighbor, new_path))
    
    end_time = time.time()
    return None, len(visited), end_time - start_time

def find_move(old_state: BoardState, new_state: BoardState) -> Dict:
    # Compare horizontal sliders
    for s1, s2 in zip(old_state.horizontal_sliders, new_state.horizontal_sliders):
        if s1.pos != s2.pos:
            return {
                "char": s1.char,
                "from": (s1.pos.y, s1.pos.x),
                "to": (s2.pos.y, s2.pos.x)
            }
    # Compare vertical sliders
    for s1, s2 in zip(old_state.vertical_sliders, new_state.vertical_sliders):
        if s1.pos != s2.pos:
            return {
                "char": s1.char,
                "from": (s1.pos.y, s1.pos.x),
                "to": (s2.pos.y, s2.pos.x)
            }
    return {}

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 solver.py <question_file>")
        return

    file_path = sys.argv[1]
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        initial_state = parse_from_text(content)
    except Exception as e:
        print(f"Error loading board: {e}")
        return

    solution, visited_count, duration = solve(initial_state)

    if solution is None:
        print(json.dumps({
            "error": "No solution found",
            "visited": visited_count,
            "time": f"{duration:.4f}s"
        }, indent=2))
    else:
        print(json.dumps({
            "solution": solution,
            "visited": visited_count,
            "time": f"{duration:.4f}s",
            "steps": len(solution)
        }, indent=2))

if __name__ == "__main__":
    main()
