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


def _unique_name(dst_dir: str, filename: str) -> str:
    """
    Generate a non-colliding filename in dst_dir.
    First try 'copy_<filename>', then 'copy_(1)_<filename>', 'copy_(2)_<filename>', ...
    """
    base = f"copy_{filename}"
    candidate = os.path.join(dst_dir, base)
    if not os.path.exists(candidate):
        return candidate

    i = 1
    while True:
        candidate = os.path.join(dst_dir, f"copy_({i})_{filename}")
        if not os.path.exists(candidate):
            return candidate
        i += 1


def run(args):
    """
    Copies a file from source to destination directory.

    Behavior:
      - `args.src` must be an existing file (links are treated as files).
      - `args.dst` must be an existing directory.
      - If a file with the same name exists in the destination, a new non-colliding
        name is generated: 'copy_<name>' or 'copy_(n)_<name>'.

    Args:
        args.src (str): source file path
        args.dst (str): destination directory path

    Returns:
        str | None: absolute path to the copied file on success, None on error.
    """
    src = args.src
    dst_dir = args.dst

    logger.info("Copy command started: src=%s, dst=%s", src, dst_dir)

    if not os.path.exists(src):
        msg = f"Error: source path not found — {src}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    if not (os.path.isfile(src) or os.path.islink(src)):
        msg = f"Error: source is not a file — {src}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    if not os.path.exists(dst_dir):
        msg = f"Error: destination directory not found — {dst_dir}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    if not os.path.isdir(dst_dir):
        msg = f"Error: destination is not a directory — {dst_dir}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    try:
        filename = os.path.basename(src)
        dst_path = os.path.join(dst_dir, filename)

        if os.path.exists(dst_path):
            new_path = _unique_name(dst_dir, filename)
            logger.warning("Destination exists. Using new name: %s", new_path)
            dst_path = new_path

        shutil.copy2(src, dst_path)

        logger.info("File copied successfully: %s -> %s", src, dst_path)
        print(f"Copied: {src} -> {dst_path}")
        return os.path.abspath(dst_path)

    except PermissionError as e:
        msg = f"Permission denied while copying {src} -> {dst_dir}: {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    except OSError as e:
        msg = f"OS error while copying {src} -> {dst_dir}: {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None
