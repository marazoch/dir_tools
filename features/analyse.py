import os

def get_size(path):
    """
    Calculate the total size of a file or directory.

    If the path is a file, its size in bytes is returned.
    If the path is a directory, the size of all files
    (including in subdirectories) is summed.

    :param:
        path: str: Path to the file or directory.
    :return:
        int: Size in bytes.
    :raises:
        FileNotFoundError
        PermissionError
    """
    total = 0
    if os.path.isfile(path):
        return os.path.getsize(path)
    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                fp = os.path.join(root, f)
                total += os.path.getsize(fp)
            except FileNotFoundError:
                continue
            except PermissionError:
                continue
    return total

def convert_size(size_bytes):
    """
    Convert a file size in bytes to a human-readable string.

    Automatically chooses the appropriate unit: B, KB, MB, GB, TB.

    :param:
        size_bytes: int: File size in bytes.
    :return:
        str: Human-readable string representation of the size.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f'{round(size_bytes, 2)} {unit}'
        size_bytes /= 1024

def run(args):
    """
    Analyze the contents of a directory and display size information.

    The function prints the total size of the given directory
    and the size of each file/folder inside, sorted by size (descending).

    :param:
        args: Namespace: Parsed CLI arguments.
        path: str: Path to the directory to analyze.
    :return:
        Output example:
            full size: 72.37 MB
                - .venv  -  72.23 MB
                - .git  -  54.71 KB
                - tests  -  44.16 KB
                - features  -  24.89 KB
                - .idea  -  11.11 KB
                - .gitignore  -  4.78 KB
                - manager.py  -  2.37 KB
                - README.md  -  78 B
                - logs  -  0 B
    """
    path = args.path
    path = os.path.abspath(path)
    if not os.path.exists(path):
        print(f'Path does not exist: {path}')
        return

    entries = os.listdir(path)
    entries_paths = [os.path.join(path, entry) for entry in entries]

    sizes = []
    total_size = 0

    for entry_path in entries_paths:
        size = get_size(entry_path)
        sizes.append((os.path.basename(entry_path), size))
        total_size += size

    print(f'full size: {convert_size(total_size)}')
    for name, size in sorted(sizes, key=lambda x: x[1], reverse=True):
        print(f' - {name}  -  {convert_size(size)}')
