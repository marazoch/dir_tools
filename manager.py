import argparse
import os
import logging
from features import copy, delete, count, find, move, add_date, analyse, hashsum, duplicates

log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, 'manager.log'),
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

COMMANDS = {
    "copy": copy,
    "delete": delete,
    "count": count,
    "find": find,
    "move": move,
    "add_date": add_date,
    "analyse": analyse,
    "hashsum": hashsum,
    "duplicates": duplicates,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python manager.py",
        description="Simple file manager",
        epilog="For more information visit https://github.com/marazoch/dir_tools",
    )

    subparsers = parser.add_subparsers(dest="command", required=True, metavar="command")

    p = subparsers.add_parser("copy", help="Copy file to destination folder")
    p.add_argument("-s", "--src", required=True, metavar="", help="file source")
    p.add_argument("-d", "--dst", required=True, metavar="", help="destination folder")

    p = subparsers.add_parser("delete", help="Delete file or folder")
    p.add_argument("-s", "--src", required=True, metavar="", help="file/folder to delete")

    p = subparsers.add_parser("count", help="Count files in folder")
    p.add_argument("-p", "--path", required=True, metavar="", help="path to folder to count")

    p = subparsers.add_parser("find", help="Find file by name (regex)")
    p.add_argument("-p", "--path", required=True, metavar="", help="path to folder for search")
    p.add_argument("-r", "--regex", required=True, metavar="", help="filename regex to find")

    p = subparsers.add_parser("move", help="Move file or folder")
    p.add_argument("-s", "--src", required=True, metavar="", help="source path")
    p.add_argument("-d", "--dst", required=True, metavar="", help="destination folder")

    p = subparsers.add_parser("add_date", help="Rename file(s) with creation date")
    p.add_argument("-p", "--path", required=True, metavar="", help="path to file or folder")
    p.add_argument("-r", "--recursive", action="store_true", help="process all subdirectories")

    p = subparsers.add_parser("analyse", help="Analyse files in dir")
    p.add_argument("-p", "--path", metavar="", required=True, help="path to file or folder")

    p = subparsers.add_parser("hashsum", help="Calculate hash of file or directory")
    p.add_argument("-p", "--path", required=True, metavar="", help="Path to file or directory")
    p.add_argument(
        "-m",
        "--method",
        choices=["sha256", "md5"],
        default="sha256",
        metavar="",
        help="Hash algorithm (sha256 or md5)",
    )

    p = subparsers.add_parser("duplicates", help="Find duplicate files in directory")
    p.add_argument("-p", "--path", required=True, metavar="", help="Path to directory")

    return parser


def dispatch(args: argparse.Namespace):
    mod = COMMANDS[args.command]
    return mod.run(args)


def main():
    parser = build_parser()
    args = parser.parse_args()
    dispatch(args)


if __name__ == "__main__":
    main()
