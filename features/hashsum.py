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


def file_hash(path, method='sha256'):
    """
    Calculate hash of a file using sha256 or md5.

    :param path: str - path to the file
           method: str - 'sha256' or 'md5' (default 'sha256')
    :return: str - hex digest of the hash
    :raises: Exception if file cannot be read or hashed
    """
    hash_func = hashlib.sha256() if method == 'sha256' else hashlib.md5()
    try:
        with open(path, 'rb') as f:
            data = f.read()
            hash_func.update(data)

        logging.info(f'Hashed file: {path} with algorithm {method}')
        return hash_func.hexdigest()
    except Exception as e:
        logging.error(f'Error hashing file {path}: {e}')
        raise


def run(args):
    """
    Calculate and print hash sums of a file or all files in a directory.

    Supports 'sha256' and 'md5' algorithms.

    :param args: argparse.Namespace with fields:
           path: str, path to file or directory
           method: str (optional), hash method ('sha256' or 'md5'), default 'sha256'
    :return: None, prints results to stdout and logs actions/errors
    """
    path = args.path
    method = args.method.lower() if args.method else 'sha256'

    logging.info(f'Started hashing for path: {path} with algo: {method}')

    if not os.path.exists(path):
        logging.error(f'Path does not exist: {path}')
        print(f'Path does not exist: {path}')
        return

    if os.path.isfile(path):
        try:
            h = file_hash(path, method)
            logging.info(f'{method}({path}) = {h}')
            print(f'{method}({path}) = {h}')
        except Exception as e:
            logging.error(f'Error hashing file {path}: {e}')
            print(f'Error hashing file {path}: {e}')
    elif os.path.isdir(path):
        logging.info(f'Hashes of files in directory {path}:')
        print(f'Hashes of files in directory {path}:')
        for root, subfolders, files in os.walk(path):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    h = file_hash(filepath, method)
                    logging.info(f'{method}({filepath}) = {h}')
                    print(f'{method}({filepath}) = {h}')
                except Exception as e:
                    logging.error(f'Error hashing {filepath}: {e}')
                    print(f'Error hashing {filepath}: {e}')
    else:
        logging.error(f'Not a file or directory: {path}')
        print(f'Not a file or directory: {path}')
