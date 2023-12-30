import os

def print_directory_tree(path, prefix='', is_last=False):
    is_dir = os.path.isdir(path)
    basename = os.path.basename(path)

    # Print the current item
    if prefix:
        # If this is the last entry in a directory, print └──, else print ├──
        if is_last:
            print(prefix[:len(prefix) - 4] + '└── ' + basename)
        else:
            print(prefix + '├── ' + basename)
    else:
        print(basename)

    if is_dir:
        entries = sorted(os.listdir(path))
        entries = [e for e in entries if e not in ['__pycache__', '.git', '.venv']]
        # Print the children
        for i, child in enumerate(entries):
            new_prefix = prefix + ('│   ' if not is_last else '    ')
            print_directory_tree(os.path.join(path, child), new_prefix, i == len(entries) - 1)

print_directory_tree('.')