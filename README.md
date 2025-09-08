# DirTools - Command Line File Manager

DirTools is a command-line utility for managing files and directories with various features such as copying, moving, deleting, counting files, searching by regex, adding date prefixes, analyzing directory size, hashing files and directories, and finding duplicate files.

This project uses only Python standard libraries:
os, sys, shutil, argparse, hashlib, logging, etc.
No external dependencies required.

## Features

- **Copy** — copy files
- **Move** — move files and directories
- **Delete** — delete files and directories
- **Count** — count files in a directory (recursive)
- **Find** — find files by regular expression
- **Analyse** — compute total size and per-entry sizes
- **Add Date** — add creation date to file name(s)
- **Hashsum** — compute SHA256 or MD5
- **Duplicates** — find duplicate files (by hash)
- **Rename** — rename a file or directory (same parent)
- **New File** — create an empty file
- **New Folder** — create a directory

## Examples
### Run GUI:
```bash
python gui.py
```
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

### Create empty file
```bash
python manager.py mkfile -p path/to/dir -n new.txt
```

### Create a folder:
```bash
python manager.py mkdir -p path/to/dir -n newfolder
```

### Rename a file:
```bash
python manager.py rename -s path/to/file.txt -n newname.txt
```
## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/dirtools.git
cd dirtools
