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
    Rename a file or directory in-place (same parent directory).

    Args:
        args.src  : str, existing file/dir path
        args.name : str, new base name (no path)

    Returns:
        str: destination path

    Raises:
        FileNotFoundError: if src doesn't exist
        ValueError: if name is empty or contains path separators
        FileExistsError: if destination already exists
        PermissionError: if rename is not permitted
    """
    src = args.src
    new_name = args.name

    logging.info(f"Rename started: src={src}, name={new_name}")

    if not os.path.exists(src):
        logging.error(f"Source does not exist: {src}")
        raise FileNotFoundError(f"Source does not exist: {src}")

    if not new_name or os.path.basename(new_name) != new_name:
        logging.error(f"Invalid new name: {new_name}")
        raise ValueError("Invalid new name: must be a base name without path separators")

    dst = os.path.join(os.path.dirname(src), new_name)

    if os.path.abspath(src) == os.path.abspath(dst):
        logging.info("Nothing to do: new name equals current name")
        print(f"Nothing to rename: {src}")
        return dst

    if os.path.exists(dst):
        logging.error(f"Target exists: {dst}")
        raise FileExistsError(f"Target already exists: {dst}")

    try:
        os.rename(src, dst)
        logging.info(f"Renamed: {src} -> {dst}")
        print(f"Renamed: {src} -> {dst}")
        return dst
    except PermissionError as e:
        logging.error(f"Permission denied: {e}")
        raise
