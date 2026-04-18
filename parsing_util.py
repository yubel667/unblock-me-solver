import os

def normalize_level_path(input_path: str) -> str:
    """
    Normalizes a level identifier or path.
    Example: 'starter/1' -> 'unblock-me-solver/levels/starter/0001.txt'
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
            
    # List of possible base directories to search in
    bases = ["unblock-me-solver/levels", "levels", "."]
    
    for base in bases:
        path = os.path.join(base, input_path)
        if os.path.isfile(path):
            return path
            
    # If not found, return the path in unblock-me-solver/levels as default (useful for editor creating new files)
    if not input_path.startswith("unblock-me-solver/levels"):
        # Ensure we don't double up if levels is already in parts
        if input_path.startswith("levels/"):
            return os.path.join("unblock-me-solver", input_path)
        return os.path.join("unblock-me-solver/levels", input_path)
    
    return input_path
