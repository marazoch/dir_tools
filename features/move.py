import os
import shutil
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
    Moves a file or directory to a new location.

    If the target file already exists in the destination folder,
    the operation is aborted with an error message.

    :param:
            args: Namespace: Arguments from argparse.
            src: str: Path to the source file or directory.
            dst: str: Path to the destination file or folder.
    :raises:
            FileNotFoundError: If the source does not exist.
            FileExistsError: If the file already exists in the destination.
            NotADirectoryError: Destination is not a directory.
            PermissionError: Permission denied while moving.
    :return:
    """
    source = args.src
    destination = args.dst

    logging.info(f'Move command started: src={source}, dst={destination}')

    if not os.path.exists(source):
        logging.error(f'Source does not exist: {source}')
        raise FileNotFoundError(f'Source does not exist: {source}')

    if not os.path.exists(destination):
        logging.error(f'Destination does not exist: {destination}')
        raise FileNotFoundError(f'Destination does not exist: {destination}')

    if not os.path.isdir(destination):
        logging.error(f'Destination is not a directory: {destination}')
        raise NotADirectoryError(f'Destination is not a directory: {destination}')

    base_name = os.path.basename(source)
    target_path = os.path.join(destination, base_name)

    # prohibit to move to the same place
    if os.path.abspath(source) == os.path.abspath(target_path):
        logging.error('Cannot move to the same location. File already exists.')
        raise FileExistsError('Cannot move to the same location. File already exists.')

    # if file already exists
    if os.path.exists(target_path):
        logging.error(f'File already exists at destination: {target_path}')
        raise FileExistsError(f'File already exists at destination: {target_path}')

    try:
        shutil.move(source, target_path)
        logging.info(f'Moved successfully: {source} to {destination}')
        print(f'Moved {source} -> {destination}')
    except PermissionError as e:
        logging.error(f'Permission denied while moving: {e}')
        raise PermissionError(f'Permission denied while moving: {e}')
