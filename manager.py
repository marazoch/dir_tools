import argparse
from features import copy, delete, count, find

commands = {
    'copy': copy,
    'delete': delete,
    'count': count,
    'find': find,
}


def main():
    parser = argparse.ArgumentParser(
        prog='file_manager',
        description='simple file manager',
        epilog='for more information visit https://github.com/marazoch/dir_tools'
    )
    subparsers = parser.add_subparsers(dest='command', required=True, metavar='command')

    p = subparsers.add_parser('copy', help='Copy file')
    p.add_argument('-s', '--src', required=True, metavar='', help='file source')
    p.add_argument('-d', '--dst', required=True, metavar='', help='copy destination')

    p = subparsers.add_parser('delete', help='Delete file or dir')
    p.add_argument('-s', '--src', required=True, metavar='', help='file source')

    p = subparsers.add_parser('count', help='Count files')
    p.add_argument('-p', '--path', required=True, metavar='', help='path to file')

    args = parser.parse_args()
    commands[args.command].run(args)


if __name__ == '__main__':
    main()
