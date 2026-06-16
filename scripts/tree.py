# tree.py
import os

def print_tree(dir_path, prefix="", max_depth=3, ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = {"__pycache__", ".git", ".venv", "venv"}
    
    entries = sorted(os.listdir(dir_path))
    entries = [e for e in entries if not e.startswith(".")]
    
    for i, entry in enumerate(entries):
        is_last = (i == len(entries) - 1)
        connector = "└── " if is_last else "├── "
        full_path = os.path.join(dir_path, entry)
        
        if os.path.isdir(full_path):
            if entry in ignore_dirs:
                continue
            print(prefix + connector + entry + "/")
            extension = "    " if is_last else "│   "
            if max_depth > 0:
                print_tree(full_path, prefix + extension, max_depth - 1, ignore_dirs)
        else:
            size = os.path.getsize(full_path)
            print(prefix + connector + f"{entry}  ({size:,} bytes)")



root = r"C:\Users\Erick\My Drive (kiyarashaminfar@gmail.com)\DCWATER\pump-predictive-maintenance"
print(f"Structure of: {root}\n")
print_tree(root, max_depth=5)