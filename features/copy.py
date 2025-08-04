import os
import shutil


def run(args):
    src = args.src
    dst = args.dst

    if not os.path.exists(src):
        raise FileNotFoundError(f"Source file does not exist: {src}")

    if not os.path.isdir(dst):
        raise NotADirectoryError(f"Path is not a directory: {dst}")

    if os.path.isdir(dst):
        filename = os.path.basename(src)
        dst_file = os.path.join(dst, filename)

        if os.path.exists(dst_file):
            dst_file = os.path.join(dst, f"copy_{filename}")
    else:
        dst_file = dst

    try:
        shutil.copy2(src, dst_file)
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied while copying '{src}' to '{dst_file}': {e}. Maybe you forget filename in {src}")

    print(f"File {src} copied to {dst}")

    return dst_file
