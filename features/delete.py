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
    Deletes a file or directory.

    :param:
            args: Namespace: Arguments from argparse.
            source: str: Path to the file or directory to delete.
    :raises:
            FileNotFoundError: If the target does not exist.
            PermissionError: If there is no permission to delete.
            Exception: Target is neither file nor directory.
    :return:
    """
    target = args.src

    logging.info(f'Delete command started: target={target}')

    if not os.path.exists(target):
        logging.error(f'Target does not exist: {target}')
        raise FileNotFoundError(f'Target does not exist: {target}')

    try:
        if os.path.isfile(target):
            os.remove(target)
            logging.info(f"File deleted: {target}")
        elif os.path.isdir(target):
            shutil.rmtree(target)
            logging.info(f"Directory deleted: {target}")
        else:
            logging.error(f'Target is neither file nor directory: {target}')
            raise Exception(f'Target is neither file nor directory: {target}')
    except PermissionError as e:
        logging.error(f'Permission denied while deleting {target}: {e}')
        raise PermissionError(f'Permission denied while deleting {target}: {e}')

    logging.info(f'Successfully deleted: {target}')

    print(f'Successfully deleted: {target}')
