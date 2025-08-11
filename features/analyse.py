import os
import logging

log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, 'manager.log'),
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


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
        for file in files:
            try:
                file_path = os.path.join(root, file)
                total += os.path.getsize(file_path)
            except FileNotFoundError:
                logging.warning(f'File not found: {path}')
                continue
            except PermissionError:
                logging.warning(f'Permission denied: {path}')
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
    logging.info(f'Starting analyse for path: {path}')

    if not os.path.exists(path):
        logging.error(f'Path does not exist: {path}')
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

    logging.info(f'Total size for {path}: {convert_size(total_size)}')
    print(f'full size: {convert_size(total_size)}')

    for name, size in sorted(sizes, key=lambda x: x[1], reverse=True):
        logging.info(f'{name}: {convert_size(size)}')
        print(f' - {name}  -  {convert_size(size)}')

    logging.info(f'Analyse completed for path: {path}')