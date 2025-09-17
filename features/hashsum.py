import os
import sys
import hashlib
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

_CHUNK = 1024 * 1024  # 1 MiB


def _hasher(method: str):
    return hashlib.sha256() if method.lower() == "sha256" else hashlib.md5()


def _hash_file(path: str, method: str) -> str:
    """Stream the file to avoid loading it fully in memory."""
    h = _hasher(method)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(_CHUNK)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def run(args):
    """
    Calculate hash of a file or all files in a directory.

    Behavior:
      - args.method in {"sha256","md5"}; default "sha256"
      - For a single file: prints "<method>  <digest>  <path>"
      - For a directory:
          * prints the same line per file (recursive, sorted by path)
          * prints "TOTAL <method>  <aggregate>  <dir>" at the end,
            where aggregate is a deterministic hash of (relpath,digest) pairs.

    Returns:
        dict | None:
          {
            "method": "sha256" | "md5",
            "items": [{"path": <abs path>, "hash": <hex>}, ...],
            "total": <hex or None>,  # only for directories
            "root": <abs path>,      # input path
          }
        or None on error (with message printed to stderr).
    """
    path = args.path
    method = (args.method or "sha256").lower()
    if method not in {"sha256", "md5"}:
        method = "sha256"  # fallback

    logger.info("Hashsum command started: path=%s, method=%s", path, method)

    if not os.path.exists(path):
        msg = f"Error: path not found — {path}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    root_abs = os.path.abspath(path)

    try:
        if os.path.isfile(path):
            digest = _hash_file(path, method)
            print(f"{method}  {digest}  {path}")
            logger.info("%s  %s  %s", method, digest, path)
            return {
                "method": method,
                "items": [{"path": root_abs, "hash": digest}],
                "total": None,
                "root": root_abs,
            }

        if os.path.isdir(path):
            files = []
            for dirpath, _, filenames in os.walk(path):
                for name in filenames:
                    files.append(os.path.join(dirpath, name))
            files.sort()

            items = []
            agg = _hasher(method)

            for fp in files:
                try:
                    d = _hash_file(fp, method)
                except PermissionError as e:
                    msg = f"Permission denied: {fp}: {e}"
                    print(msg, file=sys.stderr)
                    logger.error(msg)
                    continue
                except OSError as e:
                    msg = f"OS error: {fp}: {e}"
                    print(msg, file=sys.stderr)
                    logger.error(msg)
                    continue

                print(f"{method}  {d}  {fp}")
                logger.info("%s  %s  %s", method, d, fp)
                items.append({"path": os.path.abspath(fp), "hash": d})

                rel = os.path.relpath(fp, path).replace(os.sep, "/")
                agg.update(rel.encode("utf-8"))
                agg.update(b"\x00")
                agg.update(d.encode("ascii"))
                agg.update(b"\n")

            total_hex = agg.hexdigest()
            print(f"TOTAL {method}  {total_hex}  {path}")
            logger.info("TOTAL %s  %s  %s", method, total_hex, path)

            return {
                "method": method,
                "items": items,
                "total": total_hex,
                "root": root_abs,
            }

        msg = f"Error: not a file or directory — {path}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    except PermissionError as e:
        msg = f"Permission denied while hashing {path}: {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None

    except OSError as e:
        msg = f"OS error while hashing {path}: {e}"
        print(msg, file=sys.stderr)
        logger.error(msg)
        return None
