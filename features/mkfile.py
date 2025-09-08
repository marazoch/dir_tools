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
    Create an empty file.

    Args:
        args.path : str, base directory where to create
        args.name : str, filename (no path)

    Returns:
        str: created file path

    Raises:
        FileNotFoundError: if base directory doesn't exist
        NotADirectoryError: if path is not a directory
        FileExistsError: if file already exists
        PermissionError: if creation is not permitted
    """
    base = args.path
    name = args.name

    logging.info(f"New file: base={base}, name={name}")

    if not os.path.exists(base):
        logging.error(f"Base path does not exist: {base}")
        raise FileNotFoundError(f"Base path does not exist: {base}")

    if not os.path.isdir(base):
        logging.error(f"Base path is not a directory: {base}")
        raise NotADirectoryError(f"Path is not a directory: {base}")

    if not name or os.path.basename(name) != name:
        logging.error(f"Invalid filename: {name}")
        raise ValueError("Invalid filename: must be a base name without path separators")

    target = os.path.join(base, name)
    if os.path.exists(target):
        logging.error(f"File already exists: {target}")
        raise FileExistsError(f"File already exists: {target}")

    try:
        # create empty file
        with open(target, "x", encoding="utf-8"):
            pass
        logging.info(f"File created: {target}")
        print(f"File created: {target}")
        return target
    except PermissionError as e:
        logging.error(f"Permission denied: {e}")
        raise
