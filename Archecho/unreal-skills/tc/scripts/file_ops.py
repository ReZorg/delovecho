#!/usr/bin/env python3
"""
TC File Operations
==================
Copy, move, delete, and organize files using TC-style workflows.

Usage:
    python file_ops.py copy <source_pattern> <target_dir> [--flatten] [--dry-run]
    python file_ops.py move <source_pattern> <target_dir> [--flatten] [--dry-run]
    python file_ops.py delete <pattern> [--dry-run]
    python file_ops.py mkdir <path>
    python file_ops.py props <path>
    python file_ops.py tree <directory> [--depth N]

Examples:
    python file_ops.py copy "./src/*.pdf" ./backup/
    python file_ops.py move "./downloads/*.jpg" ./photos/ --dry-run
    python file_ops.py delete "./temp/*.log"
    python file_ops.py props ./report.pdf
    python file_ops.py tree /home/ubuntu --depth 2
"""

import os
import sys
import glob
import shutil
import argparse
from pathlib import Path
from datetime import datetime


def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:,.0f} {unit}" if unit == 'B' else f"{size:,.1f} {unit}"
        size /= 1024
    return f"{size:,.1f} TB"


def cmd_copy(pattern, target, flatten=False, dry_run=False):
    files = sorted(glob.glob(pattern, recursive=True))
    if not files:
        print("No files matched pattern.")
        return
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    for f in files:
        src = Path(f)
        if src.is_dir():
            continue
        dst = target / src.name if flatten else target / src.relative_to(Path(pattern).parent)
        print(f"  COPY  {src} → {dst}")
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    action = "would copy" if dry_run else "copied"
    print(f"\n✓ {len(files)} file(s) {action}.")


def cmd_move(pattern, target, flatten=False, dry_run=False):
    files = sorted(glob.glob(pattern, recursive=True))
    if not files:
        print("No files matched pattern.")
        return
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    for f in files:
        src = Path(f)
        if src.is_dir():
            continue
        dst = target / src.name if flatten else target / src.relative_to(Path(pattern).parent)
        print(f"  MOVE  {src} → {dst}")
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), dst)
    action = "would move" if dry_run else "moved"
    print(f"\n✓ {len(files)} file(s) {action}.")


def cmd_delete(pattern, dry_run=False):
    files = sorted(glob.glob(pattern, recursive=True))
    if not files:
        print("No files matched pattern.")
        return
    for f in files:
        p = Path(f)
        if p.is_dir():
            print(f"  DELETE DIR  {p}")
            if not dry_run:
                shutil.rmtree(p)
        else:
            print(f"  DELETE  {p}")
            if not dry_run:
                p.unlink()
    action = "would delete" if dry_run else "deleted"
    print(f"\n✓ {len(files)} item(s) {action}.")


def cmd_mkdir(path):
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created: {p}")


def cmd_props(path):
    p = Path(path)
    if not p.exists():
        print(f"Error: {path} not found")
        sys.exit(1)

    stat = p.stat()
    print(f"  Path:      {p.resolve()}")
    print(f"  Type:      {'Directory' if p.is_dir() else 'File'}")

    if p.is_file():
        print(f"  Size:      {format_size(stat.st_size)} ({stat.st_size:,} bytes)")
        print(f"  Extension: {p.suffix or '(none)'}")
    elif p.is_dir():
        total = sum(f.stat().st_size for f in p.rglob('*') if f.is_file())
        fcount = sum(1 for f in p.rglob('*') if f.is_file())
        dcount = sum(1 for f in p.rglob('*') if f.is_dir())
        print(f"  Size:      {format_size(total)} ({total:,} bytes)")
        print(f"  Contains:  {fcount} files, {dcount} directories")

    print(f"  Modified:  {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Accessed:  {datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Created:   {datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Mode:      {oct(stat.st_mode)[-3:]}")


def cmd_tree(directory, max_depth=3, _prefix='', _depth=0):
    if _depth == 0:
        print(f"  {directory}")
    p = Path(directory)
    entries = sorted(p.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
    entries = [e for e in entries if not e.name.startswith('.')]
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = '└── ' if is_last else '├── '
        if entry.is_dir():
            print(f"  {_prefix}{connector}{entry.name}/")
            if _depth < max_depth:
                extension = '    ' if is_last else '│   '
                cmd_tree(entry, max_depth, _prefix + extension, _depth + 1)
        else:
            size = format_size(entry.stat().st_size)
            print(f"  {_prefix}{connector}{entry.name} ({size})")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TC File Operations')
    sub = parser.add_subparsers(dest='command', required=True)

    p_copy = sub.add_parser('copy')
    p_copy.add_argument('pattern')
    p_copy.add_argument('target')
    p_copy.add_argument('--flatten', action='store_true')
    p_copy.add_argument('--dry-run', action='store_true')

    p_move = sub.add_parser('move')
    p_move.add_argument('pattern')
    p_move.add_argument('target')
    p_move.add_argument('--flatten', action='store_true')
    p_move.add_argument('--dry-run', action='store_true')

    p_del = sub.add_parser('delete')
    p_del.add_argument('pattern')
    p_del.add_argument('--dry-run', action='store_true')

    p_mkdir = sub.add_parser('mkdir')
    p_mkdir.add_argument('path')

    p_props = sub.add_parser('props')
    p_props.add_argument('path')

    p_tree = sub.add_parser('tree')
    p_tree.add_argument('directory')
    p_tree.add_argument('--depth', type=int, default=3)

    args = parser.parse_args()

    if args.command == 'copy':
        cmd_copy(args.pattern, args.target, args.flatten, args.dry_run)
    elif args.command == 'move':
        cmd_move(args.pattern, args.target, args.flatten, args.dry_run)
    elif args.command == 'delete':
        cmd_delete(args.pattern, args.dry_run)
    elif args.command == 'mkdir':
        cmd_mkdir(args.path)
    elif args.command == 'props':
        cmd_props(args.path)
    elif args.command == 'tree':
        cmd_tree(args.directory, args.depth)
