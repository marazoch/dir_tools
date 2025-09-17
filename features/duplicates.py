import os
import sys
import hashlib
import logging
from collections import defaultdict

log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "manager.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)

logger = logging.getLogger(__name__)

_CHUNK = 1024 * 1024  # 1 MiB


def _hash_file(path: str, method: str = "sha256") -> str:
    """Streamed hash of a file (no full read into memory)."""
    h = hashlib.sha256() if method == "sha256" else hashlib.md5()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(_CHUNK)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _group_by_size(root: str) -> dict[int, list[str]]:
    by_size = defaultdict(list)
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            fp = os.path.join(dirpath, name)
            try:
                sz = os.path.getsize(fp)
            except (FileNotFoundError, PermissionError, OSError):
                # skip transient/inaccessible files
                logger.warning("Skipping not accessible: %s", fp)
                continue
            by_size[sz].append(fp)
    return by_size


def run(args):
    """
    Find duplicate files in directory using (size -> sha256) bucketing.

    Args:
        args.path (str): path to directory

    Returns:
        list[dict] | None:
          [
            {"hash": "<sha256>", "size": <bytes>, "files": [<path1>, <path2>, ...]},
            ...
          ]
          or None on error.
    """
    root = args.path
    logger.info("Duplicates command started: path=%s", root)

    if not os.path.exists(root):
        msg = f"Error: path not found — {root}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None
    if not os.path.isdir(root):
        msg = f"Error: not a directory — {root}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    by_size = _group_by_size(root)

    groups = []
    for size, files in sorted(by_size.items()):
        if len(files) < 2:
            continue  # unique size can't be duplicate
        # refine by content hash
        by_hash = defaultdict(list)
        for fp in files:
            try:
                d = _hash_file(fp, "sha256")
            except (FileNotFoundError, PermissionError, OSError) as e:
                logger.warning("Skipping on hash error %s: %s", fp, e)
                continue
            by_hash[d].append(fp)

        for digest, same in by_hash.items():
            if len(same) > 1:
                same_sorted = sorted(same)
                groups.append({"hash": digest, "size": size, "files": same_sorted})

    if groups:
        for i, g in enumerate(groups, 1):
            print(f"Duplicate group #{i}: {len(g['files'])} file(s), size {g['size']} bytes, sha256={g['hash']}")
            for p in g["files"]:
                print(f"  {p}")
    else:
        print("No duplicates found.")

    logger.info("Duplicates completed: %d group(s) in %s", len(groups), root)
    return groups
