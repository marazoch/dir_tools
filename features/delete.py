import os
import shutil

def run(args):
    target = args.src

    if not os.path.exists(target):
        raise FileNotFoundError(f"Target does not exist: {target}")

    try:
        if os.path.isfile(target):
            os.remove(target)
        elif os.path.isdir(target):
            shutil.rmtree(target)
        else:
            raise Exception(f"Target is neither file nor directory: {target}")
    except PermissionError as e:
        raise PermissionError(f"Permission denied while deleting '{target}': {e}")

    print(f"Successfully deleted: {target}")
