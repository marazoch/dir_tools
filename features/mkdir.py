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
    Create a directory (single level).

    Args:
        args.path : str, base directory where to create
        args.name : str, new folder name (no path)

    Returns:
        str: created directory path

    Raises:
        FileNotFoundError: if base path doesn't exist
        NotADirectoryError: if base path is not a directory
        FileExistsError: if target already exists
        PermissionError: if creation is not permitted
    """
    base = args.path
    name = args.name

    logging.info(f"New folder: base={base}, name={name}")

    if not os.path.exists(base):
        logging.error(f"Base path does not exist: {base}")
        raise FileNotFoundError(f"Base path does not exist: {base}")

    if not os.path.isdir(base):
        logging.error(f"Base path is not a directory: {base}")
        raise NotADirectoryError(f"Path is not a directory: {base}")

    if not name or os.path.basename(name) != name:
        logging.error(f"Invalid folder name: {name}")
        raise ValueError("Invalid folder name: must be a base name without path separators")

    target = os.path.join(base, name)
    if os.path.exists(target):
        logging.error(f"Folder already exists: {target}")
        raise FileExistsError(f"Folder already exists: {target}")

    try:
        os.makedirs(target, exist_ok=False)
        logging.info(f"Folder created: {target}")
        print(f"Folder created: {target}")
        return target
    except PermissionError as e:
        logging.error(f"Permission denied: {e}")
        raise
