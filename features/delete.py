import os
import shutil
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
    Deletes a file or directory.

    :param:
            args: Namespace: Arguments from argparse.
            source: str: Path to the file or directory to delete.
    :raises:
            FileNotFoundError: If the target does not exist.
            PermissionError: If there is no permission to delete.
            Exception: Target is neither file nor directory.
    :return: True if successfully deleted, False otherwise.
    """
    target = args.src
    logger.info("Delete command started: target=%s", target)

    if not os.path.exists(target):
        msg = f"Error: path not found — {target}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return False

    try:
        if os.path.isfile(target) or os.path.islink(target):
            os.remove(target)
            logger.info("File deleted: %s", target)
        elif os.path.isdir(target):
            shutil.rmtree(target)
            logger.info("Directory deleted: %s", target)
        else:
            msg = f"Error: target is neither file nor directory — {target}"
            print(msg, file=sys.stderr)
            logger.error(msg)
            return False
    except PermissionError as e:
        msg = f"Permission denied while deleting {target}: {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return False
    except OSError as e:
        msg = f"OS error while deleting {target}: {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return False

    logger.info("Successfully deleted: %s", target)
    print(f"Deleted: {target}")
    return True
