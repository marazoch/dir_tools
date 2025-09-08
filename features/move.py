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
    Moves a file or directory to a new location.

    Behavior:
      - src must exist
      - dst must be an existing directory
      - if a file/dir with the same name exists in dst, operation fails
      - returns absolute path to moved object on success, None on error

    Args:
        args.src (str): Path to the source file or directory
        args.dst (str): Path to the destination directory

    Returns:
        str | None: new absolute path on success, None on error
    """
    source = args.src
    destination = args.dst
    logger.info("Move command started: src=%s, dst=%s", source, destination)

    if not os.path.exists(source):
        msg = f"Error: source not found — {source}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    if not os.path.exists(destination):
        msg = f"Error: destination not found — {destination}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    if not os.path.isdir(destination):
        msg = f"Error: destination is not a directory — {destination}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    base_name = os.path.basename(source)
    target_path = os.path.join(destination, base_name)

    # prohibit move to same place
    if os.path.abspath(source) == os.path.abspath(target_path):
        msg = "Error: cannot move to the same location"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    if os.path.exists(target_path):
        msg = f"Error: already exists at destination — {target_path}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    try:
        shutil.move(source, target_path)
        logger.info("Moved successfully: %s -> %s", source, target_path)
        print(f"Moved: {source} -> {target_path}")
        return os.path.abspath(target_path)

    except PermissionError as e:
        msg = f"Permission denied while moving {source}: {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    except OSError as e:
        msg = f"OS error while moving {source}: {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None
