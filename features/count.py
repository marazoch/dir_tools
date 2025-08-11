import os
import logging

log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, 'manager.log'),
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


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

    logging.info(f'Count command started: path={path}')

    if not os.path.exists(path):
        logging.error(f'Path does not exist: {path}')
        raise FileNotFoundError(f'Path does not exist: {path}')

    if not os.path.isdir(path):
        logging.error(f'Path is not a directory: {path}')
        raise NotADirectoryError(f'Path is not a directory: {path}')

    total_files = 0
    try:
        for root, dirs, files in os.walk(path):
            total_files += len(files)
    except PermissionError as e:
        logging.error(f'Permission denied while accessing {path}: {e}')
        raise PermissionError(f'Permission denied while accessing {path}: {e}')

    logging.info(f'Total files counted in {path}: {total_files}')

    print(f'Total files in {path}: {total_files}')

    return total_files
