# DirTools - Command Line File Manager

DirTools is a command-line utility for managing files and directories with various features such as copying, moving, deleting, counting files, searching by regex, adding date prefixes, analyzing directory size, hashing files and directories, and finding duplicate files.

This project uses only Python standard libraries:
os, sys, shutil, argparse, hashlib, logging, etc.
No external dependencies required.

## Features

- Copy, move, and delete files.
- Count files in a directory.
- Find files by regex pattern.
- Add date prefix to filenames.
- Analyze directory content size.
- Calculate hash sums (SHA256 or MD5) for files or directories.
- Find duplicate files by hash.

## Examples

### For help run:
```bash
python manager.py -h
python manager.py <command> -h
```
### Copy file or folder
```bash
python manager.py copy -s /path/to/source/file.txt -d /path/to/destination/folder
```
### Count files
```bash
python manager.py count -p /path/to/directory
```
### Delete file or folder
```bash
python manager.py move -s /path/to/source/file.txt -d /path/to/destination/folder
```
### Find file
```bash
python manager.py find -p /path/to/directory -r ".*\.txt$"
```
### Move file or folder
```bash
python manager.py move -s /path/to/source/file.txt -d /path/to/destination/folder
```
### Add date to filename
```bash
python manager.py add_date -p /path/to/file.txt
```
### Analyse file or folder
```bash
python manager.py analyse -p /path/to/directory
```
### Check hashsum of file or folder (default sha256)
```bash
python manager.py hashsum -p /path/to/file_or_directory -m sha256
```
### Search for duplicates in folder and subfolders
```bash
python manager.py duplicates -p /path/to/directory
```
## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/dirtools.git
cd dirtools
