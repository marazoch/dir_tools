import os
import re

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

    if not os.path.exists(path):
        raise FileNotFoundError(f'Path does not exist: {path}')

    try:
        regex = re.compile(pattern)
    except re.error:
        raise ValueError(f'Invalid regular expression: {pattern}')

    matched_files = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if regex.fullmatch(file):
                matched_files.append(os.path.join(root, file))

    for file in matched_files:
        print(file)

    return matched_files
