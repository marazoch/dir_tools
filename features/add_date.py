import os
import datetime


def run(args):
    """
    Adds the file creation date to the file name.

    If a file path is provided, only that file will be renamed.
    If a directory is provided:
        - Without --recursive: only files in the top-level directory are processed.
        - With --recursive: all files in the directory and its subdirectories are processed.

    :param:
            args: Namespace: Arguments from argparse.
            path: str: Path to file or directory.
            recursive: bool: Whether to process directories recursively.
    :raises:
            FileNotFoundError: If the given path does not exist.
            FileExistsError: If the new file name already exists.
    :return:  filename with date
    """
    path = args.path
    recursive = args.recursive

    if not os.path.exists(path):
        raise FileNotFoundError(f'Path does not exist: {path}')

    if os.path.isfile(path):
        _rename_with_date(file_path=path)
    else:
        if recursive:
            for root, subfolders, files in os.walk(path):
                for f in files:
                    file_path = os.path.join(root, f)
                    _rename_with_date(file_path=file_path)
        else:
            for f in os.listdir(path):
                file_path = os.path.join(path, f)
                if os.path.isfile(file_path):
                    _rename_with_date(file_path=file_path)


def _rename_with_date(file_path):
    """
    Renames a file by appending its creation date to the name.

    Example:


    :param:
            file_path: str: Path to file or rename.
            recursive: bool: Whether to process directories recursively.
    :raises:
            FileExistsError: If the new file name already exists.
    :return:
            Output example:
            original file: "document.txt"
            after rename: "document_2025-08-06.txt"

    """
    creation_time = os.path.getctime(file_path)
    date_str = datetime.datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d')

    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)

    if date_str in name:
        print(f'Skipping (already contains date): {file_path}')
        return

    new_name = f'{date_str}_{name}{ext}'
    new_path = os.path.join(dir_name, new_name)

    if os.path.exists(new_path):
        raise FileExistsError(f'File already exists: {new_path}')

    os.rename(file_path, new_path)
    print(f'Renamed: {file_path} to {new_path}')
