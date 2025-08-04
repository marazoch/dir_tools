import argparse
from features import copy, delete, count, find, move

commands = {
    'copy': copy,
    'delete': delete,
    'count': count,
    'find': find,
    'move': move,
    'add_date': NotImplemented,
    'analyse': NotImplemented
}


def main():
    parser = argparse.ArgumentParser(
        prog='python manager.py',
        description='simple file manager',
        epilog='for more information visit https://github.com/marazoch/dir_tools'
    )
    subparsers = parser.add_subparsers(dest='command', required=True, metavar='command')

    p = subparsers.add_parser('copy', help='Copy file to destination folder')
    p.add_argument('-s', '--src', required=True, metavar='', help='file source')
    p.add_argument('-d', '--dst', required=True, metavar='', help='destination folder')

    p = subparsers.add_parser('delete', help='Delete file or folder')
    p.add_argument('-s', '--src', required=True, metavar='', help='file source to delete')

    p = subparsers.add_parser('count', help='Count files in folder')
    p.add_argument('-p', '--path', required=True, metavar='', help='path to folder to count')

    p = subparsers.add_parser('find', help='Find file by name')
    p.add_argument('-p', '--path', required=True, metavar='', help='path to folder for search')
    p.add_argument('-r', '--regex', required=True, metavar='', help='filename regex to find')

    parser_move = subparsers.add_parser("move", help="Move file or folder")
    parser_move.add_argument('-s', '--src', required=True, metavar='', help='source path')
    parser_move.add_argument('-d', '--dst', required=True, metavar='', help='destination folder')

    args = parser.parse_args()
    commands[args.command].run(args)


if __name__ == '__main__':
    main()
