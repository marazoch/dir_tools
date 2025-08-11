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

commands = {
    'copy': copy,
    'delete': delete,
    'count': count,
    'find': find,
    'move': move,
    'add_date': add_date,
    'analyse': analyse,
    'hashsum': hashsum,
    'duplicates': duplicates,
}


def main():
    parser = argparse.ArgumentParser(
        prog='python manager.py',
        description='simple file manager',
        epilog='for more information visit https://github.com/marazoch/dir_tools'
    )

    subparsers = parser.add_subparsers(dest='command', required=True, metavar='command')

    parser_copy = subparsers.add_parser('copy', help='Copy file to destination folder')
    parser_copy.add_argument('-s', '--src', required=True, metavar='', help='file source')
    parser_copy.add_argument('-d', '--dst', required=True, metavar='', help='destination folder')

    parser_delete = subparsers.add_parser('delete', help='Delete file or folder')
    parser_delete.add_argument('-s', '--src', required=True, metavar='', help='file source to delete')

    parser_count = subparsers.add_parser('count', help='Count files in folder')
    parser_count.add_argument('-p', '--path', required=True, metavar='', help='path to folder to count')

    parser_find = subparsers.add_parser('find', help='Find file by name')
    parser_find.add_argument('-p', '--path', required=True, metavar='', help='path to folder for search')
    parser_find.add_argument('-r', '--regex', required=True, metavar='', help='filename regex to find')

    parser_move = subparsers.add_parser("move", help="Move file or folder")
    parser_move.add_argument('-s', '--src', required=True, metavar='', help='source path')
    parser_move.add_argument('-d', '--dst', required=True, metavar='', help='destination folder')

    parser_add_date = subparsers.add_parser('add_date', help='Rename file(s) with creation date')
    parser_add_date.add_argument('-p', '--path', required=True, metavar='', help="path to file or folder")
    parser_add_date.add_argument('-r', '--recursive', action='store_true',
                                 help='process all subdirectories')

    parser_analyse = subparsers.add_parser('analyse', help='Analyse files in dir')
    parser_analyse.add_argument('-p', '--path', metavar='', required=True, help='path to file or folder')

    parser_hashsum = subparsers.add_parser('hashsum', help='Calculate hash of file or directory')
    parser_hashsum.add_argument('-p', '--path', required=True, help='Path to file or directory')
    parser_hashsum.add_argument('-m', '--method', choices=['sha256', 'md5'], default='sha256',
                                help='Hash algorithm')

    parser_duplicates = subparsers.add_parser('duplicates', help='Find duplicate files in directory')
    parser_duplicates.add_argument('-p', '--path', required=True, help='Path to directory')

    args = parser.parse_args()
    commands[args.command].run(args)


if __name__ == '__main__':
    main()
