import os
import sys
import datetime
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
    Add the file creation date to filenames.

    Behavior:
      - If args.path is a file: rename just this file -> name_YYYY-MM-DD.ext
      - If args.path is a directory:
          * without --recursive: process only top-level files
          * with --recursive: process files in all subdirectories
      - If a target name already exists -> print error to stderr and skip that file
      - If a filename already contains the date string -> print 'Skipping ...' and leave it as is

    Args:
        args.path (str): Path to a file or directory
        args.recursive (bool): Recursive mode for directories

    Returns:
        list[str] | None: list of successfully renamed file paths; None on fatal path error
    """
    path = args.path
    recursive = bool(getattr(args, "recursive", False))

    logger.info("Add_date command started: path=%s, recursive=%s", path, recursive)

    if not os.path.exists(path):
        msg = f"Error: path not found — {path}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    renamed = []

    if os.path.isfile(path):
        new_path = _rename_with_date(path)
        if new_path:
            renamed.append(new_path)
    else:
        if recursive:
            for root, _, files in os.walk(path):
                for f in files:
                    fp = os.path.join(root, f)
                    new_path = _rename_with_date(fp)
                    if new_path:
                        renamed.append(new_path)
        else:
            for f in os.listdir(path):
                fp = os.path.join(path, f)
                if os.path.isfile(fp):
                    new_path = _rename_with_date(fp)
                    if new_path:
                        renamed.append(new_path)

    print(f"Processed: {len(renamed)} file(s)")
    logger.info("Add_date completed: %d file(s) renamed", len(renamed))
    return renamed


def _rename_with_date(file_path: str) -> str | None:
    """
    Rename a single file by appending its creation date to the name:
        <name>_YYYY-MM-DD<ext>

    Skips if:
      - filename already contains the date substring, or
      - the target name already exists (prints error and returns None).

    Returns:
        str | None: new full path if renamed; None if skipped or error.
    """
    try:
        ctime = os.path.getctime(file_path)
        date_str = datetime.datetime.fromtimestamp(ctime).strftime("%Y-%m-%d")

        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        name, ext = os.path.splitext(base_name)

        if date_str in name:
            msg = f"Skipping (already contains date): {file_path}"
            print(msg)
            logger.info(msg)
            return None

        new_name = f"{name}_{date_str}{ext}"
        new_path = os.path.join(dir_name, new_name)

        if os.path.exists(new_path):
            msg = f"Error: target already exists — {new_path}"
            print(msg, file=sys.stderr)
            logger.error(msg)
            return None

        os.rename(file_path, new_path)
        print(f"Renamed: {file_path} -> {new_path}")
        logger.info("Renamed: %s -> %s", file_path, new_path)
        return new_path

    except PermissionError as e:
        msg = f"Permission denied while renaming {file_path}: {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None
    except OSError as e:
        msg = f"OS error while renaming {file_path}: {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None
