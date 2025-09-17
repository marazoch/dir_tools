import os
import re
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
    Find files by regex pattern in a given directory.

    Args:
        args.path (str): path to directory
        args.regex (str): regex pattern for file names

    Returns:
        list[str] | None: matched file paths, or None if error occurred
    """
    path = args.path
    pattern = args.regex
    logger.info("Find command started: path=%s, regex=%s", path, pattern)

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
        regex = re.compile(pattern)
    except re.error as e:
        msg = f"Error: invalid regex '{pattern}': {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    matched_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if regex.fullmatch(file):
                full = os.path.join(root, file)
                matched_files.append(full)

    logger.info("Find command completed: %d files matched", len(matched_files))

    if matched_files:
        for f in matched_files:
            print(f)
    else:
        print("No matches found")

    return matched_files
