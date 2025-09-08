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


def get_size(path: str) -> int:
    """
    Calculate total size of a file or directory (bytes).
    - File: returns its size
    - Directory: sum of all files (recursively)
    Silently skips files that disappear or are not accessible.
    """
    if os.path.isfile(path):
        try:
            return os.path.getsize(path)
        except (FileNotFoundError, PermissionError):
            logger.warning("Skipping not accessible file: %s", path)
            return 0

    total = 0
    for root, _, files in os.walk(path):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                total += os.path.getsize(fpath)
            except (FileNotFoundError, PermissionError):
                logger.warning("Skipping not accessible file: %s", fpath)
                continue
    return total


def convert_size(size_bytes: int) -> str:
    """
    Convert bytes to a human-readable string (B, KB, MB, GB, TB).
    """
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            # keep up to 2 decimals, strip trailing .0
            s = f"{size:.2f}".rstrip("0").rstrip(".")
            return f"{s} {unit}"
        size /= 1024.0


def run(args):
    """
    Analyse directory: prints total size and each direct child (file/dir) size,
    sorted by size (desc).

    Args:
        args.path (str): path to directory

    Returns:
        dict | None: {
            "path": <abs path>,
            "total_bytes": <int>,
            "entries": List[Tuple[name, size_bytes]]
        } on success; None on error.
    """
    path = os.path.abspath(args.path)
    logger.info("Analyse command started: path=%s", path)

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

    try:
        entries = os.listdir(path)
    except PermissionError as e:
        msg = f"Permission denied while listing {path}: {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None
    except OSError as e:
        msg = f"OS error while listing {path}: {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    entries_paths = [os.path.join(path, entry) for entry in entries]

    sizes = []
    total_size = 0
    for entry_path in entries_paths:
        size = get_size(entry_path)
        sizes.append((os.path.basename(entry_path), size))
        total_size += size

    # output
    print(f"full size: {convert_size(total_size)}")
    logger.info("Total size for %s: %s", path, convert_size(total_size))

    for name, size in sorted(sizes, key=lambda x: x[1], reverse=True):
        print(f" - {name}  -  {convert_size(size)}")
        logger.info("%s: %s", name, convert_size(size))

    logger.info("Analyse completed: %s", path)
    return {"path": path, "total_bytes": total_size, "entries": sizes}
