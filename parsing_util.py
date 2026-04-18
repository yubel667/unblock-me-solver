import os

def normalize_level_path(input_path: str) -> str:
    """
    Normalizes a level identifier or path.
    Example: 'starter/1' -> 'levels/starter/0001.txt' (if in unblock-me-solver dir)
    """
    # If it's already an existing file, use it as is
    if os.path.isfile(input_path):
        return input_path
    
    # Check for category/number format (e.g., 'starter/1')
    parts = input_path.split('/')
    if len(parts) == 2:
        category, num_str = parts
        if num_str.isdigit():
            # Pad to 4 digits and add .txt
            input_path = f"{category}/{num_str.zfill(4)}.txt"
        elif not num_str.endswith(".txt"):
            input_path = f"{category}/{num_str}.txt"
            
    # Possible base directories to search in
    # Prioritize local 'levels' over 'unblock-me-solver/levels'
    bases = ["levels", "unblock-me-solver/levels", "."]
    
    for base in bases:
        path = os.path.join(base, input_path)
        if os.path.isfile(path):
            return path
            
    # If not found (e.g. creating new level in editor)
    # If we are inside unblock-me-solver, use 'levels/'
    if os.path.basename(os.getcwd()) == "unblock-me-solver":
        return os.path.join("levels", input_path)
    
    # Default to unblock-me-solver/levels if it exists or if we are at root
    return os.path.join("unblock-me-solver/levels", input_path)
