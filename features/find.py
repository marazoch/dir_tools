import os
import re
import logging

log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, 'manager.log'),
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


def run(args):
    """
    Finds files by regex pattern in a given directory.

    :param:
            args: Namespace: Arguments from argparse.
            path: str: Path to the directory.
            regex: str: Regex pattern for file names.
    :raises:
            FileNotFoundError: If the path does not exist.
            ValueError: If the regex pattern is invalid.
    :return:
            list of matched files
    """
    path = args.path
    pattern = args.regex

    logging.info(f'Find command started: path={path}, regex={pattern}')

    if not os.path.exists(path):
        logging.error(f'Path does not exist: {path}')
        raise FileNotFoundError(f'Path does not exist: {path}')

    try:
        regex = re.compile(pattern)
    except re.error as e:
        logging.error(f'Invalid regex pattern {pattern}: {e}')
        raise ValueError(f'Invalid regular expression: {pattern}')

    matched_files = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if regex.fullmatch(file):
                matched_files.append(os.path.join(root, file))

    logging.info(f'Find command completed: {len(matched_files)} files matched')

    for file in matched_files:
        print(file)

    return matched_files
