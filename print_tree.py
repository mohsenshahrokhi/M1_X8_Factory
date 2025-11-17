import os

def print_tree(start_path, prefix=""):
    entries = sorted(os.listdir(start_path))
    entries_count = len(entries)

    for index, entry in enumerate(entries):
        path = os.path.join(start_path, entry)
        connector = "└── " if index == entries_count - 1 else "├── "
        print(prefix + connector + entry)

        if os.path.isdir(path):
            extension = "    " if index == entries_count - 1 else "│   "
            print_tree(path, prefix + extension)


if __name__ == "__main__":
    root = os.path.dirname(os.path.abspath(__file__))
    print(f"Project Tree: {root}\n")
    print_tree(root)
