import os
import hashlib
import logging

log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, 'manager.log'),
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


def file_hash(path):
    """
    Calculate SHA256 hash of a file.

    :param path: str - path to the file
    :return: str - hex digest of SHA256 hash
    :raises: Exception if file cannot be read or hashed
    """
    hash_func = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            data = f.read()
            hash_func.update(data)
        logging.info(f'Hashed file: {path}')
        return hash_func.hexdigest()
    except Exception as e:
        logging.error(f'Error hashing file {path}: {e}')
        raise


def run(args):
    """
    Search for duplicate files in a directory and print groups of duplicates.

    Uses SHA256 hashing to identify identical files.

    :param args: argparse.Namespace with field:
        - path: str, path to directory for duplicate search
    :return: None, prints duplicates to stdout and logs actions/errors
    """
    path = args.path

    logging.info(f'Started duplicate search in directory: {path}')

    if not os.path.isdir(path):
        logging.error(f'Path is not a directory: {path}')
        print(f'Path is not a directory: {path}')
        return

    hashes = dict()

    for root, subfolders, files in os.walk(path):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                h = file_hash(filepath)
                if h in hashes:
                    hashes[h].append(filepath)
                else:
                    hashes[h] = [filepath]
            except Exception as e:
                logging.error(f'Error hashing {filepath}: {e}')
                print(f'Error hashing {filepath}: {e}')

    duplicates_found = False
    for h, files_list in hashes.items():
        if len(files_list) > 1:
            duplicates_found = True
            print(f'Duplicate files (hash={h}):')
            for f in files_list:
                print(f'  {f}')
            print()

    if not duplicates_found:
        print('No duplicates found.')
