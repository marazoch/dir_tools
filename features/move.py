import os
import shutil

def run(args):
    source = args.src
    destination = args.dst

    if not os.path.exists(source):
        raise FileNotFoundError(f"Source does not exist: {source}")

    if not os.path.exists(destination):
        raise FileNotFoundError(f"Destination does not exist: {destination}")

    if not os.path.isdir(destination):
        raise NotADirectoryError(f"Destination is not a directory: {destination}")

    base_name = os.path.basename(source)
    target_path = os.path.join(destination, base_name)

    # prohibit to move to the same place
    if os.path.abspath(source) == os.path.abspath(target_path):
        raise FileExistsError("Cannot move to the same location. File already exists.")

    # if file already exists
    if os.path.exists(target_path):
        raise FileExistsError(f"File already exists at destination: {target_path}")

    try:
        shutil.move(source, target_path)
    except PermissionError as e:
        raise PermissionError(f"Permission denied while moving: {e}")
