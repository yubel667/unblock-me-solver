import os
import sys
import subprocess
import argparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def export_single(level_id):
    """Worker function to export a single level."""
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = f".:{env.get('PYTHONPATH', '')}"
        
        # We pass the relative level_id (e.g. starter/0001)
        subprocess.run(
            [sys.executable, "export_webp.py", level_id],
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        return level_id, True, None
    except subprocess.CalledProcessError as e:
        return level_id, False, e.stderr

def batch_export():
    parser = argparse.ArgumentParser(description="Batch export Unblock Me solutions to WebP.")
    parser.add_argument("-p", "--parallelism", type=int, default=10, help="Number of parallel exports (default: 10)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing solutions")
    args = parser.parse_args()

    levels_dir = "levels"
    solutions_dir = "solutions"
    
    if not os.path.exists(levels_dir):
        print(f"Error: {levels_dir} folder not found.")
        return

    # Find all .txt files recursively
    all_levels = []
    for root, dirs, files in os.walk(levels_dir):
        for file in files:
            if file.endswith(".txt"):
                # Relative path from levels_dir, without .txt
                rel_path = os.path.relpath(os.path.join(root, file), levels_dir)
                level_id = rel_path.replace(".txt", "")
                all_levels.append(level_id)

    to_export = []
    for lid in all_levels:
        out_path = os.path.join(solutions_dir, f"{lid}.webp")
        if args.force or not os.path.exists(out_path):
            to_export.append(lid)
            
    to_export.sort()

    if not to_export:
        print("All solutions are already exported. Use --force to re-export.")
        return

    print(f"Found {len(to_export)} levels to export. Starting batch export (p={args.parallelism})...")

    with ThreadPoolExecutor(max_workers=args.parallelism) as executor:
        futures = {executor.submit(export_single, lid): lid for lid in to_export}
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Exporting WebPs", unit="file"):
            lid, success, error_msg = future.result()
            if not success:
                print(f"\nError exporting {lid}:")
                print(error_msg)

    print("\nBatch export complete.")

if __name__ == "__main__":
    batch_export()
