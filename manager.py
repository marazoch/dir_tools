import argparse
import os
import logging

from features import copy, delete, count, find, move, add_date, analyse, hashsum, duplicates, rename, mkfile, mkdir

log_dir = os.path.join(os.path.dirname(__file__), 'logs')
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
    'rename': rename,
    'mkfile': mkfile,
    'mkdir': mkdir,
}


def main():
    parser = argparse.ArgumentParser(
        prog='python manager.py',
        description='simple file manager',
        epilog='for more information visit https://github.com/marazoch/dir_tools'
    )

    subparsers = parser.add_subparsers(dest='command', required=True, metavar='command')

    p_copy = subparsers.add_parser('copy', help='Copy file to destination folder')
    p_copy.add_argument('-s', '--src', required=True, metavar='', help='file source')
    p_copy.add_argument('-d', '--dst', required=True, metavar='', help='destination folder')

    p_delete = subparsers.add_parser('delete', help='Delete file or folder')
    p_delete.add_argument('-s', '--src', required=True, metavar='', help='file/folder to delete')

    p_count = subparsers.add_parser('count', help='Count files in folder')
    p_count.add_argument('-p', '--path', required=True, metavar='', help='path to folder to count')

    p_find = subparsers.add_parser('find', help='Find file by name (regex)')
    p_find.add_argument('-p', '--path', required=True, metavar='', help='path to folder for search')
    p_find.add_argument('-r', '--regex', required=True, metavar='', help='filename regex to find')

    p_move = subparsers.add_parser('move', help='Move file or folder')
    p_move.add_argument('-s', '--src', required=True, metavar='', help='source path')
    p_move.add_argument('-d', '--dst', required=True, metavar='', help='destination folder')

    p_add_date = subparsers.add_parser('add_date', help='Rename file(s) with creation date')
    p_add_date.add_argument('-p', '--path', required=True, metavar='', help="path to file or folder")
    p_add_date.add_argument('-r', '--recursive', action='store_true', help='process subdirectories recursively')

    p_analyse = subparsers.add_parser('analyse', help='Analyse files in dir')
    p_analyse.add_argument('-p', '--path', metavar='', required=True, help='path to directory')

    p_hashsum = subparsers.add_parser('hashsum', help='Calculate hash of file or directory')
    p_hashsum.add_argument('-p', '--path', required=True, metavar='', help='Path to file or directory')
    p_hashsum.add_argument('-m', '--method', choices=['sha256', 'md5'], default='sha256', metavar='',
                           help='Hash algorithm (sha256 or md5)')

    p_duplicates = subparsers.add_parser('duplicates', help='Find duplicate files in directory')
    p_duplicates.add_argument('-p', '--path', required=True, metavar='', help='Path to directory')

    p_rename = subparsers.add_parser('rename', help='Rename file or directory (same parent dir)')
    p_rename.add_argument('-s', '--src', required=True, metavar='', help='source file/dir path')
    p_rename.add_argument('-n', '--name', required=True, metavar='', help='new base name')

    p_mkfile = subparsers.add_parser('mkfile', help='Create empty file in a directory')
    p_mkfile.add_argument('-p', '--path', required=True, metavar='', help='base directory')
    p_mkfile.add_argument('-n', '--name', required=True, metavar='', help='filename')

    p_mkdir = subparsers.add_parser('mkdir', help='Create a folder in a directory')
    p_mkdir.add_argument('-p', '--path', required=True, metavar='', help='base directory')
    p_mkdir.add_argument('-n', '--name', required=True, metavar='', help='folder name')

    args = parser.parse_args()
    commands[args.command].run(args)


if __name__ == '__main__':
    main()
