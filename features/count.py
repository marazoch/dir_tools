import os


def run(args):
    """
    Counts the number of files in a directory (including nested files).

    :param:
            args: Namespace: Arguments from argparse.
            path: str: Path to the directory.
    :raises:
            FileNotFoundError: If the source file does not exist.
            NotADirectoryError: Path is not a directory.
            PermissionError: If there is no permission to read/write the file.
    :return:
            total_files: int: number of files in directory
    """
    path = args.path

    if not os.path.exists(path):
        raise FileNotFoundError(f'Path does not exist: {path}')

    if not os.path.isdir(path):
        raise NotADirectoryError(f'Path is not a directory: {path}')

    total_files = 0
    try:
        for root, dirs, files in os.walk(path):
            total_files += len(files)
    except PermissionError as e:
        raise PermissionError(f'Permission denied while accessing {path}: {e}')

    print(f'Total files in {path}: {total_files}')

    return total_files
