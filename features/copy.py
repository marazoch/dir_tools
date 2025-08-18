import os
import shutil
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
    Copies a file from source to destination.

    If the destination file already exists in the same folder as the source,
    a new file is created with the prefix "copy_" to avoid overwriting.

    :param:
            args: Namespace: Arguments from argparse.
            src: str: Path to the source file.
            dst: str: Path to the destination file or folder.
    :raises:
            FileNotFoundError: If the source file does not exist.
            NotADirectoryError: Path is not a directory.
            PermissionError: If there is no permission to read/write the file.
    :return:
            dst_file
    """
    src = args.src
    dst = args.dst

    logging.info(f"Copy command started: src={src}, dst={dst}")

    if not os.path.exists(src):
        logging.error(f'Source file does not exist: {src}')
        raise FileNotFoundError(f'Source file does not exist: {src}')

    if not os.path.isdir(dst):
        logging.error(f'Destination path is not a directory: {dst}')
        raise NotADirectoryError(f'Path is not a directory: {dst}')

    if os.path.isdir(dst):
        filename = os.path.basename(src)
        dst_file = os.path.join(dst, filename)

        if os.path.exists(dst_file):
            dst_file = os.path.join(dst, f'copy_{filename}')
            logging.warning(f'File already exists in destination. Renaming to: {dst_file}')
    else:
        dst_file = dst

    try:
        shutil.copy2(src, dst_file)
        logging.info(f'File copied successfully: {src} to {dst_file}')
        print(f'File {src} copied to {dst}')
    except PermissionError as e:
        logging.error(f'Permission denied while copying {src} to {dst_file}: {e}')
        raise PermissionError(
            f'Permission denied while copying {src} to {dst_file}: {e}. Maybe you forget filename in {src}')

    return dst_file
