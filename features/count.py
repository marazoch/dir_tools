import os
import sys
import logging

log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "manager.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)

logger = logging.getLogger(__name__)


def run(args):
    """
    Counts the number of files in a directory (recursively).

    Args:
        args.path (str): Path to the directory.

    Returns:
        int | None: number of files on success; None if an error occurred.
    """
    path = args.path
    logger.info("Count command started: path=%s", path)

    if not os.path.exists(path):
        msg = f"Error: path not found — {path}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    if not os.path.isdir(path):
        msg = f"Error: not a directory — {path}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    total_files = 0

    try:
        for _, _, files in os.walk(path):
            total_files += len(files)
    except PermissionError as e:
        msg = f"Permission denied while accessing {path}: {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    except OSError as e:
        msg = f"OS error while accessing {path}: {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    logger.info("Total files counted in %s: %d", path, total_files)
    print(f"Total files in {path}: {total_files}")
    return total_files
